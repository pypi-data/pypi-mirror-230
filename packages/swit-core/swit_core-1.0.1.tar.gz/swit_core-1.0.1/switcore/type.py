from typing import Callable, Coroutine

from switcore.action.schemas import SwitResponse

DrawerHandler = Callable[..., Coroutine[None, None, SwitResponse]]
SyncDrawerHandler = Callable[..., SwitResponse]
