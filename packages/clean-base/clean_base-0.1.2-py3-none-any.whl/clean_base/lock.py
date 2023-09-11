from pathlib import Path

from clean_base.settings import LOCK_FILE, LOCK_NAMED_FILE

# ? ----------------------------------------------------------------------------
# ? STANDARD LOCK FILE
# ? ----------------------------------------------------------------------------


def lock(base_dir: Path) -> bool:
    """Create a lock file in the base directory.

    Description:
        Designed to be used to prevent a single process to run multiple times is
        it was already executed previously.

    Args:
        base_dir (Path): The base directory to create the lock file in.

    Returns:
        bool: True if the lock file was created, False otherwise.

    """

    if not base_dir.is_dir():
        raise Exception(f"Invalid `base_dir`: {base_dir}")

    lock_file_path = base_dir.joinpath(LOCK_FILE)

    with lock_file_path.open("w") as lock:
        lock.write("1")
    return True


def has_lock(base_dir: Path) -> bool:
    """Check if a lock file exists in the base directory.

    Description:
        Designed to be used to prevent a single process to run multiple times is
        it was already executed previously.

    Args:
        base_dir (Path): The base directory to create the lock file in.

    Returns:
        bool: True if the lock file exists, False otherwise.

    """

    if not base_dir.is_dir():
        return False

    content = 0
    lock_file_path = base_dir.joinpath(LOCK_FILE)

    if not lock_file_path.exists():
        return False

    with lock_file_path.open("r") as lock:
        content = int(lock.read())

    if content == 1:
        return True
    return False


# ? ----------------------------------------------------------------------------
# ? NAMED LOCK FILE
# ? ----------------------------------------------------------------------------


def lock_named(base_dir: Path, step: str) -> bool:
    """Create a named lock file in the base directory.

    Description:
        Designed to be used to prevent a single process to run multiple times is
        it was already executed previously.

    Args:
        base_dir (Path): The base directory to create the lock file in.
        step (str): The name of the step to create the lock file for.

    Returns:
        bool: True if the lock file was created, False otherwise.

    """

    if not base_dir.is_dir():
        raise Exception(f"Invalid `base_dir`: {base_dir}")

    lock_file_path = base_dir.joinpath(LOCK_NAMED_FILE.format(step=step))

    with lock_file_path.open("w") as lock:
        lock.write("1")
    return True


def has_named_lock(base_dir: Path, step: str) -> bool:
    """Check if a named lock file exists in the base directory.

    Description:
        Designed to be used to prevent a single process to run multiple times is
        it was already executed previously.

    Args:
        base_dir (Path): The base directory to create the lock file in.
        step (str): The name of the step to create the lock file for.

    Returns:
        bool: True if the lock file exists, False otherwise.

    """

    if not base_dir.is_dir():
        return False

    content = 0
    lock_file_path = base_dir.joinpath(LOCK_NAMED_FILE.format(step=step))

    if not lock_file_path.exists():
        return False

    with lock_file_path.open("r") as lock:
        content = int(lock.read())

    if content == 1:
        return True
    return False


# ? ----------------------------------------------------------------------------
# ? SETUP DEFAULT EXPORTS
# ? ----------------------------------------------------------------------------


__all__ = ["lock", "has_lock", "lock_named", "has_named_lock"]
