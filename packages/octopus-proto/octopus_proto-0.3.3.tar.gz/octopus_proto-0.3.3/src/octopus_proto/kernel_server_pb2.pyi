import common_pb2 as _common_pb2
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class StartKernelRequest(_message.Message):
    __slots__ = ["kernel_name"]
    KERNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    kernel_name: str
    def __init__(self, kernel_name: _Optional[str] = ...) -> None: ...

class StartKernelResponse(_message.Message):
    __slots__ = ["code", "msg"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...

class StopKernelRequest(_message.Message):
    __slots__ = ["kernel_name"]
    KERNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    kernel_name: str
    def __init__(self, kernel_name: _Optional[str] = ...) -> None: ...

class StopKernelResponse(_message.Message):
    __slots__ = ["code", "msg"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...

class RestartKernelRequest(_message.Message):
    __slots__ = ["kernel_name"]
    KERNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    kernel_name: str
    def __init__(self, kernel_name: _Optional[str] = ...) -> None: ...

class RestartKernelResponse(_message.Message):
    __slots__ = ["code", "msg"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...

class ExecuteRequest(_message.Message):
    __slots__ = ["code", "kernel_name"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    KERNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    code: str
    kernel_name: str
    def __init__(self, code: _Optional[str] = ..., kernel_name: _Optional[str] = ...) -> None: ...

class ExecuteResponse(_message.Message):
    __slots__ = ["result", "stdout", "stderr", "traceback"]
    RESULT_FIELD_NUMBER: _ClassVar[int]
    STDOUT_FIELD_NUMBER: _ClassVar[int]
    STDERR_FIELD_NUMBER: _ClassVar[int]
    TRACEBACK_FIELD_NUMBER: _ClassVar[int]
    result: str
    stdout: str
    stderr: str
    traceback: str
    def __init__(self, result: _Optional[str] = ..., stdout: _Optional[str] = ..., stderr: _Optional[str] = ..., traceback: _Optional[str] = ...) -> None: ...

class GetStatusRequest(_message.Message):
    __slots__ = ["kernel_name"]
    KERNEL_NAME_FIELD_NUMBER: _ClassVar[int]
    kernel_name: str
    def __init__(self, kernel_name: _Optional[str] = ...) -> None: ...

class GetStatusResponse(_message.Message):
    __slots__ = ["is_alive", "code", "msg"]
    IS_ALIVE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    is_alive: bool
    code: int
    msg: str
    def __init__(self, is_alive: bool = ..., code: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...
