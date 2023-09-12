import platform
from pathlib import Path


def get_cache_directory():
    home = Path.home()

    # Determine the OS-specific cache directory
    if platform.system() == "Windows":
        cache_dir = home / "AppData" / "Local" / "prompt_functions"
    elif platform.system() == "Darwin":  # macOS
        cache_dir = home / "Library" / "Caches" / "prompt_functions"
    else:  # Linux and other UNIX-like systems
        cache_dir = home / ".cache" / "prompt_functions"

    # Create the directory if it doesn't exist
    cache_dir.mkdir(parents=True, exist_ok=True)

    return cache_dir


def list_prompt_library():
    cache_dir = get_cache_directory()

    # List the directories inside the cache directory
    directories = [d.name for d in cache_dir.iterdir() if d.is_dir()]

    return directories
