class RoomExistError(Exception):
    def __init__(self, number):
        message = f"Комната с номером {number} уже существует"
        super().__init__(message)
