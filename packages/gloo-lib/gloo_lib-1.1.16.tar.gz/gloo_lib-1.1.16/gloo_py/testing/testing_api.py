import asyncio
import os
import typing
from pydantic import BaseModel
import aiohttp
import pytest
import requests
from ..env import ENV
from ..api_types import CreateCycleRequest, CreateCycleResponse, TestCaseStatus
from ..logging import logger

U = typing.TypeVar("U", bound=BaseModel)


class TestAPIWrapper:
    def __init__(self) -> None:
        self.base_url = ENV.GLOO_BASE_URL
        key = ENV.GLOO_APP_SECRET

        self.headers = {
            "Content-Type": "application/json",
        }
        if key:
            self.headers["Authorization"] = f"Bearer {key}"
        self.__session_id = ENV.GLOO_PROCESS_ID
        self.__called_cycle_id = False

    async def global_gloo_cycle_id(
        self,
        *,
        py_session: pytest.Session,
        session: typing.Optional[aiohttp.ClientSession] = None,
    ) -> str:
        await self.__create_cycle_id(
            create_cycle_request=CreateCycleRequest(
                project_id=ENV.GLOO_APP_ID,
                session_id=self.__session_id,
            ),
            session=session,
        )

        return self.__session_id

    def __post_sync(
        self,
        url: str,
        data: typing.Dict[str, typing.Any],
        model: typing.Optional[typing.Type[U]] = None,
    ) -> typing.Union[U, typing.Any]:
        try:
            with requests.session() as s:
                response = s.post(
                    f"{self.base_url}/{url}", json=data, headers=self.headers
                )

            text = response.text
            if response.status_code != 200:
                raise Exception(f"GlooTest Error: /{url} {response.status_code} {text}")
            if model:
                return model.model_validate_json(text)
            return response.json()

        except Exception as e:
            raise e

    async def __post(
        self,
        url: str,
        data: typing.Dict[str, typing.Any],
        model: typing.Optional[typing.Type[U]] = None,
        *,
        session: typing.Optional[aiohttp.ClientSession] = None,
    ) -> typing.Union[U, typing.Any]:
        try:
            if not session:
                async with aiohttp.ClientSession() as s:
                    response = await s.post(
                        f"{self.base_url}/{url}", json=data, headers=self.headers
                    )
            else:
                response = await session.post(
                    f"{self.base_url}/{url}", json=data, headers=self.headers
                )

            text = await response.text()
            if response.status != 200:
                raise Exception(f"GlooTest Error: /{url} {response.status} {text}")
            if model:
                return model.model_validate_json(text)
            return await response.json()

        except Exception as e:
            raise e

    async def __create_cycle_id(
        self,
        create_cycle_request: CreateCycleRequest,
        *,
        session: typing.Optional[aiohttp.ClientSession] = None,
    ) -> str:
        response = await self.__post(
            "tests/create-cycle",
            create_cycle_request.model_dump(by_alias=True),
            CreateCycleResponse,
            session=session,
        )
        if not response:
            raise Exception(
                "Failed to register test with Gloo Services. Did you forget to run init_gloo with a project_id anywhere in the call path?"  # noqa: E501
            )
        logger.info(f"\033[94mSee test results at: {response.dashboard_url}\033[0m")
        assert self.__session_id == response.test_cycle_id
        return response.test_cycle_id

    async def create_test_cases(
        self,
        dataset_name: str,
        test_name: str,
        test_case_names: typing.List[str],
        *,
        session: typing.Optional[aiohttp.ClientSession] = None,
    ) -> None:
        case_args_dict = [{"name": arg} for arg in test_case_names]
        await self.__post(
            "tests/create-case",
            {
                "project_id": ENV.GLOO_APP_ID,
                "test_cycle_id": self.__session_id,
                "test_dataset_name": dataset_name,
                "test_name": test_name,
                "test_case_args": case_args_dict,
            },
            session=session,
        )

    def update_test_case(
        self,
        dataset_name: str,
        test_name: str,
        test_case_name: str,
        status: TestCaseStatus,
        error: typing.Optional[typing.Any] = None,
    ) -> None:
        self.__post_sync(
            "tests/update",
            {
                "project_id": ENV.GLOO_APP_ID,
                "test_cycle_id": self.__session_id,
                "test_dataset_name": dataset_name,
                "test_case_definition_name": test_name,
                "test_case_arg_name": test_case_name,
                "status": status,
                "result_data": None,
                "error_data": error,
            },
        )
