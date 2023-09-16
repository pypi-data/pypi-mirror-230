import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class SendTaskRequest(_message.Message):
    __slots__ = ["input_files", "task"]
    INPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    TASK_FIELD_NUMBER: _ClassVar[int]
    input_files: _containers.RepeatedScalarFieldContainer[str]
    task: str
    def __init__(self, input_files: _Optional[_Iterable[str]] = ..., task: _Optional[str] = ...) -> None: ...

class OnAgentAction(_message.Message):
    __slots__ = ["input", "tool"]
    INPUT_FIELD_NUMBER: _ClassVar[int]
    TOOL_FIELD_NUMBER: _ClassVar[int]
    input: str
    tool: str
    def __init__(self, input: _Optional[str] = ..., tool: _Optional[str] = ...) -> None: ...

class OnAgentActionEnd(_message.Message):
    __slots__ = ["output", "output_files"]
    OUTPUT_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FILES_FIELD_NUMBER: _ClassVar[int]
    output: str
    output_files: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, output: _Optional[str] = ..., output_files: _Optional[_Iterable[str]] = ...) -> None: ...

class FinalRespond(_message.Message):
    __slots__ = ["answer"]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    answer: str
    def __init__(self, answer: _Optional[str] = ...) -> None: ...

class TaskRespond(_message.Message):
    __slots__ = ["token_usage", "iteration", "model_name", "on_agent_action", "on_agent_action_end", "final_respond"]
    TOKEN_USAGE_FIELD_NUMBER: _ClassVar[int]
    ITERATION_FIELD_NUMBER: _ClassVar[int]
    MODEL_NAME_FIELD_NUMBER: _ClassVar[int]
    ON_AGENT_ACTION_FIELD_NUMBER: _ClassVar[int]
    ON_AGENT_ACTION_END_FIELD_NUMBER: _ClassVar[int]
    FINAL_RESPOND_FIELD_NUMBER: _ClassVar[int]
    token_usage: int
    iteration: int
    model_name: str
    on_agent_action: OnAgentAction
    on_agent_action_end: OnAgentActionEnd
    final_respond: FinalRespond
    def __init__(self, token_usage: _Optional[int] = ..., iteration: _Optional[int] = ..., model_name: _Optional[str] = ..., on_agent_action: _Optional[_Union[OnAgentAction, _Mapping]] = ..., on_agent_action_end: _Optional[_Union[OnAgentActionEnd, _Mapping]] = ..., final_respond: _Optional[_Union[FinalRespond, _Mapping]] = ...) -> None: ...

class AddKernelRequest(_message.Message):
    __slots__ = ["endpoint", "key"]
    ENDPOINT_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    endpoint: str
    key: str
    def __init__(self, endpoint: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class AddKernelResponse(_message.Message):
    __slots__ = ["code", "msg"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...

class AssembleAppRequest(_message.Message):
    __slots__ = ["name", "language", "code", "saved_filenames", "desc"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    SAVED_FILENAMES_FIELD_NUMBER: _ClassVar[int]
    DESC_FIELD_NUMBER: _ClassVar[int]
    name: str
    language: str
    code: str
    saved_filenames: _containers.RepeatedScalarFieldContainer[str]
    desc: str
    def __init__(self, name: _Optional[str] = ..., language: _Optional[str] = ..., code: _Optional[str] = ..., saved_filenames: _Optional[_Iterable[str]] = ..., desc: _Optional[str] = ...) -> None: ...

class AssembleAppResponse(_message.Message):
    __slots__ = ["code", "msg"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...

class RunAppRequest(_message.Message):
    __slots__ = ["name"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    name: str
    def __init__(self, name: _Optional[str] = ...) -> None: ...

class AppInfo(_message.Message):
    __slots__ = ["name", "language", "ctime"]
    NAME_FIELD_NUMBER: _ClassVar[int]
    LANGUAGE_FIELD_NUMBER: _ClassVar[int]
    CTIME_FIELD_NUMBER: _ClassVar[int]
    name: str
    language: str
    ctime: int
    def __init__(self, name: _Optional[str] = ..., language: _Optional[str] = ..., ctime: _Optional[int] = ...) -> None: ...

class QueryAppsRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class QueryAppsResponse(_message.Message):
    __slots__ = ["apps"]
    APPS_FIELD_NUMBER: _ClassVar[int]
    apps: _containers.RepeatedCompositeFieldContainer[AppInfo]
    def __init__(self, apps: _Optional[_Iterable[_Union[AppInfo, _Mapping]]] = ...) -> None: ...

class PingRequest(_message.Message):
    __slots__ = []
    def __init__(self) -> None: ...

class PongResponse(_message.Message):
    __slots__ = ["code", "msg"]
    CODE_FIELD_NUMBER: _ClassVar[int]
    MSG_FIELD_NUMBER: _ClassVar[int]
    code: int
    msg: str
    def __init__(self, code: _Optional[int] = ..., msg: _Optional[str] = ...) -> None: ...
