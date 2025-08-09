import datetime
from typing import Optional
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