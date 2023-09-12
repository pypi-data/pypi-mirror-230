from typing import Any, Dict, List, Optional
import typing

from pydantic import BaseModel, Field
from enum import Enum


class TypeSchema(BaseModel):
    name: str
    fields: Any


class IOValue(BaseModel):
    value: Any
    type: TypeSchema


class IO(BaseModel):
    input: Optional[IOValue]
    output: Optional[IOValue]


class LLMOutputModelMetadata(BaseModel):
    logprobs: Optional[Any]
    prompt_tokens: Optional[int]
    output_tokens: Optional[int]
    total_tokens: Optional[int]


class LLMOutputModel(BaseModel):
    raw_text: str
    metadata: LLMOutputModelMetadata


class LLMEventInputPrompt(BaseModel):
    template: str
    template_args: Dict[str, str]


class LLMEventInput(BaseModel):
    prompt: LLMEventInputPrompt
    invocation_params: Dict[str, Any]


class LLMEventSchema(BaseModel):
    mdl_name: str = Field(alias="model_name")
    provider: str
    input: LLMEventInput
    output: Optional[LLMOutputModel]


class EventChain(BaseModel):
    function_name: str
    variant_name: Optional[str]


class LogSchemaContext(BaseModel):
    hostname: str
    process_id: str
    stage: Optional[str]
    latency_ms: Optional[int]
    start_time: str
    tags: Dict[str, str]
    event_chain: List[EventChain]


class Error(BaseModel):
    code: int
    message: str
    traceback: Optional[str]


MetadataType = LLMEventSchema


class LogSchema(BaseModel):
    project_id: str
    event_type: typing.Literal["log", "func_llm", "func_prob", "func_code"]
    root_event_id: str
    event_id: str
    parent_event_id: Optional[str]
    context: LogSchemaContext
    io: IO
    error: Optional[Error]
    metadata: Optional[MetadataType]


### Tests
class CreateCycleRequest(BaseModel):
    project_id: str
    session_id: str


class CreateCycleResponse(BaseModel):
    test_cycle_id: str
    dashboard_url: str


class LogTestTags(BaseModel):
    test_cycle_id: str
    test_dataset_name: str
    test_case_name: str
    test_case_arg_name: str


class TestCaseStatus(str, Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    PASSED = "PASSED"
    FAILED = "FAILED"
    CANCELLED = "CANCELLED"
    EXPECTED_FAILURE = "EXPECTED_FAILURE"
