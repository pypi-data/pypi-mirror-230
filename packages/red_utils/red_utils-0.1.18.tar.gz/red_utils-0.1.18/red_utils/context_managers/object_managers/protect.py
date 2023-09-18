"""Context manager classes to protect instances of objects."""
from __future__ import annotations

import inspect
import json

class ListProtect:
    """Protect a list during modification by modifying a copy instead of the original.

    Description:
        ListProtect creates a copy of a list before running operations like .append(), and prevents
        errors on the original object by destroying the copy if an error is encountered, only
        overwriting the original if no errors occur.

    Usage:
        ex_list = [1, 2, 3]

        ## Protects from a ZeroDivision error
        with ListProtect(ex_list) as copy:
            copy.append(1/0)

        print(f'List: {ex_list}')
    """

    def __init__(self, original: list):
        """Call immediately after with ListProtect() as copy."""
        if not isinstance(original, list):
            raise TypeError(
                f"Invalid type for protected list: ({type(original)}). Must be of type list."
            )

        ## Set class value to original list
        self.original = original

    def __enter__(self):
        """Call after initializing ListProtect instance."""
        ## Create a copy of the list to work on
        self.clone: list = self.original.copy()

        return self.clone

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Call if ListProtect context manager encounters an error."""
        ## No exception encountered, update original
        #  list and return
        if exc_type is None:
            self.original[:] = self.clone

        ## Error encountered, print details
        else:
            ## https://docs.python.org/3/library/inspect.html?highlight=currentframe
            frame = inspect.currentframe()
            ## Full path to error file
            file_name = frame.f_code.co_filename
            ## Line number where error occurred.
            file_no = frame.f_lineno

            ## Build error details dict
            err = {
                "success": False,
                "detail": {
                    "module": file_name,
                    "line": file_no,
                    "exception_type": exc_type,
                    "exception_text": exc_value,
                },
            }

            ## Return error, exit returning original list
            print(
                f"[ERROR] Error encountered running list operation on protected list. Details: \n{err}"
            )

        return True


class DictProtect:
    """Protect a dict during modification by modifying a copy instead of the original.

    Description:
        DictProtect creates a copy of a dict before running operations like .update(), and prevents
        errors on the original object by destroying the copy if an error is encountered, only
        overwriting the original if no errors occur.

    Usage:
        ex_dict = {"example": "value"}

        ## Protects from a ZeroDivision error
        with DictProtect(ex_dict) as copy:
            copy["example"] = 1 / 0

        print(f'Dict: {ex_dict}')
    """

    def __init__(self, original: dict):
        """Call immediately after with DictProtect() as copy."""
        if not isinstance(original, dict):
            raise TypeError(
                f"Invalid type for protected dict: ({type(original)}). Must be of type dict."
            )

        ## Set class value to original dict
        self.original = original

    def __enter__(self):
        """Call after initializing DictProtect instance."""
        ## Create a copy of the dict to work on
        self.clone: dict = self.original.copy()

        return self.clone

    def __exit__(self, exc_type, exc_value, exc_traceback):
        """Call if DictProtect context manager encounters an error."""
        ## No exception encountered, update original
        #  list and return
        if exc_type is None:
            self.original[:] = self.clone

        ## Error encountered, print details
        else:
            ## https://docs.python.org/3/library/inspect.html?highlight=currentframe
            frame = inspect.currentframe()
            ## Full path to error file
            file_name = frame.f_code.co_filename
            ## Line number where error occurred.
            file_no = frame.f_lineno

            ## Build error details dict
            err = {
                "success": False,
                "detail": {
                    "module": file_name,
                    "line": file_no,
                    "exception_type": exc_type,
                    "exception_text": exc_value,
                },
            }

            ## Return error, exit returning original list
            print(
                f"[ERROR] Error encountered running dict operation on protected dict. Details: \n{err}"
            )

        return True
