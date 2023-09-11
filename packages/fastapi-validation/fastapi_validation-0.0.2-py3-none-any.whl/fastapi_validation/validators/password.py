import re

from pydantic import MissingError

PASSWORD_REGEX = r'^(?=.*[A-Z])(?=.*\d)\S{6,}$'


class PasswordValidation(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(
            pattern=PASSWORD_REGEX,
            examples=['Secret@1234'],
        )

    @classmethod
    def validate(cls, value):
        if not isinstance(value, str) or not value:
            raise MissingError()

        if not re.search(PASSWORD_REGEX, value):
            raise ValueError()

        return cls(value)

    def __repr__(self):
        return f'PasswordValidation({super().__repr__()})'
