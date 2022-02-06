class BusinessLogicError(Exception):
    pass


class NonUniqEmail(BusinessLogicError):
    def __init__(self, email: str):
        message = f"Email пользователя: {email} должен быть уникальным"
        super().__init__(message)


class RoomExistError(BusinessLogicError):
    def __init__(self, number):
        message = f"Комната с номером {number} уже существует"
        super().__init__(message)


class RoomNonFree(BusinessLogicError):
    def __init__(self):
        message = "Невозможно забронировать"  # например можно передавать uuid брони с которой пересечение
        super().__init__(message)
