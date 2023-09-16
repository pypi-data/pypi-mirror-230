# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from azureml.dataprep import DataPrepException, UserErrorException


_DATAPREP_EXECEPTION_USER_ERROR_CODES = ('ScriptExecution.StreamAccess.Validation',
                                         'ScriptExecution.StreamAccess.NotFound',
                                         'ScriptExecution.StreamAccess.Authentication',
                                         'ScriptExecution.StreamAccess.Throttling',
                                         'ScriptExecution.StreamAccess.EOF',
                                         'ScriptExecution.DatabaseQuery',
                                         'ScriptExecution.Database.TypeMismatch',
                                         'ScriptExecution.Validation',
                                         'ScriptExecution.DatabaseConnection.Authentication',
                                         'ScriptExecution.DatabaseConnection',
                                         'ScriptExecution.Database.TypeMismatch',
                                         'ScriptExecution.WriteStreams.NotFound',
                                         'ScriptExecution.WriteStreams.Authentication',
                                         'ScriptExecution.WriteStreams.Validation',
                                         'ScriptExecution.WriteStreams.AlreadyExists',
                                         'ScriptExecution.WriteStreams.Throttling',
                                         'ScriptExecution.Transformation.Validation')


_RSLEX_USER_ERROR_VALUES = ('Microsoft.DPrep.ErrorValues.SourceFileNotFound',
                            'Microsoft.DPrep.ErrorValues.SourceFilePermissionDenied',
                            'Microsoft.DPrep.ErrorValues.InvalidArgument',
                            'Microsoft.DPrep.ErrorValues.ValueWrongKind',
                            'Microsoft.DPrep.ErrorValues.SourcePermissionDenied',
                            'Microsoft.DPrep.ErrorValues.DestinationPermissionDenied',
                            'Microsoft.DPrep.ErrorValues.DestinationDiskFull',
                            'Microsoft.DPrep.ErrorValues.FileSizeChangedWhileDownloading',
                            'Microsoft.DPrep.ErrorValues.StreamInfoInvalidPath',
                            'Microsoft.DPrep.ErrorValues.NoManagedIdentity',
                            'Microsoft.DPrep.ErrorValues.NoOboEndpoint',
                            'Microsoft.DPrep.ErrorValues.StreamInfoRequired',
                            'Microsoft.DPrep.ErrorValues.ParseJsonFailure')


_RSLEX_USER_ERROR_MSGS = ('InvalidUriScheme',
                          'StreamError(NotFound)',
                          'DataAccessError(NotFound)',
                          'No such host is known',
                          'No identity was found on compute',
                          'Make sure uri is correct',
                          'Invalid JSON in log record',
                          'Invalid table version',
                          'stream did not contain valid UTF-8',
                          'Got unexpected error: invalid data. Kind(InvalidData)',
                          'Only one of version or timestamp can be specified but not both.',
                          'The requested stream was not found. Please make sure the request uri is correct.',
                          'stream did not contain valid UTF-8',
                          'Authentication failed when trying to access the stream',
                          'Unable to find any delta table metadata',
                          'Range requested from the service is invalid for current stream.',
                          'Invalid Parquet file.',
                          'DataAccessError(PermissionDenied)',
                          'OutputError(NotEmpty)',
                          'DestinationError(NotEmpty)',
                          'invalid azureml datastore uri format',
                          'does not have automatic support')


def _reclassify_rslex_error(err):
    """
    Reclassifies some errors from outside of MLTable into UserErrorExceptions or RuntimeErrors.
    """
    if isinstance(err, (UserErrorException, RuntimeError)):  # just a safety net
        raise err

    err_msg = err.args[0]
    # first check remaps errors from RSlex to UserErrorExceptions in following ways:
    # - is a DataPrepException whose error_code attribute is in _DATAPREP_EXECEPTION_USER_ERROR_CODES or whose message
    #   attribute contains am error value in _RSLEX_USER_ERROR_VALUES
    # - error message contains any element in _RSLEX_USER_ERROR_MSGS
    if ((isinstance(err, DataPrepException) or hasattr(err, 'error_code'))
        and err.error_code in _DATAPREP_EXECEPTION_USER_ERROR_CODES) \
            or any(user_err_msg in err_msg for user_err_msg in _RSLEX_USER_ERROR_MSGS) \
            or (isinstance(err, DataPrepException)
                and any(user_error_value in err.message for user_error_value in _RSLEX_USER_ERROR_VALUES)):
        raise UserErrorException(err)
    if 'Python expression parse error' in err_msg:
        raise UserErrorException(f'Not a valid python expression in filter. {err_msg}')
    if 'ExecutionError(StreamError(PermissionDenied' in err_msg:
        raise UserErrorException(
            f'Getting permission error please make sure proper access is configured on storage: {err_msg}')
    raise RuntimeError(err_msg)


def _wrap_rslex_function_call(func):
    """
    Maps Exceptions from the calling RSlex function to a UserErrorException or RuntimeError based on error context.
    """
    try:
        return func()
    except Exception as e:
        _reclassify_rslex_error(e)
