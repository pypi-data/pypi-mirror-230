# imports
from marvin.tools import tool

from netsky.tools.internet import (
    open_browser,
    search_internet,
    webpage_to_str,
)
from netsky.tools.text import summarize_text, translate_text
from netsky.tools.code import text_to_python, fix_python_error, run_python_function
from netsky.tools.filesystem import read_file, list_files_and_dirs, write_file
from netsky.tools.birdbrain import list_tables, query_table, get_table_schema


# tools
tools = [
    # internet
    open_browser,
    search_internet,
    webpage_to_str,
    # text
    summarize_text,
    translate_text,
    # filesystem
    read_file,
    list_files_and_dirs,
    write_file,
    # code
    text_to_python,
    fix_python_error,
    run_python_function,
    # data
    list_tables,
    query_table,
    get_table_schema,
]

__all__ = ["tool", "tools"]
