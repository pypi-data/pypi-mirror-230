from pathlib import Path, PurePosixPath, PureWindowsPath, WindowsPath
import logging


class Store:
    """Object to handle different paths to a store amongst computers
    """
    def __init__(self, local_path: str=None, win_path: str = None, unix_path: str = None):
        """Initialize Store object

        Args:
            local_path (str, optional): Path to the store on the local computer. If not provided, it is supposed to be
            the same as either `win_runner_path` or `unix_runner_path` based on the OS.
            Defaults to None.
            win_path (str, optional): Path to the store on the windows runner computers. Defaults to None.
            unix_path (str, optional): Path to the store on the unix runner computers. Defaults to None.
        """
        if not local_path:
            if isinstance(Path("a"), WindowsPath):
                local_path = win_path
            else:
                local_path = unix_path

        self._local_path = Path(local_path).resolve()  # resolve mount point in case of windows mount
        self._win_path = PureWindowsPath(win_path) if win_path is not None else None
        self._unix_path = PurePosixPath(unix_path) if unix_path is not None else None

    def to_unix(self, dir: str | Path) -> PurePosixPath | None:
        if dir == "":
            return None
        if self._unix_path is None:
            raise ValueError("Trying to get Unix path from store which has unix_path not set")

        dir_path = Path(dir).resolve()
        if dir_path.is_relative_to(self._local_path):
            relative_path = dir_path.relative_to(self._local_path)
            out_path = self._unix_path / PurePosixPath(relative_path)
        else:
            logging.warning(f"Path {dir_path} has not been detected as relative to store path ({self._local_path})")
            out_path = PurePosixPath(dir_path)

        return out_path

    def to_win(self, dir: str | Path) -> PureWindowsPath | None:
        if dir == "":
            return None
        if self._win_path is None:
            raise ValueError("Trying to get Windows path from store which has win_path not set")

        dir_path = Path(dir).resolve()
        if dir_path.is_relative_to(self._local_path):
            relative_path = dir_path.relative_to(self._local_path)
            out_path = self._win_path / PureWindowsPath(relative_path)
        else:
            logging.warning(f"Path {dir_path} has not been detected as relative to store path ({self._local_path})")
            out_path = PureWindowsPath(dir_path)

        return out_path
