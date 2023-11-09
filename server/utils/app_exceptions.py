from fastapi import Request, status
from starlette.responses import JSONResponse


class AppExceptionCase(Exception):
    def __init__(self, status_code: int, detail: str):
        self.exception_case = self.__class__.__name__
        self.status_code = status_code
        self.detail = detail

    def __str__(self):
        return (
            f"<AppException {self.exception_case} - "
            + f"status_code={self.status_code} - detail={self.detail}>"
        )


async def app_exception_handler(request: Request, exc: AppExceptionCase):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "app_exception": exc.exception_case,
            "detail": exc.detail,
        },
    )


class AppException(object):
    class NotFoundException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Not found"
            self.detail = detail
            self.status_code = 404

    class AlreadyExistsException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Conflict"
            self.detail = detail
            self.status_code = 409

    class RegistrationException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Could not register"
            self.detail = detail
            self.status_code = 400

    class ValidationException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Invalid"
            self.detail = detail
            self.status_code = 422

    class UnauthorizedException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Unauthorized"
            self.detail = detail
            self.status_code = 401

    class ForbiddenException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Forbidden"
            self.detail = detail
            self.status_code = 403

    class CreationException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Could not create"
            self.detail = detail
            self.status_code = 400

    class InternalServerException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Internal server error"
            self.detail = detail
            self.status_code = 500

    class PaymentRequiredException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Payment required"
            self.detail = detail
            self.status_code = 402

    class TooLargeException(AppExceptionCase):
        def __init__(self, detail: str = None):
            self.exception_case = "Data is too large"
            self.detail = detail
            self.status_code = 413


async def internal_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"type": str(type(exc)), "context": str(exc.__context__)},
    )
