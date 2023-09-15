import builtins
import functools
import sys
from typing import Any, Callable

from snowmate_collector.configs.collector_settings import CollectorSettings

used_attributes = {}

CUSTOM_GETATTRIBUTE = "snowmate_custom_gettattribute"
OVERRIDE_GETATTRIBUTE = "snowmate_override_getattribute"
CUSTOM_DEL = "snowmate_custom_del"


def is_custom_overriding_function(caller_method_name: str):
    return caller_method_name in {
        CUSTOM_GETATTRIBUTE,
        OVERRIDE_GETATTRIBUTE,
        CUSTOM_DEL,
    }


def snowmate_custom_gettattribute_decorator(gettattribute_method: Callable) -> Callable:
    @functools.wraps(gettattribute_method)
    def snowmate_custom_gettattribute(self, item: str) -> Any:
        attr_value = gettattribute_method(self, item)
        if id(self) in used_attributes and not callable(attr_value):
            func_code = sys._getframe(1).f_code  # # pylint: disable=protected-access
            caller_method = func_code.co_name
            call_method_file = func_code.co_filename
            if (
                not is_custom_overriding_function(caller_method)
                and not hasattr(self.__class__, caller_method)
                and call_method_file in CollectorSettings.project_files
            ):
                snowmate_override_getattribute(attr_value)
                used_attributes[id(self)].add(item)
        return attr_value

    return snowmate_custom_gettattribute


def snowmate_custom_snowmate_custom_del(del_method: Callable) -> Callable:
    @functools.wraps(del_method)
    def snowmate_custom_del(self):
        if used_attributes and id(self) in used_attributes:
            del used_attributes[id(self)]
        del_method(self)

    return snowmate_custom_del


def obj_has_custom_get_attribute(obj_instance: Any) -> bool:
    obj_get_attr = obj_instance.__class__.__getattribute__
    return (
        hasattr(obj_get_attr, "__code__")
        and obj_get_attr.__code__.co_name == CUSTOM_GETATTRIBUTE
    )


def snowmate_override_getattribute(obj_instance: Any) -> bool:
    """Override getattribute function for obj instance, return True if success, else False"""

    def do_nothing_del(_self) -> None:
        pass

    if obj_instance is not None and type(obj_instance).__module__ != builtins.__name__:
        try:
            used_attributes[id(obj_instance)] = set()
            if not obj_has_custom_get_attribute(obj_instance):
                del_func = do_nothing_del
                if hasattr(obj_instance.__class__, "__del__"):
                    del_func = obj_instance.__class__.__del__
                obj_instance.__class__.__del__ = snowmate_custom_snowmate_custom_del(
                    del_func
                )
                obj_instance.__class__.__getattribute__ = (
                    snowmate_custom_gettattribute_decorator(
                        obj_instance.__class__.__getattribute__
                    )
                )
            return True

        except (TypeError, AttributeError):
            return False
    return False
