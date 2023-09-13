from abc import ABC, abstractmethod
from collections import defaultdict

from switcore.action.activity_router import ActivityRouter, PathResolver
from switcore.action.exceptions import UndefinedSubmitAction
from switcore.action.schemas import SwitRequest, BaseState, SwitResponse, UserActionType
from switcore.type import SyncDrawerHandler


class SyncActivityHandlerABC(ABC):
    def __init__(self) -> None:
        self.handlers: dict[str, SyncDrawerHandler] = dict()
        self.view_actions: dict[str, set[str]] = defaultdict(set)

    def include_activity_router(self, activity_router: ActivityRouter):
        self.view_actions.update(activity_router.view_actions)
        for action_id, func in activity_router.handlers.items():
            self.handlers[action_id] = func

    def on_turn(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        if swit_request.user_action.type == UserActionType.view_actions_drop:
            response = self.on_view_actions_drop(swit_request, state, *args, **kwargs)
        elif swit_request.user_action.type == UserActionType.view_actions_submit:
            response = self.on_view_actions_submit(swit_request, state, *args, **kwargs)
        elif swit_request.user_action.type == UserActionType.right_panel_open:
            response = self.on_right_panel_open(swit_request, state, *args, **kwargs)
        elif swit_request.user_action.type == UserActionType.view_actions_input:
            response = self.on_view_actions_input(swit_request, state, *args, **kwargs)
        elif swit_request.user_action.type == UserActionType.view_actions_oauth_complete:
            response = self.on_view_actions_oauth_complete(swit_request, state, *args, **kwargs)
        elif swit_request.user_action.type == UserActionType.user_commands_chat_extension:
            response = self.on_user_commands_chat_extension(swit_request, state, *args, **kwargs)
        elif swit_request.user_action.type == UserActionType.user_commands_chat:
            response = self.on_user_commands_chat(swit_request, state, *args, **kwargs)
        else:
            assert False, "undefined user_action type"

        return response

    @abstractmethod
    def on_right_panel_open(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    @abstractmethod
    def on_presence_sync(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    @abstractmethod
    def on_user_commands_chat(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    @abstractmethod
    def on_user_commands_chat_extension(
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    @abstractmethod
    def on_user_commands_chat_commenting(
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    @abstractmethod
    def on_user_commands_context_menus_message(
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    @abstractmethod
    def on_user_commands_context_menus_message_comment(
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    @abstractmethod
    def on_view_actions_drop(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()

    def on_view_actions_input(self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        return self.on_view_actions_submit(swit_request, state, *args, **kwargs)

    def on_view_actions_submit(
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        user_action: str = swit_request.user_action.id
        action_path_resolver: PathResolver = PathResolver.from_combined(user_action)
        view_key: str = PathResolver.from_combined(swit_request.current_view.view_id).key

        func_or_null: SyncDrawerHandler | None = self.handlers.get(action_path_resolver.key, None)
        view_ids_or_null: set[str] | None = self.view_actions.get(action_path_resolver.key, None)

        if func_or_null is None or view_ids_or_null is None:
            raise UndefinedSubmitAction(f"undefined submit action: {user_action}")

        if '*' not in view_ids_or_null and view_key not in view_ids_or_null:
            raise UndefinedSubmitAction(f"action is called in :{view_ids_or_null}")

        args = [swit_request, state, *action_path_resolver.paths, *args]
        response = func_or_null(*args, **kwargs)
        return response

    @abstractmethod
    def on_view_actions_oauth_complete(
            self, swit_request: SwitRequest, state: BaseState, *args, **kwargs) -> SwitResponse:
        raise NotImplementedError()
