class UserDomainError(Exception):
    """Base class for user domain exceptions."""


class UserNotFoundError(UserDomainError):
    def __init__(self, user_id: object | None = None) -> None:
        message = "User not found" if user_id is None else f"User '{user_id}' not found"
        super().__init__(message)


class UserAlreadyExistsError(UserDomainError):
    def __init__(self, field: str, value: str) -> None:
        super().__init__(f"User with {field} '{value}' already exists")
