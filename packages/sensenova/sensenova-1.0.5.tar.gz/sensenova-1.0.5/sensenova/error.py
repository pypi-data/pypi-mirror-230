import sensenova


class SensenovaError(Exception):
    def __init__(
        self,
        message=None,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
        code=None
    ):
        super(SensenovaError, self).__init__(message)

        if http_body and hasattr(http_body, "decode"):
            try:
                http_body = http_body.decode("utf-8")
            except BaseException:
                http_body = (
                    "<Could not decode body as utf-8.>"
                )

        self._message = message
        self.http_body = http_body
        self.http_status = http_status
        self.json_body = json_body
        self.headers = headers or {}
        self.code = code
        self.error = self.construct_error_object()

    def __str__(self):
        msg = self._message or "<empty message>"
        return msg + '\n'

    def construct_error_object(self):
        if (
            self.json_body is None
            or not isinstance(self.json_body, dict)
            or "error" not in self.json_body
            or not isinstance(self.json_body["error"], dict)
        ):
            return None

        return sensenova.api_resources.error_object.ErrorObject.construct_from(
            self.json_body["error"]
        )


class APIConnectionError(SensenovaError):
    def __init__(
        self,
        message,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
        code=None,
        should_retry=False,
    ):
        super(APIConnectionError, self).__init__(
            message, http_body, http_status, json_body, headers, code
        )
        self.should_retry = should_retry


class InvalidRequestError(SensenovaError):
    def __init__(
        self,
        message,
        param=None,
        code=None,
        http_body=None,
        http_status=None,
        json_body=None,
        headers=None,
    ):
        super(InvalidRequestError, self).__init__(
            message, http_body, http_status, json_body, headers, code
        )
        self.param = param

    def __repr__(self):
        return "%s(message=%r, param=%r, code=%r, http_status=%r)" % (
            self.__class__.__name__,
            self._message,
            self.param,
            self.code,
            self.http_status,
        )

    def __reduce__(self):
        return type(self), (
            self._message,
            self.param,
            self.code,
            self.http_body,
            self.http_status,
            self.json_body,
            self.headers
        )


class ServiceUnavailableError(SensenovaError):
    pass


class APIError(SensenovaError):
    pass


class AuthenticationError(SensenovaError):
    pass


class RateLimitError(SensenovaError):
    pass


class PermissionError(SensenovaError):
    pass


class TryAgain(SensenovaError):
    pass
