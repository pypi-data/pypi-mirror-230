# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from typing import List, Dict, Any, Union, Optional, TypeVar, Tuple
import os

import yaml

from azureml.dataprep.rslex import PyRsDataflow

from .engineapi.typedefinitions import (InspectorArguments, ExecuteInspectorCommonResponse, FieldType, InvalidLineHandling)
from .typeconversions import TypeConverter, FloatConverter, DateTimeConverter, StreamInfoConverter
from .dataprofile import DataProfile
from .inspector import BaseInspector
from ._dataframereader import RecordIterable, _execute, get_dataframe_reader
from ._rslex_executor import get_rslex_executor
from ._partitionsreader import PartitionIterable
from .dataflow import Dataflow, DataflowValidationError, FilePath, _is_datapath, _is_datapaths, PromoteHeadersMode, FileEncoding, DecimalMark, MismatchAsOption, MultiColumnSelection
from .datasources import process_uris, FileDataSource
from ._datastore_helper import file_datastores_to_uris
from ._loggerfactory import _LoggerFactory, track, trace
from .step import (Step, MultiColumnSelection, ColumnSelector)
from .tracing._open_telemetry_adapter import to_dprep_span_context
from .engineless_builders import ColumnTypesBuilder


logger = None
tracer = trace.get_tracer(__name__)

def get_logger():
    global logger
    if logger is not None:
        return logger

    logger = _LoggerFactory.get_logger("EnginelessDataflow")
    return logger


# single column, list of columns, pattern selector
ColumnSelector = Union[str, List[str], Dict[str, Union[str, bool]]]


class EnginelessBuilders:
    def __init__(self, dataflow: 'EnginelessDataflow'):
        self._dataflow = dataflow

    def set_column_types(self) -> ColumnTypesBuilder:
        """
        Constructs an instance of :class:`ColumnTypesBuilder`.
        """
        return ColumnTypesBuilder(self._dataflow)

class EnginelessDataflow(Dataflow):
    """
    Dataflow wrapper around a RSlex Dataflow YAML. Does not support the addition of any transformation steps
    Clex engine activity, etc.
    """

    def __init__(self, py_rs_dataflow):
        # fake attribute to trick AbstractDataset._should_auto_inference with AbstractDatset._load
        Dataflow.__init__(self, engine_api=None)
        self.meta = {'infer_column_types': 'False'}
        self.builders = EnginelessBuilders(self)

        if isinstance(py_rs_dataflow, str):
            from azureml.dataprep.api._rslex_executor import ensure_rslex_environment
            ensure_rslex_environment()
            # covers validation
            self._py_rs_dataflow = PyRsDataflow(py_rs_dataflow)
        elif isinstance(py_rs_dataflow, PyRsDataflow):
            self._py_rs_dataflow = py_rs_dataflow
        else:
            raise ValueError('Expect RSlex Dataflow YAML string or RSlex PyRsDataflow')

    def __repr__(self) -> str:
        return 'EnginelessDataflow:\n' + self._py_rs_dataflow.to_yaml_string()

    def _to_yaml_dict(self) -> dict:
        return yaml.safe_load(self._py_rs_dataflow.to_yaml_string())

    def _copy_and_update_metadata(self,
                                  action: str,
                                  source: str,
                                  **kwargs) -> 'EnginelessDataflow':
        # py_rs_dataflow is immutable so even if no changes occur & same instance is passed, nothing bad should happen
        new_py_rs_dataflow = self._py_rs_dataflow

        if not new_py_rs_dataflow.has_schema_property('metadata', 'activity'):
            new_py_rs_dataflow = new_py_rs_dataflow.set_schema_property('metadata', 'activity', action)

        if not new_py_rs_dataflow.has_schema_property('metadata', 'activityApp'):
            new_py_rs_dataflow = new_py_rs_dataflow.set_schema_property('metadata', 'activityApp', source)

        run_id = os.environ.get("AZUREML_RUN_ID", None)
        if run_id is not None:
            # keep this here so not to break existing reporting
            new_py_rs_dataflow = new_py_rs_dataflow.set_schema_property('metadata', 'runId', run_id)
            new_py_rs_dataflow = new_py_rs_dataflow.set_schema_property('metadata', 'run_id', run_id)

        for (k, v) in kwargs.items():
            if not new_py_rs_dataflow.has_schema_property('metadata', k):
                new_py_rs_dataflow = new_py_rs_dataflow.set_schema_property('metadata', k, v)

        return EnginelessDataflow(new_py_rs_dataflow)

    @track(get_logger)
    def read_parquet_file(self, include_path: bool = False) -> 'EnginelessDataflow':
        """
        Reads the Parquet files in the dataset.

        :param include_path_column: Indicates whether to include the path column in the output.
        :return: The modified Dataflow.
        """
        return self._add_transformation('read_parquet', {"include_path_column": include_path})

    @track(get_logger)
    def read_preppy(self, include_path: bool = False) -> 'EnginelessDataflow':
        """
        Reads the Preppy files in the dataset.

        :param include_path_column: Indicates whether to include the path column in the output.
        :return: The modified Dataflow.
        """
        return self._add_transformation('read_files', {"keep_existing_columns": include_path, "reader": "preppy"})

    @track(get_logger)
    def parse_delimited(self,
                        separator: str,
                        headers_mode: PromoteHeadersMode,
                        encoding: FileEncoding,
                        quoting: bool,
                        partition_size: Optional[int] = None,
                        empty_as_string: bool = False,
                        inlucde_path: bool = True) -> 'Dataflow':
        """
        Adds step to parse CSV data.

        :param separator: The separator to use to split columns.
        :param headers_mode: How to determine column headers.
        :param encoding: The encoding of the files being read.
        :param quoting: Whether to handle new line characters within quotes. This option will impact performance.
        :param skip_rows: How many rows to skip.
        :param skip_mode: The mode in which rows are skipped.
        :param comment: Character used to indicate a line is a comment instead of data in the files being read.
        :param partition_size: Desired partition size.
        :param empty_as_string: Whether to keep empty field values as empty strings. Default is read them as null.
        :return: A new Dataflow with Parse Delimited Step added.
        """
        self._raise_if_multi_char('separator', separator)
        self._validate_partition_size(partition_size)

        headers_mode_mapped = self._map_headers_mode(headers_mode)

        encoding_mapped = self._map_encoding(encoding)
        args = {'delimiter': separator,
                'header': headers_mode_mapped,
                'support_multi_line': quoting,
                'empty_as_string': empty_as_string,
                'encoding': encoding_mapped,
                'include_path_column': inlucde_path,
                'infer_column_types': False}
        if partition_size is not None:
            args['partition_size'] = partition_size
        return self._add_transformation('read_delimited',
                                        args=args)

    def parse_json_lines(self,
                         encoding: FileEncoding,
                         partition_size: Optional[int] = None,
                         invalid_lines: InvalidLineHandling = InvalidLineHandling.ERROR,
                         include_path: Optional[bool] = False) -> 'Dataflow':
        """
        Creates a new Dataflow with the operations required to read JSON lines files.

        :param invalid_lines: How to handle invalid JSON lines.
        :param encoding: The encoding of the files being read.
        :param partition_size: Desired partition size.
        :return: A new Dataflow with Read JSON line Step added.
        """
        invalid_lines = self._map_invalid_lines(invalid_lines)
        return self._add_transformation('read_json_lines',
                                        {"invalid_lines": invalid_lines,
                                         "encoding": self._map_encoding(encoding),
                                         "include_path_column": include_path})

    def _map_invalid_lines(self, invalid_lines):
        invalid_lines_mapped = ''
        if invalid_lines.value == InvalidLineHandling.ERROR.value:
            invalid_lines_mapped = 'error'
        elif invalid_lines.value == InvalidLineHandling.DROP.value:
            invalid_lines_mapped = 'drop'
        else:
            raise ValueError('Unsupported invalid lines handling: ' + str(invalid_lines))
        return invalid_lines_mapped

    def _map_encoding(self, encoding):
        encoding_mapped = ''
        if encoding.value == FileEncoding.UTF8.value:
            encoding_mapped = 'utf8'
        elif encoding.value == FileEncoding.ISO88591.value:
            encoding_mapped = 'iso88591'
        elif encoding.value == FileEncoding.LATIN1.value:
            encoding_mapped = 'latin1'
        elif encoding.value == FileEncoding.ASCII.value:
            encoding_mapped = 'ascii'
        elif encoding.value == FileEncoding.WINDOWS1252.value:
            encoding_mapped = 'windows1252'
        elif encoding.value == FileEncoding.UTF16.value:
            encoding_mapped = 'utf16'
        else:
            raise ValueError('Unsupported encoding: ' + str(encoding))
        return encoding_mapped

    def _map_headers_mode(self, headers_mode):
        headers_mode_mapped = ''
        if headers_mode.value == PromoteHeadersMode.ALLFILES.value:
            headers_mode_mapped='all_files_different_headers'
        elif headers_mode.value == PromoteHeadersMode.SAMEALLFILES.value:
            headers_mode_mapped='all_files_same_headers'
        elif headers_mode.value == PromoteHeadersMode.FIRSTFILE.value:
            headers_mode_mapped='from_first_file'
        elif headers_mode.value == PromoteHeadersMode.NONE.value:
            headers_mode_mapped='no_header'
        else:
            raise ValueError('Unsupported headers_mode: ' + str(headers_mode))
        return headers_mode_mapped

    def add_step(self,
                 step_type: str,
                 arguments: Dict[str, Any],
                 local_data: Dict[str, Any] = None) -> 'Dataflow':
        raise NotImplementedError

    def _add_transformation(self, step, args):
        return EnginelessDataflow(self._py_rs_dataflow.add_transformation(step, args, None))

    def _add_columns_from_partition_format(self,
                                column: str,
                                partition_format: str,
                                ignore_error: bool) -> 'EnginelessDataflow':
        """
        Add new columns to the dataset based on matching the partition format for provided column.

        :param partition_format: The partition format matching the column to create columns.
        :param ignore_error: Indicate whether or not to fail the execution if there is any error.
        :return: The modified Dataflow.
        """
        args = {'path_column': column, 'partition_format': partition_format, 'ignore_error': ignore_error}
        return self._add_transformation('extract_columns_from_partition_format', args)

    def take(self, count: int) -> 'EnginelessDataflow':
        """
        Takes the specified count of records.

        :param count: The number of records to take.
        :return: The modified Dataflow.
        """
        if not (isinstance(count, int) and count > 0):
            raise ValueError('count must be a positive integer')
        return self._add_transformation('take', count)


    def drop_columns(self, columns: Union[str, List[str]]) -> 'EnginelessDataflow':
        """
        Drops the specified columns.

        :param columns: The columns to drop.
        :return: The modified Dataflow.
        """
        if not isinstance(columns, list) and not isinstance(columns, str):
            get_logger().error(f'Column selector of type {columns.__class__} was used.')
            raise ValueError('columns must be a list of strings or a string. Column selector is not supported yet.')
        return self._add_transformation('drop_columns', columns)

    def keep_columns(self, columns: Union[str, List[str]]) -> 'EnginelessDataflow':
        """
        Keeps the specified columns.

        :param columns: The columns to keep.
        :return: The modified Dataflow.
        """
        if not isinstance(columns, list) and not isinstance(columns, str):
            get_logger().error(f'Column selector of type {columns.__class__} was used.')
            raise ValueError('columns must be a list of strings or a string. Column selector is not supported yet.')
        return self._add_transformation('keep_columns', columns)

    def promote_headers(self) -> 'Dataflow':
        """
        Sets the first record in the dataset as headers, replacing any existing ones.
        :return: The modified Dataflow.
        """
        raise NotImplementedError

    def convert_unix_timestamp_to_datetime(self,
                                           columns: MultiColumnSelection,
                                           use_seconds: bool = False) -> 'Dataflow':
        """
        Converts the specified column to DateTime values by treating the existing value as a Unix timestamp.

        :param columns: The source columns.
        :param use_seconds: Whether to use seconds as the resolution. Milliseconds are used if false.
        :return: The modified Dataflow.
        """
        raise NotImplementedError

    TypeConversionInfo = TypeVar('TypeConversionInfo',
                                 FieldType,
                                 TypeConverter,
                                 Tuple[FieldType, List[str], Tuple[FieldType, str]])

    def set_column_types(self, type_conversions: Dict[str, TypeConversionInfo]) -> 'Dataflow':
        """
        Converts values in specified columns to the corresponding data types.

        .. remarks::

            The values in the type_conversions dictionary could be of several types:

            * :class:`azureml.dataprep.FieldType`
            * :class:`azureml.dataprep.TypeConverter`
            * Tuple of DATE (:class:`azureml.dataprep.FieldType`) and List of format strings (single format string is also supported)

            .. code-block:: python

                import azureml.dataprep as dprep

                dataflow = dprep.read_csv(path='./some/path')
                dataflow = dataflow.set_column_types({'MyNumericColumn': dprep.FieldType.DECIMAL,
                                                   'MyBoolColumn': dprep.FieldType.BOOLEAN,
                                                   'MyAutodetectDateColumn': dprep.FieldType.DATE,
                                                   'MyDateColumnWithFormat': (dprep.FieldType.DATE, ['%m-%d-%Y']),
                                                   'MyOtherDateColumn': dprep.DateTimeConverter(['%d-%m-%Y'])})

            .. note::

                If you choose to convert a column to DATE and do not provide \
                **format(s)** to use, DataPrep will attempt to infer a format to use by pulling on the data. \
                If a format could be inferred from the data, it will be used to convert values in the corresponding
                column. However, if a format could not be inferred, this step will fail and you will need to either \
                provide the format to use or use the interactive builder \
                :class:`azureml.dataprep.api.builders.ColumnTypesBuilder` by calling \
                'dataflow.builders.set_column_types()'

        :param type_conversions: A dictionary where key is column name and value is either
            :class:`azureml.dataprep.FieldType` or :class:`azureml.dataprep.TypeConverter` or a Tuple of
            DATE (:class:`azureml.dataprep.FieldType`) and List of format strings

        :return: The modified Dataflow.
        """
        return self._set_column_types(list((k, v) for k, v in type_conversions.items()))

    def _set_column_types(self, type_conversions: List[Tuple[ColumnSelector, TypeConversionInfo]]) -> 'Dataflow':
        def _get_validity_and_type_arguments(converter: TypeConverter) -> Tuple[bool, Optional[Dict[str, Any]]]:
            if isinstance(converter, DateTimeConverter):
                return (converter.formats is not None and len(converter.formats) > 0,  {'formats': converter.formats})
            if isinstance(converter, TypeConverter) and converter.data_type.value == FieldType.DATE.value:
                return (False, None)
            if isinstance(converter, FloatConverter):
                return (True, None)
            if isinstance(converter, StreamInfoConverter) and converter.workspace is not None:
                return (True, {
                    'subscription': converter.workspace.subscription_id,
                    'resource_group': converter.workspace.resource_group,
                    'workspace_name': converter.workspace.name,
                    'escaped': converter.escaped
                })
            return (True, None)

        normalized_type_conversions : Tuple[ColumnSelector, TypeConverter] = []
        columns_to_tranform_decimal_marks: List[str] = []
        # normalize type_conversion argument
        for col, conv_info in type_conversions:
            if not isinstance(conv_info, TypeConverter):
                # if a 2 value tuple and first value is FieldType.Date
                if isinstance(conv_info, tuple) and conv_info[0] == FieldType.DATE and len(conv_info) == 2:
                    converter = DateTimeConverter(conv_info[1] if isinstance(conv_info[1], List)
                                                              else [conv_info[1]])
                elif isinstance(conv_info, tuple) and conv_info[0] == FieldType.DECIMAL and len(conv_info) == 2:
                    converter = FloatConverter(conv_info[1])
                    if converter.decimal_mark.value == DecimalMark.COMMA.value:
                        columns_to_tranform_decimal_marks.append(col)
                elif isinstance(conv_info, tuple) and conv_info[0] == FieldType.STREAM and len(conv_info) == 2:
                    converter = StreamInfoConverter(conv_info[1])
                elif conv_info in FieldType and conv_info.value < FieldType.UNKNOWN.value:
                    converter = TypeConverter(conv_info)
                else:
                    raise ValueError('Unexpected conversion info for column: ' + col)
            else:
                if isinstance(conv_info, FloatConverter) and conv_info.decimal_mark == ',':
                    columns_to_tranform_decimal_marks.append(col)
                converter = conv_info

            normalized_type_conversions.append((col, converter))

        # construct transformation arguments
        def fieldType_to_string(field_type: FieldType) -> str:
            if field_type == FieldType.DATE:
                return 'datetime'
            if field_type == FieldType.DECIMAL:
                return 'float'
            if field_type == FieldType.BOOLEAN:
                return 'boolean'
            if field_type == FieldType.INTEGER:
                return 'int'
            if field_type == FieldType.STRING:
                return 'string'
            if field_type == FieldType.STREAM:
                return 'stream_info'

            raise ValueError('Unexpected field type: ' + str(field_type))

        columns_needing_inference = []
        arguments = []
        for col, converter in normalized_type_conversions:
            col_conversion : Dict[str, Any] = {'columns': col}
            is_valid, args = _get_validity_and_type_arguments(converter)
            if not is_valid:
                columns_needing_inference.append(col)
                continue
            type = fieldType_to_string(converter.data_type)
            col_conversion['column_type'] = { type: args } if args is not None else type
            arguments.append(col_conversion)

        if len(columns_needing_inference) > 0:
            just_columns_to_infer = self.keep_columns(columns_needing_inference)
            ex = get_rslex_executor()
            error = None
            inference_result = None
            try:
                with tracer.start_as_current_span('EnginelessDataflow.set_columns_types.infer_missing_date_formats', trace.get_current_span()) as span:
                    inference_result = ex.infer_types(just_columns_to_infer._py_rs_dataflow.to_yaml_string(), 200, to_dprep_span_context(span.get_context()).span_id)
            except Exception as e:
                error = e
                raise
            finally:
                builder = {
                    "activity" : 'set_columns_types.infer_missing_date_formats',
                    "clex_forced" : False,
                    "fallback_allowed" : False }

                if error is not None:
                    builder['rslex_failed'] = True
                    builder["rslex_error"] = str(error)
                else:
                    builder["execution_succeeded"] = True
                    builder["inference_col_count"] = len(inference_result)
                try:
                    _LoggerFactory.trace(logger, "dataflow_execution", builder)
                except Exception:
                    pass

            for col, type_inference in inference_result.items():
                col_conversion : Dict[str, Any] = {'columns': col}
                if type_inference.field_type == 'datetime':
                    if len(type_inference.ambiguous_formats) > 0:
                        raise ValueError(f'Ambiguous date formats for column: "{col}", matching formats: {type_inference.ambiguous_formats}. Please specify the format explicitly.')
                    if len(type_inference.datetime_formats) == 0:
                        # no date formats from inference means that the column was already of date type
                        continue
                    col_conversion['column_type'] = { 'datetime': {'formats': type_inference.datetime_formats}}
                else:
                    raise ValueError(f'Unexpected field type for {col}, provided {normalized_type_conversions[col]} but got {type_inference.field_type} during inference. '
                                     'Make sure the provided type has all required arguments so that inference could be avoided.')
                arguments.append(col_conversion)

        # if columns_to_tranform_decimal_marks > 0 then also arguments > 0
        transformed = self._with_columns_to_transform_decimal_marks(columns_to_tranform_decimal_marks)
        return transformed._add_transformation('convert_column_types', arguments) if len(arguments) > 0 else self

    def _with_columns_to_transform_decimal_marks(self, columns: ColumnSelector):
        if len(columns) > 0:
            return self._add_transformation('transform_columns',
                                            {'language': 'Native',
                                             'transformations': [{
                                                 'columns': columns,
                                                 'function_source': '{"r":["Function",[[],{"r":[]},{"r":["Invoke",[{"r":["Identifier","CleanStringNumberTransform"]},[".",false,false]]]}]]}'}]})
        return self

    def _with_partition_size(self, partition_size: int) -> 'EnginelessDataflow':
        if not (isinstance(partition_size, int) and partition_size > 0):
            raise ValueError('expect partition_size to be positive int')

        rs_dataflow_yaml = self._to_yaml_dict()
        transformations = rs_dataflow_yaml['transformations'][0]
        # invalid parition size test, json lines paritiont size test
        if 'read_delimited' in transformations:
            transformation = transformations['read_delimited']
        elif 'read_json_lines' in transformations:
            transformation = transformations['read_json_lines']
        else:
            raise ValueError('Can only update partition_size if `read_delimited` or `read_json_lines` '
                             'are in the EnglinelessDataflow')

        transformation['partition_size'] = partition_size
        rs_dataflow_str = yaml.safe_dump(rs_dataflow_yaml)
        return EnginelessDataflow(rs_dataflow_str)

    def _get_steps(self) -> List[Step]:
        raise NotImplementedError

    def execute_inspector(self, inspector: BaseInspector) -> ExecuteInspectorCommonResponse:
        raise NotImplementedError

    def _execute_inspector(self, inspector: Union[str, InspectorArguments]) -> ExecuteInspectorCommonResponse:
        raise NotImplementedError

    def execute_inspectors(self, inspectors: List[BaseInspector]) \
            -> Dict[InspectorArguments, ExecuteInspectorCommonResponse]:
        raise NotImplementedError

    def _execute_inspectors(self, inspectors: Union[str, List[InspectorArguments]]) \
            -> Dict[InspectorArguments, ExecuteInspectorCommonResponse]:
        raise NotImplementedError

    def _get_profile(self,
                     include_stype_counts: bool = False,
                     number_of_histogram_bins: int = 10,
                     include_average_spaces_count: bool = False,
                     include_string_lengths: bool = False) -> DataProfile:
        raise NotImplementedError

    @track(get_logger)
    def has_invalid_source(self, return_validation_error=False):
        raise NotImplementedError

    @track(get_logger)
    def get_partition_count(self) -> int:
        from azureml.dataprep.api._dataframereader import get_partition_count_with_rslex
        return get_partition_count_with_rslex(self._py_rs_dataflow.to_yaml_string())

    @track(get_logger)
    def run_local(self) -> None:
        """
        Runs the current Dataflow using the local execution runtime.
        """
        parent = trace.get_current_span()
        with tracer.start_as_current_span('Dataflow.run_local', parent) as span:
            _execute('Dataflow.run_local',
                     self._py_rs_dataflow.to_yaml_string(),
                     force_clex=False,
                     allow_fallback_to_clex=False,
                     span_context=to_dprep_span_context(span.get_context()))

    @track(get_logger)
    def run_spark(self) -> None:
        raise NotImplementedError

    @track(get_logger)
    def verify_has_data(self):
        """
        Verifies that this Dataflow would produce records if executed. An exception will be thrown otherwise.
        """
        with tracer.start_as_current_span('EnginelessDataflow.verify_has_data', trace.get_current_span()):
              if len(self.take(1)._to_pyrecords()) == 0:
                raise DataflowValidationError("The Dataflow produced no records.")

    @track(get_logger)
    def _to_pyrecords(self):
        ex = get_rslex_executor()
        error = None
        record_count = None
        try:
            with tracer.start_as_current_span('EnginelessDataflow._to_pyrecords', trace.get_current_span()) as span:
                records = ex.to_pyrecords(self._py_rs_dataflow.to_yaml_string(), to_dprep_span_context(span.get_context()).span_id)
                record_count = len(records)
                return records
        except Exception as e:
            error = e
            raise
        finally:
            builder = {
                "activity" : '_to_pyrecords',
                "clex_forced" : False,
                "fallback_allowed" : False }

            if error is not None:
                builder['rslex_failed'] = True
                builder["rslex_error"] = str(error)
            else:
                builder["execution_succeeded"] = True
                builder["record_count"] = record_count
            try:
                _LoggerFactory.trace(logger, "dataflow_execution", builder)
            except Exception:
                pass

    def select_partitions(self, partition_indices: List[int]) -> 'EnginelessDataflow':
        """
        Selects specific partitions from the data, dropping the rest.

        :return: The modified Dataflow.
        """
        return self._add_transformation('select_partitions', partition_indices)

    def _partition_to_pandas_dataframe(self,
                                       i: int,
                                       extended_types: bool,
                                       nulls_as_nan: bool,
                                       on_error: str,
                                       out_of_range_datetime: str) -> 'pandas.DataFrame':
        return self.select_partitions([i]).to_pandas_dataframe(extended_types=extended_types,
                                                               nulls_as_nan=nulls_as_nan,
                                                               on_error=on_error,
                                                               out_of_range_datetime=out_of_range_datetime)

    @track(get_logger)
    def to_dask_dataframe(self,
                          sample_size: int = 10000,
                          dtypes: dict = None,
                          extended_types: bool = False,
                          nulls_as_nan: bool = True,
                          on_error: str = 'null',
                          out_of_range_datetime: str = 'null'):
        """
        Returns a Dask DataFrame that can lazily read the data in the Dataflow.

        .. remarks::
            Dask DataFrames allow for parallel and lazy processing of data by splitting the data into multiple
                partitions. Because Dask DataFrames don't actually read any data until a computation is requested,
                it is necessary to determine what the schema and types of the data will be ahead of time. This is done
                by reading a specific number of records from the Dataflow (specified by the `sample_size` parameter).
                However, it is possible for these initial records to have incomplete information. In those cases, it is
                possible to explicitly specify the expected columns and their types by providing a dict of the shape
                `{column_name: dtype}` in the `dtypes` parameter.

        :param sample_size: The number of records to read to determine schema and types.
        :param dtypes: An optional dict specifying the expected columns and their dtypes.
            `sample_size` is ignored if this is provided.
        :param extended_types: Whether to keep extended DataPrep types such as DataPrepError in the DataFrame. If False,
            these values will be replaced with None.
        :param nulls_as_nan: Whether to interpret nulls (or missing values) in number typed columns as NaN. This is
            done by pandas for performance reasons; it can result in a loss of fidelity in the data.
        :param on_error: How to handle any error values in the Dataflow, such as those produced by an error while parsing values.
            Valid values are 'null' which replaces them with null; and 'fail' which will result in an exception.
        :param out_of_range_datetime: How to handle date-time values that are outside the range supported by Pandas.
            Valid values are 'null' which replaces them with null; and 'fail' which will result in an exception.
        :return: A Dask DataFrame.
        """
        from ._dask_helper import have_dask, DaskImportError
        from ._pandas_helper import have_pandas

        if not (have_dask() and have_pandas()):
            raise DaskImportError()

        import dask.dataframe as dd
        from dask.delayed import delayed
        import pandas

        # TODO defaulting to non-optimized dask, optimized dask in future PR (nathof)
        partition_count = self.get_partition_count()

        if partition_count <= 0:
            return dd.from_pandas(pandas.DataFrame(), chunksize=1)

        dtypes = dtypes or {col: str(t) for (col, t) in self.take(sample_size).to_pandas_dataframe().dtypes.items()}
        delayed_functions = [delayed(self._partition_to_pandas_dataframe)(i, extended_types, nulls_as_nan, on_error, out_of_range_datetime) for i in range(0, partition_count)]
        return dd.from_delayed(delayed_functions, meta=dtypes)

    @track(get_logger)
    def to_spark_dataframe(self, spark_session: 'pyspark.sql.SparkSession' = None) -> 'pyspark.sql.DataFrame':
        raise NotImplementedError

    @track(get_logger)
    def to_record_iterator(self) -> RecordIterable:
        raise NotImplementedError

    @track(get_logger)
    def to_partition_iterator(self, on_error: str = 'null') -> PartitionIterable:
        raise NotImplementedError

    # noinspection PyUnresolvedReferences
    @track(get_logger)
    def to_pandas_dataframe(self,
                            extended_types: bool = False,
                            nulls_as_nan: bool = True,
                            on_error: str = 'null',
                            out_of_range_datetime: str = 'null') -> 'pandas.DataFrame':
        """
        Pulls all of the data and returns it as a Pandas `Link pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.

        .. remarks::

            This method will load all the data returned by this Dataflow into memory.

            Since Dataflows do not require a fixed, tabular schema but Pandas DataFrames do, an implicit tabularization
                step will be executed as part of this action. The resulting schema will be the union of the schemas of all
                records produced by this Dataflow.

        :param extended_types: Whether to keep extended DataPrep types such as DataPrepError in the DataFrame. If False,
            these values will be replaced with None.
        :param nulls_as_nan: Whether to interpret nulls (or missing values) in number typed columns as NaN. This is
            done by pandas for performance reasons; it can result in a loss of fidelity in the data.
        :param on_error: How to handle any error values in the Dataflow, such as those produced by an error while parsing values.
            Valid values are 'null' which replaces them with null; and 'fail' which will result in an exception.
        :param out_of_range_datetime: How to handle date-time values that are outside the range supported by Pandas.
            Valid values are 'null' which replaces them with null; and 'fail' which will result in an exception.
        :return: A Pandas `Link pandas.DataFrame <https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.html>`_.
        """
        with tracer.start_as_current_span('Dataflow.to_pandas_dataframe', trace.get_current_span()) as span:
            span_context = to_dprep_span_context(span.get_context())
            return get_dataframe_reader().to_pandas_dataframe(self._py_rs_dataflow.to_yaml_string(),
                                                              extended_types,
                                                              nulls_as_nan,
                                                              on_error,
                                                              out_of_range_datetime,
                                                              span_context)

    def to_json(self):
        import json
        dflow_obj = {'blocks':[], 'meta': {'RsDataflow': self._py_rs_dataflow.to_yaml_string()}}
        return json.dumps(dflow_obj)

    @staticmethod
    def _paths_to_uris(paths: FilePath, force_file: bool = False) -> List[Dict[str, str]]:
        # handle case of datastore paths
        if _is_datapath(paths):
            return [{'pattern' : uri} for uri in file_datastores_to_uris([paths])]
        if _is_datapaths(paths):
            return [{'pattern' : uri} for uri in file_datastores_to_uris(paths)]

        # handle FileDataSource by extracting path for future processing
        if isinstance(paths, FileDataSource):
            paths = [resource_detail.to_pod()['path'] for resource_detail in paths.underlying_value.resource_details]
        if not isinstance(paths, list):
            paths = [paths]
        # handle all other uris
        return [{'pattern' if can_search and not force_file else 'file' : uri} for can_search, uri in process_uris(paths)]

    def to_datetime(self,
                    columns: MultiColumnSelection,
                    date_time_formats: Optional[List[str]] = None,
                    date_constant: Optional[str] = None) -> 'Dataflow':
        """
        Converts the values in the specified columns to DateTimes.

        :param columns: The source columns.
        :param date_time_formats: The formats to use to parse the values. If none are provided, a partial scan of the
            data will be performed to derive one.
        :param date_constant: If the column contains only time values, a date to apply to the resulting DateTime.
        :return: The modified Dataflow.
        """
        columns = _column_selection_to_py_rs_dataflow_selector(columns)
        if date_time_formats is None or len(date_time_formats) == 0:
            return self._set_column_types([(columns, FieldType.DATE)])

        return self._add_transformation('convert_column_types', [{
                                               'columns': columns,
                                               'column_type': {
                                                   'formats': date_time_formats,
                                                   'date_constant': date_constant
                                                   }}])

    def to_number(self,
                  columns: MultiColumnSelection,
                  decimal_point: DecimalMark = DecimalMark.DOT) -> 'Dataflow':
        """
        Converts the values in the specified columns to floating point numbers.

        :param columns: The source columns.
        :param decimal_point: The symbol to use as the decimal mark.
        :return: The modified Dataflow.
        """
        columns = _column_selection_to_py_rs_dataflow_selector(columns)
        if decimal_point == DecimalMark.DOT:
            transformed = self
        else: # decimal_point == DecimalMark.COMMA:
            transformed = self._with_columns_to_transform_decimal_marks(columns)

        return transformed._add_transformation('convert_column_types', [{
                                               'columns': columns,
                                               'column_type': 'float'
                                               }])

    def to_bool(self,
                columns: MultiColumnSelection,
                true_values: List[str],
                false_values: List[str],
                mismatch_as: MismatchAsOption = MismatchAsOption.ASERROR) -> 'Dataflow':
        """
        Converts the values in the specified columns to booleans.

        :param columns: The source columns.
        :param true_values: The values to treat as true.
        :param false_values: The values to treat as false.
        :param mismatch_as: How to treat values that don't match the values in the true or false values lists.
        :return: The modified Dataflow.
        """
        if mismatch_as == MismatchAsOption.ASERROR:
            mismatch_as = 'error'
        elif mismatch_as == MismatchAsOption.ASFALSE:
            mismatch_as = 'false'
        else:
            mismatch_as = 'true'

        return self._add_transformation('convert_column_types', [{
                                        'columns': _column_selection_to_py_rs_dataflow_selector(columns),
                                        'column_type': {
                                            'boolean':{
                                                'true_values': true_values,
                                                'false_values': false_values,
                                                'mismatch_as': mismatch_as
                                                }}}])

    def to_string(self,
                  columns: MultiColumnSelection) -> 'Dataflow':
        """
        Converts the values in the specified columns to strings.

        :param columns: The source columns.
        :return: The modified Dataflow.
        """
        return self._add_transformation('convert_column_types', [{
                                        'columns': _column_selection_to_py_rs_dataflow_selector(columns),
                                        'column_type': 'string'
                                    }])

    def to_long(self,
                columns: MultiColumnSelection) -> 'Dataflow':
        """
        Converts the values in the specified columns to 64 bit integers.

        :param columns: The source columns.
        :return: The modified Dataflow.
        """
        return self._add_transformation('convert_column_types', [{
                                        'columns': _column_selection_to_py_rs_dataflow_selector(columns),
                                        'column_type': 'int'
                                    }])

    @staticmethod
    def from_paths(paths: FilePath, force_file: bool = False) -> 'EnginelessDataflow':
        uri_paths = EnginelessDataflow._paths_to_uris(paths, force_file)
        rs_df = PyRsDataflow.from_paths(uri_paths)
        return EnginelessDataflow(rs_df)

    @staticmethod
    def from_query_source(handler, query, handler_arguments) -> 'EnginelessDataflow':
        arguments = {'handler': handler, 'query': query, 'handler_arguments': handler_arguments}
        rs_df = PyRsDataflow.from_query_source(arguments)
        return EnginelessDataflow(rs_df)

def _column_selection_to_py_rs_dataflow_selector(columns) -> ColumnSelector:
    if isinstance(columns, str):
        return columns
    if isinstance(columns, (list, set)):
        if not all(isinstance(column_selection, str) for column_selection in columns):
            raise ValueError('Unsupported value for column selection.')
        return list(columns)
    if isinstance(columns , ColumnSelector):
        # RSlex any match in the string
        if columns.match_whole_word:
            pattern = columns.term
            if columns.ignore_case:
                pattern = '(?i)' + pattern
            pattern = '^' + pattern + '$'
            return {'pattern': pattern,
                    'ignore_case': False}
        return {'pattern': columns.term,
                'invert': columns.invert,
                'ignore_case': columns.ignore_case}

    raise ValueError('Unsupported value for column selection.')
