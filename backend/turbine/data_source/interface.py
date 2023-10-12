from abc import abstractmethod
from typing import Optional
from pydantic import BaseModel
from typing import Any


class DataSourceDocument(BaseModel):
    text: str
    metadata: Optional[dict[str, Any]] = None


class DataSource:
    @abstractmethod
    def get_documents(self) -> list[DataSourceDocument]:
        ...
