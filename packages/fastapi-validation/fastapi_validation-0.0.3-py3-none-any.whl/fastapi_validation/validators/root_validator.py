from typing import Optional

from pydantic.class_validators import root_validator
from pydantic.typing import AnyCallable


class RootValidator:
    def __init__(
        self,
        _func: Optional[AnyCallable] = None,
        *,
        pre: bool = True,
        allow_reuse: bool = True,
        skip_on_failure: bool = False
    ):
        self._func = _func
        self.pre = pre
        self.allow_reuse = allow_reuse
        self.skip_on_failure = skip_on_failure

    def __call__(self, decorator: AnyCallable):
        return root_validator(
            _func=self._func, pre=self.pre, allow_reuse=self.allow_reuse, skip_on_failure=self.skip_on_failure
        )(decorator)
