class RoomExistError(Exception):
    def __init__(self, number):
        message = f"Комната с номером {number} уже существует"
        super().__init__(message)


class RoomNonFree(Exception):
    def __init__(self):
        message = "Невозможно забронировать"  # например можно передавать uuid брони с которой пересечение
        super().__init__(message)
