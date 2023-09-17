# imports
from netsky.tools import tool

from io import StringIO
from contextlib import redirect_stdout

from netsky.functions import (
    gen_python_function,
    fix_python_function,
)


# tools
@tool
def text_to_python(question: str) -> str:
    """Returns a Python function given text."""
    return gen_python_function(question)


@tool
def fix_python_error(code: str, error: str) -> str:
    """Fixes a Python error in the code."""
    return fix_python_function(code, error)


@tool
def python_function_to_udf(code: str) -> str:
    """Converts a Python function to an Ibis UDF."""
    return f"""
import ibis

@ibis.udf.scalar.python
{code}""".strip()


@tool
def run_python_function(code: str) -> str:
    """Execute Python code as a string and return the output"""
    f = StringIO()

    with redirect_stdout(f):
        try:
            exec(code)
        except Exception as e:
            return str(f"Error: {e}")

    print(f.getvalue())
    return f.getvalue()
