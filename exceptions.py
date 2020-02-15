
class BaseException(Exception):
    code = 1
    detail = "Base exception"


class FileException(BaseException):
    code = 200
    detail = "Error handling file {}"
    def __init__(self, file_path):
        self.detail = self.detail.format(file_path)


class OpenFileException(FileException):
    code = 201
    detail = "Can not open file {}"


class UnsupportedFileTypeException(FileException):
    code = 202
    detail = "File type is not supported: {}"
