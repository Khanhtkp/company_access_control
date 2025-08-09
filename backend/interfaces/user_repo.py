from abc import ABC, abstractmethod
from typing import List, Optional
from ..models.user import User
class IUserRepository(ABC):
    @abstractmethod
    def add_user(self, user: User): pass

    @abstractmethod
    def update_user(self, user: User): pass

    @abstractmethod
    def delete_user(self, user_id: str): pass

    @abstractmethod
    def get_user(self, user_id: str) -> Optional[User]: pass

    @abstractmethod
    def get_all_users(self) -> List[User]: pass