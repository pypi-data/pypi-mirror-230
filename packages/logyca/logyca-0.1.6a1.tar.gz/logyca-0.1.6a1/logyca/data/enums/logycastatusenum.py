from enum import IntEnum
from http import HTTPStatus

class LogycaStatusEnum(IntEnum):
        '''Description
        LOGYCA Custom States
        \n:param Ok: Not an error; returned on success
        \n:param Cancelled: The operation was cancelled, typically by the caller.
        \n:param Unknown: Unknown error. For example, this error may be returned when a Status value received from another address space belongs to an error space that is not known in this address space. Also errors raised by APIs that do not return enough error information may be converted to this error.
        \n:param Invalid_Argument: The client specified an invalid argument. Note that this differs from FAILED_PRECONDITION. INVALID_ARGUMENT indicates arguments that are problematic regardless of the state of the system (e.g., a malformed file name).
        \n:param DeadLine_Exceeded: The deadline expired before the operation could complete. For operations that change the state of the system, this error may be returned even if the operation has completed successfully. For example, a successful response from a server could have been delayed long
        \n:param Not_Found: Some requested entity (e.g., file or directory) was not found. Note to server developers: if a request is denied for an entire class of users, such as gradual feature rollout or undocumented whitelist, NOT_FOUND may be used. If a request is denied for some users within a class of users, such as user-based access control, PERMISSION_DENIED must be used.
        \n:param Already_Exists: The entity that a client attempted to create (e.g., file or directory) already exists.
        \n:param Permission_Denied: The caller does not have permission to execute the specified operation. PERMISSION_DENIED must not be used for rejections caused by exhausting some resource (use RESOURCE_EXHAUSTEDinstead for those errors). PERMISSION_DENIED must not be used if the caller can not be identified (use UNAUTHENTICATED instead for those errors). This error code does not imply the request is valid or the requested entity exists or satisfies other pre-conditions.
        \n:param Resource_Exhausted: Some resource has been exhausted, perhaps a per-user quota, or perhaps the entire file system is out of space.
        \n:param Failed_Condition: The operation was rejected because the system is not in a state required for the operation's execution. For example, the directory to be deleted is non-empty, an rmdir operation is applied to a non-directory, etc. Service implementors can use the following guidelines to decide between FAILED_PRECONDITION, ABORTED, and UNAVAILABLE: (a) Use UNAVAILABLE if the client can retry just the failing call. (b) Use ABORTED if the client should retry at a higher level (e.g., when a client-specified test-and-set fails, indicating the client should restart a read-modify-write sequence). (c) Use FAILED_PRECONDITION if the client should not retry until the system state has been explicitly fixed. E.g., if an "rmdir" fails because the directory is non-empty, FAILED_PRECONDITIONshould be returned since the client should not retry unless the files are deleted from the directory.
        \n:param Aborted: The operation was aborted, typically due to a concurrency issue such as a sequencer check failure or transaction abort. See the guidelines above for deciding between FAILED_PRECONDITION, ABORTED, and UNAVAILABLE.
        \n:param Out_Of_Range: The operation was attempted past the valid range. E.g., seeking or reading past end-of-file. Unlike INVALID_ARGUMENT, this error indicates a problem that may be fixed if the system state changes. For example, a 32-bit file system will generate INVALID_ARGUMENT if asked to read at an offset that is not in the range [0,2^32-1], but it will generate OUT_OF_RANGE if asked to read from an offset past the current file size. There is a fair bit of overlap between FAILED_PRECONDITION and OUT_OF_RANGE. We recommend using OUT_OF_RANGE (the more specific error) when it applies so that callers who are iterating through a space can easily look for an OUT_OF_RANGE error to detect when they are done.
        \n:param UnImplemented: The operation is not implemented or is not supported/enabled in this service.
        \n:param Internal: Internal errors. This means that some invariants expected by the underlying system have been broken. This error code is reserved for serious errors.
        \n:param UnAvailable: The service is currently unavailable. This is most likely a transient condition, which can be corrected by retrying with a backoff.
        \n:param DataLoss: Unrecoverable data loss or corruption.
        \n:param UnAuthenticated: The request does not have valid authentication credentials for the operation.
        \n:param Partial: Saved partial
        \n:param Created: Pending
        \n:param InProcess: Transaction in process.
        \n:return int: Integer according to variable meaning
        '''
        Ok = 0
        Cancelled = 1
        Unknown = 2
        Invalid_Argument = 3
        DeadLine_Exceeded = 4
        Not_Found = 5
        Already_Exists = 6
        Permission_Denied = 7
        Resource_Exhausted = 8
        Failed_Condition = 9
        Aborted = 10
        Out_Of_Range = 11
        UnImplemented = 12
        Internal = 13
        UnAvailable = 14
        DataLoss = 15
        UnAuthenticated = 16
        Partial = 20
        Created = 1001
        InProcess = 1002
        @property
        def mappingHttpStatusCode(self):
                if (self.value==LogycaStatusEnum.Ok):                   return HTTPStatus.OK
                if (self.value==LogycaStatusEnum.Cancelled):            return HTTPStatus.NOT_FOUND
                if (self.value==LogycaStatusEnum.Unknown):              return HTTPStatus.INTERNAL_SERVER_ERROR
                if (self.value==LogycaStatusEnum.Invalid_Argument):     return HTTPStatus.BAD_REQUEST
                if (self.value==LogycaStatusEnum.DeadLine_Exceeded):    return HTTPStatus.GATEWAY_TIMEOUT
                if (self.value==LogycaStatusEnum.Not_Found):            return HTTPStatus.NOT_FOUND
                if (self.value==LogycaStatusEnum.Already_Exists):       return HTTPStatus.CONFLICT
                if (self.value==LogycaStatusEnum.Permission_Denied):    return HTTPStatus.FORBIDDEN
                if (self.value==LogycaStatusEnum.Resource_Exhausted):   return HTTPStatus.TOO_MANY_REQUESTS
                if (self.value==LogycaStatusEnum.Failed_Condition):     return HTTPStatus.BAD_REQUEST
                if (self.value==LogycaStatusEnum.Aborted):              return HTTPStatus.CONFLICT
                if (self.value==LogycaStatusEnum.Out_Of_Range):         return HTTPStatus.BAD_REQUEST
                if (self.value==LogycaStatusEnum.UnImplemented):        return HTTPStatus.NOT_IMPLEMENTED
                if (self.value==LogycaStatusEnum.Internal):             return HTTPStatus.INTERNAL_SERVER_ERROR
                if (self.value==LogycaStatusEnum.UnAvailable):          return HTTPStatus.SERVICE_UNAVAILABLE
                if (self.value==LogycaStatusEnum.DataLoss):             return HTTPStatus.INTERNAL_SERVER_ERROR
                if (self.value==LogycaStatusEnum.UnAuthenticated):      return HTTPStatus.UNAUTHORIZED
                if (self.value==LogycaStatusEnum.Partial):              return HTTPStatus.OK
                if (self.value==LogycaStatusEnum.Created):              return HTTPStatus.OK
                if (self.value==LogycaStatusEnum.InProcess):            return HTTPStatus.OK
                return HTTPStatus.NOT_FOUND
