from abc import ABC, abstractmethod
from typing import List, Dict, Optional
import datetime
import cv2
import numpy as np
from insightface.app import FaceAnalysis


class User:
    def __init__(self, user_id: str, name: str, department: str, role: str, email: str, phone: str, face_data: Optional[bytes] = None):
        self.user_id = user_id
        self.name = name
        self.department = department
        self.role = role
        self.email = email
        self.phone = phone
        self.face_data = face_data

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "name": self.name,
            "department": self.department,
            "role": self.role,
            "email": self.email,
            "phone": self.phone,
        }

class AccessLog:
    def __init__(self, user_id: str, timestamp: datetime.datetime, status: str, image: Optional[bytes] = None):
        self.user_id = user_id
        self.timestamp = timestamp
        self.status = status
        self.image = image

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "timestamp": self.timestamp.isoformat(),
            "status": self.status,
        }

class AccessRule:
    def __init__(self, user_id: str, area: str, allowed_hours: List[str]):
        self.user_id = user_id
        self.area = area
        self.allowed_hours = allowed_hours

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "area": self.area,
            "allowed_hours": self.allowed_hours
        }

# --- Interfaces (for backend adapters) ---

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

class IAccessLogRepository(ABC):
    @abstractmethod
    def add_log(self, log: AccessLog): pass

    @abstractmethod
    def get_logs(self, user_id: Optional[str] = None) -> List[AccessLog]: pass

class IAccessControlService(ABC):
    @abstractmethod
    def grant_access(self, rule: AccessRule): pass

    @abstractmethod
    def revoke_access(self, user_id: str, area: str): pass

    @abstractmethod
    def get_rules(self, user_id: Optional[str] = None) -> List[AccessRule]: pass

class IFaceRecognitionService(ABC):
    @abstractmethod
    def train_model(self): pass

    @abstractmethod
    def verify_face(self, face_image: bytes) -> str: pass

# --- In-Memory Implementations for Local Testing ---

class InMemoryUserRepository(IUserRepository):
    def __init__(self):
        self.users: Dict[str, User] = {}

    def add_user(self, user: User):
        self.users[user.user_id] = user

    def update_user(self, user: User):
        self.users[user.user_id] = user

    def delete_user(self, user_id: str):
        self.users.pop(user_id, None)

    def get_user(self, user_id: str) -> Optional[User]:
        return self.users.get(user_id)

    def get_all_users(self) -> List[User]:
        return list(self.users.values())

class InMemoryAccessLogRepository(IAccessLogRepository):
    def __init__(self):
        self.logs: List[AccessLog] = []

    def add_log(self, log: AccessLog):
        self.logs.append(log)

    def get_logs(self, user_id: Optional[str] = None) -> List[AccessLog]:
        if user_id:
            return [log for log in self.logs if log.user_id == user_id]
        return self.logs

class SimpleAccessControlService(IAccessControlService):
    def __init__(self):
        self.rules: List[AccessRule] = []

    def grant_access(self, rule: AccessRule):
        self.rules.append(rule)

    def revoke_access(self, user_id: str, area: str):
        self.rules = [r for r in self.rules if not (r.user_id == user_id and r.area == area)]

    def get_rules(self, user_id: Optional[str] = None) -> List[AccessRule]:
        if user_id:
            return [r for r in self.rules if r.user_id == user_id]
        return self.rules

class InsightFaceRecognitionService(IFaceRecognitionService):
    def __init__(self, known_embeddings: List[np.ndarray], student_ids: List[str]):
        self.app = FaceAnalysis(providers=['CPUExecutionProvider'])
        self.app.prepare(ctx_id=0)
        self.known_embeddings = known_embeddings
        self.student_ids = student_ids

    def cosine_similarity(self, emb1: np.ndarray, emb2: np.ndarray) -> float:
        return np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))

    def train_model(self):
        print("InsightFace does not require training here.")

    def verify_face(self, face_image: bytes) -> str:
        frame = cv2.imdecode(np.frombuffer(face_image, np.uint8), cv2.IMREAD_COLOR)
        faces = self.app.get(frame)
        best_similarity = -1
        label = "Unknown"

        for face in faces:
            embedding = face.embedding
            for i in range(len(self.known_embeddings)):
                similarity = self.cosine_similarity(embedding, self.known_embeddings[i])
                if similarity > best_similarity:
                    best_similarity = similarity
                    best_match_name = self.student_ids[i]

            if best_similarity > 0.4:
                label = best_match_name

        return label if label != "Unknown" else ""

# --- Admin Controller Layer (for Frontend Interaction & REST API Backend) ---

