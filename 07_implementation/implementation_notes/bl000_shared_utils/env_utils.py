"""
Environment variable parsing utilities.

Provides type-safe functions for reading environment variables with defaults.
"""

import os


def env_int(name: str, default: int) -> int:
    """
    Get an environment variable as an int, with a default.
    
    Returns the default if:
    - Variable is not set
    - Variable is empty string
    - Variable cannot be parsed as int
    
    Args:
        name: Environment variable name
        default: Default value if variable not set or invalid
        
    Returns:
        Int value from environment or default
    """
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def env_float(name: str, default: float) -> float:
    """
    Get an environment variable as a float, with a default.
    
    Returns the default if:
    - Variable is not set
    - Variable is empty string
    - Variable cannot be parsed as float
    
    Args:
        name: Environment variable name
        default: Default value if variable not set or invalid
        
    Returns:
        Float value from environment or default
    """
    raw = os.environ.get(name)
    if raw is None or not str(raw).strip():
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def env_str(name: str, default: str) -> str:
    """
    Get an environment variable as a string, with a default.
    
    Returns the default if:
    - Variable is not set
    - Variable is empty string (after stripping whitespace)
    
    Args:
        name: Environment variable name
        default: Default value if variable not set or empty
        
    Returns:
        String value from environment or default
    """
    raw = os.environ.get(name)
    if raw is None:
        return default
    value = str(raw).strip()
    return value if value else default
