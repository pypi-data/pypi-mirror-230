from typing import Optional, Any
from uuid import UUID
from fastapi_exception import DuplicateError

from ..constants.validator_constant import VALIDATOR_UNIQUE
from ..types.custom_condition_type import CustomCondition
from .exist import Exists


# TODO: Extend request body to support custom exclude
class Unique(Exists):
    __name__ = VALIDATOR_UNIQUE

    def __init__(
        self,
        table,
        column: Any,
        case_insensitive: bool = False,
        customs: Optional[list[CustomCondition]] = [],
    ):
        super().__init__(table, column, case_insensitive, customs)

    def validate(self, value: Any, values: dict[Any], *criterion):
        return super().validate(value, values, *criterion)

    def __call__(self, value: Optional[Any], values: dict[Any]) -> Optional[UUID]:
        if not value:
            return value

        criterion = super().init_criterion(self.case_insensitive, self.table.__tablename__, self.column, value)
        super().build_custom_criterion(criterion, self.table.__tablename__, values, self.customs)

        if self.validate(value, values, *criterion):
            raise DuplicateError(self.column)

        return value
