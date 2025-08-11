from ..models.access_log import AccessLog
from abc import ABC, abstractmethod
from typing import List, Optional
class IAccessLogRepository(ABC):
    @abstractmethod
    def add_log(self, log: AccessLog): pass

    @abstractmethod
    def get_logs(self, user_id: Optional[str] = None) -> List[AccessLog]: pass