from ..interfaces.user_repo import IUserRepository
from ..models.user import User
from typing import List, Optional
import pymysql
from insightface.app import FaceAnalysis
import cv2
import numpy as np
class MySQLUserRepository(IUserRepository):
    def __init__(self):
        self.conn = pymysql.connect(
            host="mysql",
            port = 3306,
            user="admin_api",
            password="admin123",
            database="access_control",
            cursorclass=pymysql.cursors.DictCursor
        )
        self._create_table()

    def _create_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id VARCHAR(255) PRIMARY KEY,
                    name VARCHAR(255),
                    department VARCHAR(255),
                    role VARCHAR(255),
                    email VARCHAR(255),
                    phone VARCHAR(255),
                    face_data LONGBLOB
                )
            """)
        self.conn.commit()

    def add_user(self, user: User):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO users (user_id, name, department, role, email, phone, face_data)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (user.user_id, user.name, user.department, user.role, user.email, user.phone, user.face_data))
        self.conn.commit()

    def update_user(self, user: User):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                UPDATE users SET name=%s, department=%s, role=%s, email=%s, phone=%s, face_data=%s
                WHERE user_id=%s
            """, (user.name, user.department, user.role, user.email, user.phone, user.face_data, user.user_id))
        self.conn.commit()

    def delete_user(self, user_id: str):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        self.conn.commit()

    def get_user(self, user_id: str) -> Optional[User]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
            row = cursor.fetchone()
            if row:
                return User(**row)
        return None

    def get_all_users(self) -> List[User]:
        with self.conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            rows = cursor.fetchall()
            return [User(**row) for row in rows]

    def load_known_faces(self, app: FaceAnalysis):
        users = self.get_all_users()
        known_embeddings, student_ids = [], []
        for user in users:
            if user.face_data:
                np_img = np.frombuffer(user.face_data, np.uint8)
                img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)
                faces = app.get(img)
                if faces:
                    known_embeddings.append(faces[0].embedding)
                    student_ids.append(user.user_id)
        return known_embeddings, student_ids