from pathlib import Path
import shutil


class FileSystem:
    """
    Cross-platform filesystem service.

    This class is responsible for actual filesystem operations.
    It uses pathlib and shutil so the same implementation can
    work across Linux, Windows, and macOS.

    Platform-specific restrictions, such as iOS sandboxing,
    can be handled by a future platform-specific implementation.
    """

    def __init__(self, root=None):
        """
        Initialize the filesystem service.

        Args:
            root:
                Optional root directory.

                If omitted, the user's home directory is used.
        """

        if root is None:
            root = Path.home()

        self.root = Path(root).expanduser().resolve()

    # =========================================================
    # PATH HANDLING
    # =========================================================

    def resolve(self, path=""):
        """
        Resolve a path relative to the filesystem root.

        Examples:

            "Documents/Homework"
            "~/Projects"
            "/home/user/Desktop"
            "notes.txt"
        """

        if path is None:
            path = ""

        path = str(path).strip()

        if not path:
            return self.root

        # Expand "~"
        path = Path(path).expanduser()

        # Absolute path
        if path.is_absolute():
            return path.resolve()

        # Relative path
        return (self.root / path).resolve()

    # =========================================================
    # CREATE DIRECTORY
    # =========================================================

    def create_directory(self, path):
        """
        Create a directory and any missing parent directories.

        Returns:
            Path
        """

        directory = self.resolve(path)

        directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        return directory

    # =========================================================
    # CREATE FILE
    # =========================================================

    def create_file(self, path, content=""):
        """
        Create a file with optional text content.

        Parent directories are created automatically.

        Returns:
            Path
        """

        file_path = self.resolve(path)

        file_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        file_path.write_text(
            content,
            encoding="utf-8",
        )

        return file_path

    # =========================================================
    # READ FILE
    # =========================================================

    def read_file(self, path):
        """
        Read a UTF-8 text file.

        Returns:
            str
        """

        file_path = self.resolve(path)

        return file_path.read_text(
            encoding="utf-8",
        )

    # =========================================================
    # LIST DIRECTORY
    # =========================================================

    def list_directory(self, path=""):
        """
        List all files and directories inside a directory.

        Returns:
            list[Path]
        """

        directory = self.resolve(path)

        if not directory.exists():
            return []

        if not directory.is_dir():
            raise NotADirectoryError(
                f"Not a directory: {directory}"
            )

        return sorted(
            directory.iterdir(),
            key=lambda item: item.name.lower(),
        )

    # =========================================================
    # CHECK EXISTENCE
    # =========================================================

    def exists(self, path):
        """
        Check whether a path exists.

        Returns:
            bool
        """

        return self.resolve(path).exists()

    # =========================================================
    # DELETE
    # =========================================================

    def delete(self, path):
        """
        Delete a file or directory.

        Directories are deleted recursively.

        Returns:
            Path
        """

        target = self.resolve(path)

        if not target.exists():
            raise FileNotFoundError(
                f"Path does not exist: {target}"
            )

        if target.is_dir():
            shutil.rmtree(target)

        else:
            target.unlink()

        return target
