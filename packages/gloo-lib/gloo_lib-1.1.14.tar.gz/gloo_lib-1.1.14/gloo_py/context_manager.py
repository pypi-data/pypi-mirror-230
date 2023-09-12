import abc
from textwrap import dedent
import typing
from .llm_client import LLMClient
from .tracer import trace

InputType = typing.TypeVar("InputType")
OutputType = typing.TypeVar("OutputType")

T = typing.TypeVar("T")


# class GlooLoggerCtx:
#     __event_type: typing.Literal["log"]

#     def __init__(
#         self,
#         *,
#         scope_name: str,
#         args: typing.Any = None,
#     ):
#         self.__api = APIWrapper()
#         self.__event_type = "log"
#         self.__event_name = scope_name
#         self.__io = IO(
#             input=IOValue(
#                 value=args, type=TypeSchema(name=type(args).__name__, fields={})
#             ),
#             output=None,
#         )

#     def set_result(self, *, val: typing.Any) -> None:
#         self.__io.output = IOValue(
#             value=val, type=TypeSchema(name=type(val).__name__, fields={})
#         )

#     def __enter__(self) -> "GlooLoggerCtx":
#         event_chain = event_chain_var.get()
#         if event_chain is None:
#             event_chain = [
#                 EventBase(
#                     func_name=self.__event_name, variant_name=None, parent_event_id=None
#                 )
#             ]
#             event_chain_var.set(event_chain)
#         else:
#             # If the event_chain already exists, append to it
#             event_chain.append(
#                 EventBase(
#                     func_name=self.__event_name,
#                     variant_name=None,
#                     parent_event_id=event_chain[-1].event_id,
#                 )
#             )
#         return self

#     def __exit__(
#         self,
#         exc_type: typing.Optional[typing.Type[BaseException]],
#         exc_value: typing.Optional[BaseException],
#         tb: typing.Optional[TracebackType],
#     ) -> None:
#         if exc_type is not None:
#             formatted_traceback = "".join(
#                 traceback.format_exception(exc_type, exc_value, tb)
#             )
#             error = Error(
#                 # TODO: For GlooErrors, we should have a list of error codes.
#                 code=1,  # Unknown error.
#                 message=f"{exc_type.__name__}: {exc_value}",
#                 traceback=formatted_traceback,
#             )
#             self.__api.log_sync(
#                 event_type=self.__event_type,
#                 io=IO(input=None, output=None),
#                 error=error,
#             )
#         else:
#             error = None

#         self.__api.log_sync(event_type=self.__event_type, io=self.__io, error=error)

#         # Pop off the most recent event
#         event_chain = event_chain_var.get()
#         if event_chain:
#             event_chain.pop()

#         # If the event_chain is empty after the pop, set the context variable back to None
#         if not event_chain:
#             event_chain_var.set(None)

#         if error:
#             raise Exception(error)

#     async def __aenter__(self) -> "GlooLoggerCtx":
#         event_chain = event_chain_var.get()
#         if event_chain is None:
#             event_chain = [
#                 EventBase(
#                     func_name=self.__event_name, variant_name=None, parent_event_id=None
#                 )
#             ]
#             event_chain_var.set(event_chain)
#         else:
#             # If the event_chain already exists, append to it
#             event_chain.append(
#                 EventBase(
#                     func_name=self.__event_name,
#                     variant_name=None,
#                     parent_event_id=event_chain[-1].event_id,
#                 )
#             )
#         return self

#     async def __aexit__(
#         self,
#         exc_type: typing.Optional[typing.Type[BaseException]],
#         exc_value: typing.Optional[BaseException],
#         tb: typing.Optional[TracebackType],
#     ) -> typing.Optional[bool]:
#         if exc_type is not None:
#             formatted_traceback = "".join(
#                 traceback.format_exception(exc_type, exc_value, tb)
#             )
#             error = Error(
#                 # TODO: For GlooErrors, we should have a list of error codes.
#                 code=1,  # Unknown error.
#                 message=f"{exc_type.__name__}: {exc_value}",
#                 traceback=formatted_traceback,
#             )
#         else:
#             error = None

#         await self.__api.log(event_type=self.__event_type, io=self.__io, error=error)

#         # Pop off the most recent event
#         event_chain = event_chain_var.get()
#         if event_chain:
#             event_chain.pop()

#         # If the event_chain is empty after the pop, set the context variable back to None
#         if not event_chain:
#             event_chain_var.set(None)

#         # TODO: Determine if we should return True or None here.
#         # If we return True, the exception is suppressed in all parent context managers.
#         return error is None


class GlooVariant(typing.Generic[InputType, OutputType]):
    __func_name: str
    __name: str

    def __init__(self, *, func_name: str, name: str):
        self.__func_name = func_name
        self.__name = name

    @property
    def name(self) -> str:
        return self.__name

    @property
    def func_name(self) -> str:
        return self.__func_name

    @abc.abstractmethod
    async def _run(self, arg: InputType) -> OutputType:
        raise NotImplementedError

    async def run(self, arg: InputType) -> OutputType:
        response = await trace(_name=self.func_name, _tags={"__variant": self.name})(
            self._run
        )(arg)
        return response


class CodeVariant(GlooVariant[InputType, OutputType]):
    __func: typing.Callable[[InputType], typing.Awaitable[OutputType]]

    def __init__(
        self,
        func_name: str,
        name: str,
        *,
        func: typing.Callable[[InputType], typing.Awaitable[OutputType]],
    ):
        super().__init__(func_name=func_name, name=name)
        self.__func = func

    async def _run(self, arg: InputType) -> OutputType:
        return await self.__func(arg)


class LLMVariant(GlooVariant[InputType, OutputType]):
    __prompt: str
    __client: LLMClient

    def __init__(
        self,
        func_name: str,
        name: str,
        *,
        prompt: str,
        client: LLMClient,
        prompt_vars: typing.Callable[
            [InputType], typing.Awaitable[typing.Dict[str, str]]
        ],
        parser: typing.Callable[[str], typing.Awaitable[OutputType]],
    ):
        super().__init__(func_name=func_name, name=name)
        self.__prompt = prompt
        self.__client = client
        self.__prompt_vars = prompt_vars
        self.__parser = parser

    async def _run(self, arg: InputType) -> OutputType:
        prompt_vars = await self.__prompt_vars(arg)

        # Determine which prompt vars are used in the prompt string.
        # format is {@var_name}
        used_vars = set()
        for var_name in prompt_vars:
            if f"{{@{var_name}}}" in self.__prompt:
                used_vars.add(var_name)

        # If there are unused vars, log a warning
        prompt_vars_copy = {
            var_name: dedent(prompt_vars[var_name].lstrip("\n").rstrip())
            for var_name in used_vars
        }

        response = await self.__client.run(self.__prompt, vars=prompt_vars_copy)
        return await self.__parser(response)
