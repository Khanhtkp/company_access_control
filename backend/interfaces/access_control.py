from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.user import AccessRule
class IAccessControlService(ABC):
    @abstractmethod
    def grant_access(self, rule: AccessRule): pass

    @abstractmethod
    def revoke_access(self, user_id: str, area: str): pass

    @abstractmethod
    def get_rules(self, user_id: Optional[str] = None) -> List[AccessRule]: pass