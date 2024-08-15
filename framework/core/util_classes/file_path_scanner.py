
import os
from typing import Iterable



class FilePathScanner:
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
                