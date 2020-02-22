
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
    

class TaxoTreeMissingAttributeException(AttributeException):
    code = 310
    detail = "Attribute {} is missing from taxonomy tree"
    

class DatasetMissingAttributeException(AttributeException):
    code = 301
    detail = "Attribute {} is missing from an item of dataset"


class DatasetAttributeMissingValueException(AttributeException):
    code = 302
    detail = "Attribute {} from dataset has no value"
    

class TaxoTreeFloatAtttributeMissingRootException(AttributeException):
    code = 320
    detail = "Float attribute {} of taxonomy tree has no range info"


class TaxoTreeFloatAtttributeRootException(AttributeException):
    code = 321
    detail = "Float attribute {} of taxonomy tree has invalid range info"


class TaxoTreeCategoryAttributeMissingRootException(AttributeException):
    code = 330
    detail = "Category attribute {} of taxonomy tree has no root value"


class TaxoNodeException(BaseException):
     code = 350
     detail = "Taxonomy node {path} is invalid"
     def __init__(self, path):
         self.detail = self.detail.format(path=path)


class TaxoNodeMissingKeyException(BaseException):
    code = 351
    detail = "Taxonomy node {path} missing key {key}"
    def __init__(self, path, key):
        self.detail = self.detail.format(path=path, key=key)


class TaxoTreeCoverageException(BaseException):
    code = 380
    detail = "Taxonomy tree of attribute {att} does not cover value {val}"
    def __init__(self, att, value):
        self.detail = self.detail.format(att=att, val=value)
