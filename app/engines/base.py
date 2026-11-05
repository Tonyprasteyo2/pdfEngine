from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional


class PDFEngine(ABC):
    name: str = "base"

    @abstractmethod
    def is_available(self) -> bool:
        ...

    @abstractmethod
    def merge(self, files: List[Path], output: Path) -> Path:
        ...

    @abstractmethod
    def validate(self, file: Path) -> bool:
        ...

    def normalize(self, file: Path, output: Path) -> Path:
        """Default: copy. Override in engines that support it."""
        import shutil
        shutil.copy2(file, output)
        return output

    def repair(self, file: Path, output: Path) -> Path:
        """Default: normalize. Override if needed."""
        return self.normalize(file, output)

    def get_page_count(self, file: Path) -> Optional[int]:
        return None

    def split(self, file: Path, output_dir: Path) -> List[Path]:
        raise NotImplementedError(f"{self.name} does not support split")

    def rotate(self, file: Path, output: Path, degrees: int = 90) -> Path:
        raise NotImplementedError(f"{self.name} does not support rotate")

    def compress(self, file: Path, output: Path) -> Path:
        raise NotImplementedError(f"{self.name} does not support compress")
