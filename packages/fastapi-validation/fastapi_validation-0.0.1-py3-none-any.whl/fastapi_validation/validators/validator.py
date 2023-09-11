from pydantic import validator
from pydantic.typing import AnyCallable


class Validator:
    def __init__(
        self,
        field: str,  # FIXME: Currently only support check only individual field
        pre: bool = False,
        each_item: bool = False,
        always: bool = False,
        check_fields: bool = True,
        whole: bool = None,
        allow_reuse: bool = True,
    ):
        self.field = field
        self.pre = pre
        self.each_item = each_item
        self.always = always
        self.check_fields = check_fields
        self.whole = whole
        self.allow_reuse = allow_reuse

    def __call__(self, decorator: AnyCallable) -> object:
        return validator(
            self.field,
            pre=self.pre,
            each_item=self.each_item,
            always=self.always,
            check_fields=self.check_fields,
            whole=self.whole,
            allow_reuse=self.allow_reuse,
        )(decorator)
