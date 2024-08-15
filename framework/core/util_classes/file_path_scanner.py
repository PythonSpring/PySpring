import os
from typing import Iterable


class FilePathScanner:
    """
    Scans a directory and its subdirectories for files with the specified target extensions, and returns a set of the full file paths.
    
    Args:
        target_dir (str): The directory to scan for files.
        target_extensions (Iterable[str]): The file extensions to search for.
    
    Returns:
        set[str]: A set of the full file paths for all files found with the target extensions.
    """
        
    def __init__(self, target_dir: str, target_extensions: Iterable[str]) -> None:
        self.target_dir = target_dir
        self.target_extensions = target_extensions

    def scan_file_paths_under_directory(self) -> set[str]:
        paths: set[str] = set()
        for root, _, files in os.walk(self.target_dir):
            for file in files:
                for extension in self.target_extensions:
                    if file.endswith(extension):
                        file_path: str = os.path.join(root, file)
                        paths.add(file_path)
                        break

        return paths
