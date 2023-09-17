class ErrorMessages:
    @staticmethod
    def invalid_method(method_name):
        raise ValueError(f"unable to add listeners to the specified method: {method_name}")
