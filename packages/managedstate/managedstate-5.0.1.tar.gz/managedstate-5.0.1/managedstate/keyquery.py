from objectextensions import Methods

from typing import Callable, Any


class KeyQuery:
    """
    Instances of this class can be provided as path keys when getting or setting the state,
    to indicate that the next nesting level of the state should be accessed via the path key returned
    from its stored function.
    The function will receive a copy of the state object at the current level of nesting
    in order to determine what key to return
    """

    # As this class is used indirectly to determine the method of access into the state,
    # it should never be stored directly as a key within that state
    __hash__ = None

    def __init__(self, path_key_getter: Callable[[Any], Any]):
        self.__function = path_key_getter
        self.__history = []

    def __call__(self, substate: Any) -> Any:
        result = self.__function(substate)
        self.__history.append(Methods.try_copy(result))

        return Methods.try_copy(result)

    @property
    def history(self) -> list:
        return self.__history
