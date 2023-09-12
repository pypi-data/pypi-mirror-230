# imports
from enum import Enum
from netsky.classifiers import ai_classifier


# classifiers
@ai_classifier
class EvalPythonCode(Enum):
    """
    Classifies Python code as valid or invalid.
    """

    INVALID = False
    VALID = True


@ai_classifier
class EvalSQLCode(Enum):
    """
    Classifies SQL code as valid or invalid.
    """

    INVALID = False
    VALID = True
