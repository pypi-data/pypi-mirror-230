# -*- coding: utf-8 -*-
import enum
import functools
import typing


_serpyco_tags = "__serpyco_tags__"


class DecoratorType(str, enum.Enum):
    PRE_DUMP = "pre_dump"
    POST_DUMP = "post_dump"
    PRE_LOAD = "pre_load"
    POST_LOAD = "post_load"


ObjCallable = typing.Callable[[object], object]
DictCallable = typing.Callable[
    [typing.Dict[str, typing.Any]], typing.Dict[str, typing.Any]
]
DecoratedCallable = typing.Union[ObjCallable, DictCallable]


def decorator_factory(decorator_type: DecoratorType) -> DecoratedCallable:
    def decorator(method: DecoratedCallable) -> DecoratedCallable:
        """
        This decorator can be applied to a callable taking one object or
        data class object and should return an object. The method will
        then be called with each object given to Serializer.dump or
        Serializer.dump_json before dumping them or with each object
        output by Serializer.load or Serializer.load_json before returning them.
        """
        setattr(method, _serpyco_tags, decorator_type)

        @functools.wraps(method)
        def wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
            try:
                result = method(*args, **kwargs)
            except TypeError:
                result = method(args[0], *args, **kwargs)

            return result

        return wrapper

    return typing.cast(DecoratedCallable, decorator)


pre_dump = decorator_factory(DecoratorType.PRE_DUMP)
post_dump = decorator_factory(DecoratorType.POST_DUMP)
pre_load = decorator_factory(DecoratorType.PRE_LOAD)
post_load = decorator_factory(DecoratorType.POST_LOAD)
