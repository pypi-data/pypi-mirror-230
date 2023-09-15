import datetime
import unittest

from switcore.action.activity_handler_abc import ActivityHandlerABC
from switcore.action.activity_router import ActivityRouter, PathResolver
from switcore.action.exceptions import UndefinedSubmitAction
from switcore.action.schemas import SwitRequest, PlatformTypes, UserInfo, UserPreferences, Context, UserAction, \
    UserActionType, View, Body, BaseState, SwitResponse, ViewCallbackType
from switcore.ui.header import Header


class ActivityHandler(ActivityHandlerABC):

    async def on_query(self, swit_request: SwitRequest, state: BaseState, query: str, *args, **kwargs) -> SwitResponse:
        pass

    async def on_right_panel_open(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_presence_sync(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_chat(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_chat_extension(self, swit_request: SwitRequest, state: BaseState, *args,
                                              **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_chat_commenting(self, swit_request: SwitRequest, state: BaseState, *args,
                                               **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_context_menus_message(self, swit_request: SwitRequest, state: BaseState, *args,
                                                     **kwargs) -> SwitResponse:
        pass

    async def on_user_commands_context_menus_message_comment(self, swit_request: SwitRequest, state: BaseState, *args,
                                                             **kwargs) -> SwitResponse:
        pass

    async def on_view_actions_drop(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        pass

    async def on_view_actions_oauth_complete(self, swit_request: SwitRequest, state: BaseState, *args,
                                             **kwargs) -> SwitResponse:
        pass


def create_swit_request(view_id: str, action_id: str):
    return SwitRequest(
        platform=PlatformTypes.DESKTOP,
        time=datetime.datetime.now(),
        app_id="test_app_id",
        user_info=UserInfo(
            user_id="test_user_id",
            organization_id="test_organization_id"
        ),
        user_preferences=UserPreferences(
            language="ko",
            time_zone_offset="+0900",
            color_theme="light"
        ),
        context=Context(
            workspace_id="test_workspace_id",
            channel_id="test_channel_id"
        ),
        user_action=UserAction(
            type=UserActionType.view_actions_submit,
            id=action_id,
            slash_command="test_slash_command",
        ),
        current_view=View(
            view_id=view_id,
            state="state",
            header=Header(
                title="test_title",
            ),
            body=Body(
                elements=[]
            ),
        ))


class RouterTest(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self) -> None:
        self.activity_handler = ActivityHandler()
        return await super().asyncSetUp()

    async def test_router01(self):
        activity_router = ActivityRouter()
        action_id: str = str(PathResolver("test_action_id01"))
        swit_request: SwitRequest = create_swit_request("right_panel", action_id)

        @activity_router.register("test_action_id01")
        async def draw_webhook_create(request: SwitRequest, state: BaseState):  # noqa F811
            return SwitResponse(callback_type=ViewCallbackType.update)

        self.activity_handler.include_activity_router(activity_router)

        swit_response = await self.activity_handler.on_turn(swit_request, BaseState())
        self.assertTrue(isinstance(swit_response, SwitResponse))

    async def test_router02(self):
        activity_router = ActivityRouter()
        path_resolver = PathResolver("test_action_id01", ["a", 1])
        swit_request: SwitRequest = create_swit_request("right_panel", str(path_resolver))

        @activity_router.register("test_action_id01", ["right_panel"])
        async def draw_webhook_create(request: SwitRequest, state: BaseState, a: str, number: int):  # noqa F811
            self.assertEqual(a, "a")
            self.assertEqual(number, 1)
            return SwitResponse(callback_type=ViewCallbackType.update)

        self.activity_handler.include_activity_router(activity_router)

        swit_response = await self.activity_handler.on_turn(swit_request, BaseState())
        self.assertTrue(isinstance(swit_response, SwitResponse))

    async def test_router03(self):
        activity_router01 = ActivityRouter()
        activity_router02 = ActivityRouter()
        action_id_01: str = str(PathResolver("test_action_id01"))
        action_id_02: str = str(PathResolver("test_action_id02"))

        swit_request_01: SwitRequest = create_swit_request("right_panel01", action_id_01)
        swit_request_02: SwitRequest = create_swit_request("right_panel02", action_id_02)

        @activity_router01.register("test_action_id01", ["right_panel01"])
        async def draw_func_01(request: SwitRequest, state: BaseState):  # noqa F811
            return SwitResponse(callback_type=ViewCallbackType.update)

        @activity_router02.register("test_action_id02", ["right_panel02"])
        async def draw_func_02(request: SwitRequest, state: BaseState):  # noqa F811
            return SwitResponse(callback_type=ViewCallbackType.update)

        self.activity_handler.include_activity_router(activity_router01)
        self.activity_handler.include_activity_router(activity_router02)

        swit_response_01 = await self.activity_handler.on_turn(swit_request_01, BaseState())
        swit_response_02 = await self.activity_handler.on_turn(swit_request_02, BaseState())

        self.assertTrue(isinstance(swit_response_01, SwitResponse))
        self.assertTrue(isinstance(swit_response_02, SwitResponse))

    async def test_router04(self):
        activity_router = ActivityRouter()
        action_id_01: str = str(PathResolver("test_action_id01"))
        action_id_02: str = str(PathResolver("test_action_id02"))
        action_id_03: str = str(PathResolver("test_action_id03", ["a", 1]))

        swit_request_01: SwitRequest = create_swit_request("right_panel", action_id_01)
        swit_request_02: SwitRequest = create_swit_request("right_panel", action_id_02)
        swit_request_03: SwitRequest = create_swit_request("right_panel", action_id_03)

        invalid_swit_request_01: SwitRequest = create_swit_request("modal", action_id_01)

        @activity_router.register("test_action_id01", ["right_panel"])
        async def draw_func_01(request: SwitRequest, state: BaseState):  # noqa F811
            return SwitResponse(callback_type=ViewCallbackType.update)

        @activity_router.register("test_action_id02", ["right_panel"])
        async def draw_func_02(request: SwitRequest, state: BaseState):  # noqa F811
            return SwitResponse(callback_type=ViewCallbackType.update)

        @activity_router.register("test_action_id03")
        async def draw_func_03(request: SwitRequest, state: BaseState, a: str, number: int):  # noqa F811
            self.assertEqual(a, "a")
            self.assertEqual(number, 1)
            return SwitResponse(callback_type=ViewCallbackType.update)

        self.activity_handler.include_activity_router(activity_router)

        swit_response_01 = await self.activity_handler.on_turn(swit_request_01, BaseState())
        swit_response_02 = await self.activity_handler.on_turn(swit_request_02, BaseState())
        swit_response_03 = await self.activity_handler.on_turn(swit_request_03, BaseState())

        self.assertTrue(isinstance(swit_response_01, SwitResponse))
        self.assertTrue(isinstance(swit_response_02, SwitResponse))
        self.assertTrue(isinstance(swit_response_03, SwitResponse))

        with self.assertRaises(UndefinedSubmitAction):
            await self.activity_handler.on_turn(invalid_swit_request_01, BaseState())

    async def test_router_with_slash(self):
        activity_router = ActivityRouter()
        swit_request = create_swit_request("right_panel", str(PathResolver("test_action_id01/aa/bb", ["a/a/b", 1])))

        @activity_router.register("test_action_id01/aa/bb", ["right_panel"])
        async def draw_webhook_create(request: SwitRequest, state: BaseState, a: str, number: int):  # noqa F811
            self.assertEqual(a, "a/a/b")
            self.assertEqual(number, 1)
            return SwitResponse(callback_type=ViewCallbackType.update)

        self.activity_handler.include_activity_router(activity_router)

        swit_response = await self.activity_handler.on_turn(swit_request, BaseState())
        self.assertTrue(isinstance(swit_response, SwitResponse))
