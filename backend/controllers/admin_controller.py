from ..interfaces.access_control import IAccessControlService
from ..interfaces.access_log_repo import IAccessLogRepository
from ..interfaces.face_recognition import IFaceRecognitionService
from ..interfaces.user_repo import IUserRepository
from ..models.user import User, AccessRule
from ..models.access_log import AccessLog
from typing import Optional, List
import datetime
class AdminController:
    def __init__(self, user_repo: IUserRepository, log_repo: IAccessLogRepository,
                 access_service: IAccessControlService, face_service: IFaceRecognitionService):
        self.user_repo = user_repo
        self.log_repo = log_repo
        self.access_service = access_service
        self.face_service = face_service

    def add_user(self, user_data: dict):
        user = User(**user_data)
        self.user_repo.add_user(user)

    def edit_user(self, user_data: dict):
        user = User(**user_data)
        self.user_repo.update_user(user)

    def delete_user(self, user_id: str):
        self.user_repo.delete_user(user_id)

    def get_user(self, user_id: str) -> Optional[dict]:
        user = self.user_repo.get_user(user_id)
        return user.to_dict() if user else None

    def list_users(self) -> List[dict]:
        return [u.to_dict() for u in self.user_repo.get_all_users()]

    def grant_access(self, rule_data: dict):
        rule = AccessRule(**rule_data)
        self.access_service.grant_access(rule)

    def revoke_access(self, user_id: str, area: str):
        self.access_service.revoke_access(user_id, area)

    def get_access_rules(self, user_id: Optional[str] = None) -> List[dict]:
        return [r.to_dict() for r in self.access_service.get_rules(user_id)]

    def verify_and_log_access(self, face_img: bytes):
        user_id = self.face_service.verify_face(face_img)
        now = datetime.datetime.now()
        status = "granted" if user_id else "denied"
        self.log_repo.add_log(AccessLog(user_id, now, status, face_img))
        return status

    def get_user_logs(self, user_id: Optional[str] = None) -> List[dict]:
        return [l.to_dict() for l in self.log_repo.get_logs(user_id)]
