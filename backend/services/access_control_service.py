from ..interfaces.access_control import IAccessControlService
from typing import List, Optional
from ..models.user import AccessRule
import pymysql
import json
class MySQLAccessControlService(IAccessControlService):
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
                CREATE TABLE IF NOT EXISTS access_rules (
                    user_id VARCHAR(255),
                    area VARCHAR(255),
                    allowed_hours JSON,
                    PRIMARY KEY (user_id, area)
                )
            """)
        self.conn.commit()

    def grant_access(self, rule: AccessRule):
        with self.conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO access_rules (user_id, area, allowed_hours)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE allowed_hours = VALUES(allowed_hours)
            """, (rule.user_id, rule.area, json.dumps(rule.allowed_hours)))
        self.conn.commit()

    def revoke_access(self, user_id: str, area: str):
        with self.conn.cursor() as cursor:
            cursor.execute("DELETE FROM access_rules WHERE user_id=%s AND area=%s", (user_id, area))
        self.conn.commit()

    def get_rules(self, user_id: Optional[str] = None) -> List[AccessRule]:
        with self.conn.cursor() as cursor:
            if user_id:
                cursor.execute("SELECT * FROM access_rules WHERE user_id=%s", (user_id,))
            else:
                cursor.execute("SELECT * FROM access_rules")
            rows = cursor.fetchall()
        return [AccessRule(r['user_id'], r['area'], json.loads(r['allowed_hours'])) for r in rows]
