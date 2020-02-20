
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


class AttributeException(BaseException):
    code = 300
    detail = "Attribute {} has some problems"
    def __init__(self, attribute):
        self.detail = self.detail.format(attribute)


class MissingAttributeException(AttributeException):
    code = 320
    detail = "Attribute {} is missing"
    

class TaxoTreeMissingAttributeException(MissingAttributeException):
    code = 321
    detail = "Attribute {} is missing from taxonomy tree"
    

class DatasetMissingAttributeException(MissingAttributeException):
    code = 322
    detail = "Attribute {} is missing from an item of dataset"


class AttributeValueException(AttributeException):
    code = 350
    detail = "Value of attribute {} has some problems"


class DatasetAttributeMissingValueException(AttributeValueException):
    code = 351
    detail = "Attribute {} from dataset has no value"
    

class TaxoTreeFloatAtttributeException(AttributeValueException):
    code = 355
    detail = "Float attribute {} of taxonomy tree has no range info"


class TaxoTreeCategoryAttributeException(AttributeValueException):
    code = 360
    detail = "Category attribute {} of taxonomy tree has no root value"
