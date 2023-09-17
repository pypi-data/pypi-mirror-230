from .partialquery import PartialQuery


class PartialQueries:
    """
    Helper class that exposes some pre-made PartialQuery objects to slot into a `.register()` call
    """

    KEY = PartialQuery(lambda key: key)  # Simply provides the deferred key as-is


class Keys:
    REGISTERED_PATH_LABEL = "registered_path_label"
    CUSTOM_QUERY_ARGS = "custom_query_args"

    PATH_KEYS = "path_keys"
    DEFAULTS = "defaults"
