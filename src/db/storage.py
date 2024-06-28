import dataclasses
from collections import defaultdict
from typing import Any, DefaultDict

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType


@dataclasses.dataclass
class UserDataRecord:
    id: int
    data: dict[str, Any] = dataclasses.field(default_factory=dict)


class TGStorage(BaseStorage):
    """
    TMP solution: support integrating aiogram storage's logic with user's data
    """

    def __init__(self) -> None:
        self.storage: dict[int, UserDataRecord] = {}
        self.state: DefaultDict[StorageKey, StateType] = defaultdict(None)

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        self.state[key] = state

    async def get_state(self, key: StorageKey) -> StateType | None:
        return self.state[key]

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        if not (user_data := self.storage.get(key.user_id)):
            user_data = UserDataRecord(id=key.user_id)

        user_data.data = data
        self.storage[key.user_id] = user_data

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        return self.storage.get(key.user_id).data

    async def close(self) -> None:
        pass
