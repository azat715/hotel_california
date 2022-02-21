class AuthenticationError(Exception):
    pass


class NotFoundEmail(AuthenticationError):
    def __init__(self, email: str):
        message = f"Пользователь c email: {email} не существует"
        super().__init__(message)


class InvalidPassword(AuthenticationError):
    def __init__(self, email: str):
        message = f"У пользователя c email: {email} не правильный пароль"
        super().__init__(message)


class AuthenticationJwtError(AuthenticationError):
    pass


class BusinessLogicError(Exception):
    pass


class NonUniqEmail(BusinessLogicError):
    def __init__(self, email: str):
        message = f"Email пользователя: {email} должен быть уникальным"
        super().__init__(message)


class UserNotAdmin(BusinessLogicError):
    def __init__(self, email: str):
        message = f"Пользователь email: {email} должен быть администратором"
        super().__init__(message)


class RoomExistError(BusinessLogicError):
    def __init__(self, number):
        message = f"Комната с номером {number} уже существует"
        super().__init__(message)


class RoomNonFree(BusinessLogicError):
    def __init__(self, number):
        message = f"Комната {number} невозможно забронировать"  # например можно передавать uuid брони с которой пересечение
        super().__init__(message)


class RoomNotFound(BusinessLogicError):
    def __init__(self, number):
        message = f"Комната с номером {number} не существует"
        super().__init__(message)


class OrderNotFound(BusinessLogicError):
    def __init__(self, order_id):
        message = f"Ордер с номером {order_id} не существует"
        super().__init__(message)


class DatesNotValid(BusinessLogicError):
    pass


class OrderNotCancel(BusinessLogicError):
    pass
