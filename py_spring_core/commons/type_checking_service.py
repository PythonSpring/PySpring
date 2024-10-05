import subprocess
from typing import Optional
from loguru import logger


class TypeCheckingErrorr(Exception): ...

class TypeCheckingService:
    def __init__(self, target_folder: str) -> None:
        self.target_folder = target_folder
        self.checking_command = ['mypy', '--disallow-untyped-defs', self.target_folder]

    def type_checking(self) -> Optional[TypeCheckingErrorr]:
        logger.info("[MYPY TYPE CHECKING] Mypy checking types for projects...")
        # Run mypy and capture stdout and stderr
        result = subprocess.run(
            self.checking_command,
            capture_output=True,  # Captures both stdout and stderr
            text=True,            # Ensures output is returned as a string
            check=False           # Avoids raising an exception on non-zero exit code
        )
        SUCCESS = 0
        if result.returncode != SUCCESS:
            error_message = f"\n{result.stdout}"
            return TypeCheckingErrorr(error_message)
        logger.success(f"Mypy Type Checking Passed: {result.stdout}".strip())
        return None