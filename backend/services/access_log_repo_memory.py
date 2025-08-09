from ..interfaces.access_log_repo import IAccessLogRepository
from typing import List, Optional
from ..models.access_log import AccessLog
import pymysql
class MySQLAccessLogRepository(IAccessLogRepository):
    def __init__(self):
        self.conn = pymysql.connect(
            host="mysql",
            port=3306,
            user="admin_api",
            password="admin123",
            database="access_control",
            cursorclass=pymysql.cursors.DictCursor
        )
        self._create_table()

    def _create_table(self):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS access_logs (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id VARCHAR(255),
                    timestamp DATETIME,
                    status VARCHAR(50),
                    image LONGBLOB
                )
            """)
        self.conn.commit()

    def add_log(self, log: AccessLog):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO access_logs (user_id, timestamp, status, image)
                VALUES (%s, %s, %s, %s)
            """, (log.user_id, log.timestamp, log.status, log.image))
        self.conn.commit()

    def get_logs(self, user_id: Optional[str] = None) -> List[AccessLog]:
        with self.conn.cursor() as cursor:
            if user_id:
                cursor.execute("SELECT * FROM access_logs WHERE user_id=%s", (user_id,))
            else:
                cursor.execute("SELECT * FROM access_logs")
            rows = cursor.fetchall()
            return [AccessLog(
                user_id=row["user_id"],
                timestamp=row["timestamp"],
                status=row["status"],
                image=row["image"]
            ) for row in rows]