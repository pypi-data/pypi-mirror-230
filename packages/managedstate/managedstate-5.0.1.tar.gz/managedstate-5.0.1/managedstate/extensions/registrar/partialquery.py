from typing import Callable, Any


class PartialQuery:
    """
    Instances of this class can be provided as path keys only in Registrar.register_path().
    When registered_get()/registered_set() is called with the relevant path label, the function provided below
    will be called and passed one value from the custom query args list;
    a valid path key or KeyQuery instance should be returned
    """

    # As this class is used indirectly to determine the method of access into the state,
    # it should never be stored directly as a key within that state
    __hash__ = None

    def __init__(self, path_key_getter: Callable[[Any], Any]):
        self.__function = path_key_getter

    def __call__(self, query_args: Any) -> Any:
        return self.__function(query_args)
