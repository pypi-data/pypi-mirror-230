from exceptiongroup import ExceptionGroup


class ValidationErrorsGroup(ExceptionGroup):
    pass


class ValidationError(Exception):
    pass


class RegistryError(Exception):
    pass
