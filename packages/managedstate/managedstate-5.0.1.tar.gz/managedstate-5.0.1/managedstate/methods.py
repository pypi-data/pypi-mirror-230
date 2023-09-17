class ErrorMessages:
    @staticmethod
    def no_default(path_index):
        raise ValueError(f"no value found and no default provided for the path key at index {path_index}")
