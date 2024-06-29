import json
import logging
import dataclasses
from collections import defaultdict
from typing import Any, DefaultDict

from aiogram.fsm.storage.base import BaseStorage, StorageKey, StateType

from src.config.app import TMP_DATA_DIR

logger = logging.getLogger(__name__)


@dataclasses.dataclass
class UserDataRecord:
    id: int
    data: dict[str, Any] = dataclasses.field(default_factory=dict)

    def dump(self) -> dict:
        return dataclasses.asdict(self)

    @classmethod
    def load(cls, data: dict) -> "UserDataRecord":
        return cls(**data)


class TGStorage(BaseStorage):
    """
    TMP solution: support integrating aiogram storage's logic with user's data
    """

    data_file_path = TMP_DATA_DIR / "user_address.json"

    def __init__(self) -> None:
        self.storage: dict[int, UserDataRecord] = self._load_from_file()
        self.state: DefaultDict[StorageKey, StateType] = defaultdict(None)

    async def set_state(self, key: StorageKey, state: StateType = None) -> None:
        self.state[key] = state

    async def get_state(self, key: StorageKey) -> StateType | None:
        return self.state.get(key)

    async def set_data(self, key: StorageKey, data: dict[str, Any]) -> None:
        if not (user_data := self.storage.get(key.user_id)):
            user_data = UserDataRecord(id=key.user_id)

        user_data.data = data
        self.storage[key.user_id] = user_data
        self._save_to_file()

    async def get_data(self, key: StorageKey) -> dict[str, Any]:
        if user_data := self.storage.get(key.user_id):
            return user_data.data

        return {}

    async def close(self) -> None:
        pass

    def _save_to_file(self) -> None:
        """Temp method for saving user's address (will be placed to use SQLite instead"""
        if not self.data_file_path.exists():
            self.data_file_path.touch()

        with open(self.data_file_path, "wt") as f:
            data = {user_id: data_record.dump() for user_id, data_record in self.storage.items()}
            json.dump(data, f)

    def _load_from_file(self) -> dict[int, UserDataRecord]:
        """Temp method for saving user's address (will be placed to use SQLite instead"""
        data = {}
        if self.data_file_path.exists():
            try:
                with open(self.data_file_path, "rt") as f:
                    data = json.load(f)
            except Exception as exc:
                logger.exception("Couldn't read from storage file: %r", exc)

        return {user_id: UserDataRecord.load(user_data) for user_id, user_data in data.items()}
