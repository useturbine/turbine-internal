from abc import abstractmethod
from typing import Iterator, Tuple, Optional
from datetime import datetime


class DataSource:
    @abstractmethod
    def get_documents(
        self, updated_since: Optional[datetime] = None
    ) -> Iterator[Tuple[str, str]]:
        """Retrieve documents from the data source."""
        pass
