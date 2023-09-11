from types import FunctionType
from typing import Optional, Any
from uuid import UUID

from sqlalchemy import text
from fastapi_exception import EntityNotFoundException

from config.database import run_with_global_session
from ..types.custom_condition import CustomCondition
from ..constants.validator_constant import VALIDATOR_EXISTS
from .base import BaseValidator


class Exists(BaseValidator):
    __name__ = VALIDATOR_EXISTS

    def __init__(
        self,
        table,
        column: Any,
        case_insensitive: bool = False,
        customs: Optional[list[CustomCondition]] = [],
    ):
        self.table = table
        self.column = column
        self.case_insensitive = case_insensitive
        self.customs = customs

    def validate(self, value: Any, values: dict[str, Any], *criterion):
        return run_with_global_session(
            lambda session: session.query(self.table).with_entities(self.table.id).filter(*criterion).first()
        )

    def __call__(self, value: Optional[Any], values: dict[str, Any]) -> Optional[UUID]:
        if not value:
            return value

        criterion = self.init_criterion(self.case_insensitive, self.table.__tablename__, self.column, value)
        self.build_custom_criterion(criterion, self.table.__tablename__, values, self.customs)

        if not self.validate(value, values, *criterion):
            raise EntityNotFoundException(self.table)

        return value

    def init_criterion(self, case_insensitive: bool, table_name: str, column: str, value):
        if case_insensitive:
            return {text(f'"{table_name}".{column} ILIKE :value').bindparams(value=value)}

        return {text(f'"{table_name}".{column} = :value').bindparams(value=value)}

    def build_custom_criterion(self, criterion, table_name: str, values: dict[str, Any], customs: list[CustomCondition]):  # noqa
        for custom in customs:
            custom['exclude'] = False if 'exclude' not in custom else custom.get('exclude')
            custom_column = custom['column']
            custom_value = (
                custom.get('value')(values) if isinstance(custom.get('value'), FunctionType) else custom.get('value')
            )

            sub_criterion = set()
            if custom['exclude']:
                if not custom_value or custom_value is None:
                    sub_criterion.add(text(f'"{table_name}.{custom_column} IS NOT NULL'))
                else:
                    sub_criterion.add(
                        text(f'"{table_name}".{custom_column} != :custom_value').bindparams(custom_value=custom_value)
                    )
            else:
                if not custom_value or custom_value is None:
                    sub_criterion.add(text(f'"{table_name}".{custom_column} IS NULL'))
                else:
                    sub_criterion.add(
                        text(f'"{table_name}".{custom_column} = :custom_value').bindparams(custom_value=custom_value)
                    )

            criterion.add(*sub_criterion)
