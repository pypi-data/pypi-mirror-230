
from enum import Enum


class PythonWarnings(Enum):
    DEFAULT: str = 'default'    # Warn once per call location
    ERROR:   str = 'error'      # Convert to exceptions
    ALWAYS:  str = 'always'     # Warn every time
    MODULE:  str = 'module'     # Warn once per calling module
    ONCE:    str = 'once'       # Warn once per Python process
    IGNORE:  str = 'ignore'     # Never warn
