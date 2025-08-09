from typing import List, Optional

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