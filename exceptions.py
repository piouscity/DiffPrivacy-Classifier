
class BaseException:
    code = 1
    detail = "Base exception"


class OpenFileException:
    code = 20
    detail = "Can not open file: {}"
    def __init__(self, file_path):
        self.detail = self.detail.format(file_path)
