import time
from inspect import isclass
from typing import Any, Callable
from warnings import warn

import arrow
from pydantic import BaseModel, Field
from typing_extensions import Annotated


class AliasResponse:
    """
    @autoapi False
    Placeholder interface for a raw_response to ensure backwards compatibility if a user uses unsupported internal methods
    """

    def __init__(self, data_class):
        self.data_class = data_class

    @property
    def content(self):
        raise NotImplementedError  # TODO: No good way of handling this

    @property
    def status_code(self):
        return 200  # TODO: Placeholder

    def json(self):
        return self.data_class.dict()

    def text(self):
        return self.json()


class RhinoBaseModel(BaseModel):
    session: Annotated[Any, Field(exclude=True)]
    _persisted: bool = False

    def __init__(self, **data):
        self._handle_aliases(data)
        self._handle_uids(data)
        self._handle_models(data)
        super().__init__(**data)

    def __str__(self):
        return f"{self.__class__.__name__} {super(RhinoBaseModel, self).__str__()}"

    class Config:
        """
        @autoapi False
        """

        ignore_extra = True
        underscore_attrs_are_private = True

    def _handle_uids(self, data):
        """
        Remap backend uid results to uid parameter
        """
        for field in self.__fields__:
            if data.get(field, None) is not None:  # User passed in or already converted
                continue
            if field.endswith("_uids"):
                old_key = field[:-5]
            elif field.endswith("_uid"):
                old_key = field[:-4]
            else:
                continue
            value = data.get(old_key, None)
            if value is not None:
                data[field] = value

    def _handle_models(self, data):
        """
        Add the session variable to any child models
        """
        session = getattr(self, "session", data.get("session"))
        for field, field_attr in self.__fields__.items():
            if isclass(field_attr.type_) and issubclass(field_attr.type_, RhinoBaseModel):
                value = data.get(field, None)
                if field_attr.sub_fields is not None and isinstance(value, list):
                    for entry in value:
                        if isinstance(entry, dict):
                            entry["session"] = session
                else:
                    if isinstance(value, dict):
                        data[field]["session"] = session

    def _handle_aliases(self, data):
        for field, field_attr in self.__fields__.items():
            if field_attr.name != field_attr.alias:
                value = data.get(field_attr.name, None)
                if value is not None:
                    data[field_attr.alias] = value

    def raw_response(self):
        warn(
            f"The SDK method you called now returns a {self.__class__.__name__} dataclass. Please update your code to use the dataclass instead. You can directly access fields on the return result, or call .dict() for a similar interface"
        )
        return AliasResponse(self)

    def json(self, *args, **kwargs):
        # TODO: Need to reverse the uids
        super(RhinoBaseModel, self).json(*args, **kwargs)

    def _wait_for_completion(
        self,
        name: str,
        is_complete: bool,
        query_function: Callable,
        validation_function: Callable,
        timeout_seconds: int = 500,
        poll_frequency: int = 10,
        print_progress: bool = True,
        is_successful: Callable = lambda result: True,
        on_success: Callable = lambda result: print("Done"),
        on_failure: Callable = lambda result: print("Finished with errors"),
    ):
        """
        @autoapi False

        Reusable code for waiting for pending operations to complete
        :param name: Name of the operation
        :param is_complete: Whether or not the object has finished
        :param query_function: lamnda(self) -> dataclass What SDK function to call to check
        :param validation_function: lambda(old_object, new_object) -> bool whether to break checking
        :param timeout_seconds: Timeout in total seconds
        :param poll_frequency: Frequency to poll
        :param print_progress: Show progress to users
        :param is_successful: lambda(result) -> bool Whether the operation was successful
        :param on_success: lambda(result) -> None What to do on success
        :param on_failure: lambda(result) -> None What to do on failure
        :return: dataclass
        """
        if is_complete:
            return self
        start_time = arrow.utcnow()
        timeout_time = start_time.shift(seconds=timeout_seconds)
        while arrow.utcnow() < timeout_time:
            try:
                new_result = query_function(self)
                if validation_function(self, new_result):
                    if is_successful(new_result):
                        on_success(new_result)
                    else:
                        on_failure(new_result)
                    return new_result
            except Exception as e:
                raise Exception(f"Exception in wait_for_completion() calling get_status(): {e}")
            if print_progress:
                time_eclipsed = arrow.utcnow().humanize(
                    start_time, granularity=["hour", "minute", "second"], only_distance=True
                )
                print(f"Waiting for {name} to complete ({time_eclipsed})")
            if poll_frequency:
                time.sleep(poll_frequency)
        raise Exception(f"Timeout waiting for {name} to complete")
