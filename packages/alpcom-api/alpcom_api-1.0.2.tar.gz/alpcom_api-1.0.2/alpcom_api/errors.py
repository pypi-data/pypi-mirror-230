class ApiError(Exception):
    pass


class AuthError(ApiError):
    ...


class ApiFormError(ApiError):
    def __init__(self, detail: dict):
        self.detail = detail

    def __str__(self):
        return str(self.detail)
