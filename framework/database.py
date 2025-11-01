import sqlite3
from typing import Dict, Any, List, Optional

class Database:
    def __init__(self, db_file_path: str = 'database.db') -> None:
        self.db_file_path = db_file_path
        self._connection = None
        self._ensure_schema()

    def _get_connection(self) -> sqlite3.Connection:
        if self._connection is None:
            self._connection = sqlite3.connect(self.db_file_path, check_same_thread = False)
        return self._connection

    def _ensure_schema(self) -> None:
        with self._get_connection() as connection:
            connection.executescript('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    first_name TEXT,
                    last_name TEXT,
                    username TEXT,
                    is_premium INTEGER,
                    stars INTEGER,
                    stars_level INTEGER,
                    gifts_count INTEGER,
                    phone_country TEXT,
                    bio TEXT
                );

                CREATE TABLE IF NOT EXISTS countries (
                    code TEXT PRIMARY KEY
                );

                CREATE TABLE IF NOT EXISTS terms (
                    text TEXT PRIMARY KEY
                );

                CREATE TABLE IF NOT EXISTS settings (
                    allow_fonts INTEGER DEFAULT 0,
                    allow_font_percentage INTEGER DEFAULT 0,
                    allow_no_premium INTEGER DEFAULT 0,
                    should_check_channel INTEGER DEFAULT 0,
                    should_check_bio INTEGER DEFAULT 0
                );
            ''')

            cursor = connection.execute("SELECT COUNT(*) FROM settings")
            if cursor.fetchone()[0] == 0:
                connection.execute('''
                    INSERT INTO settings (
                        allow_fonts, allow_font_percentage, allow_no_premium, should_check_channel, should_check_bio
                    ) VALUES (0, 0, 0, 0, 0)
                ''')
                connection.commit()

    def add_country(self, code: str) -> None:
        with self._get_connection() as connection:
            connection.execute('''
                INSERT OR IGNORE INTO countries (code)
                VALUES (?)
            ''', (code,))
            connection.commit()
    
    def get_countries(self) -> list[dict]:
        with self._get_connection() as connection:
            rows = connection.execute('''
                SELECT code FROM countries
            ''').fetchall()
            return [{'code': row[0]} for row in rows]

    def remove_country(self, code: str) -> None:
        with self._get_connection() as connection:
            connection.execute('''
                DELETE FROM countries WHERE code = ?
            ''', (code,))
            connection.commit()

    def does_country_exist(self, code: str) -> bool:
        with self._get_connection() as connection:
            return connection.execute('''
                SELECT COUNT(*) FROM countries WHERE code = ?
            ''', (code,)).fetchone()[0] > 0
    
    def add_user(self, user_id: int, first_name: str, last_name: str, username: str, is_premium: bool, stars: int, stars_level: int, gifts_count: int, phone_country: str, bio: str) -> None:
        with self._get_connection() as connection:
            connection.execute('''
                INSERT OR REPLACE INTO users (id, first_name, last_name, username, is_premium, stars, stars_level, gifts_count, phone_country, bio)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, first_name, last_name, username, int(is_premium), stars, stars_level, gifts_count, phone_country, bio))
            connection.commit()
    
    def get_user(self, user_id: int) -> dict | None:
        with self._get_connection() as connection:
            row = connection.execute('''
                SELECT * FROM users WHERE id = ?
            ''', (user_id,)).fetchone()
            if row is None:
                return None
            columns = [column[1] for column in connection.execute('PRAGMA table_info(users)')]
            return dict(zip(columns, row))

    def add_term(self, text: str) -> None:
        with self._get_connection() as connection:
            connection.execute('''
                INSERT OR IGNORE INTO terms (text)
                VALUES (?)
            ''', (text,))
            connection.commit()
    
    def get_terms(self) -> list[str]:
        with self._get_connection() as connection:
            rows = connection.execute('''
                SELECT text FROM terms
            ''').fetchall()
            return [row[0] for row in rows]
    
    def remove_term(self, text: str) -> None:
        with self._get_connection() as connection:
            connection.execute('''
                DELETE FROM terms WHERE text = ?
            ''', (text,))
            connection.commit()
    
    def does_term_exist(self, text: str) -> bool:
        with self._get_connection() as connection:
            terms = self.get_terms()
            return text.lower() in [term.lower() for term in terms]

    def get_settings(self) -> Dict[str, Any]:
        with self._get_connection() as connection:
            row = connection.execute('''
                SELECT * FROM settings
            ''').fetchone()
            columns = [column[1] for column in connection.execute('PRAGMA table_info(settings)')]
            return dict(zip(columns, row))
    
    def edit_setting(self, key: str, value: Any) -> None:
        with self._get_connection() as connection:
            query = f'UPDATE settings SET {key} = ?'
            connection.execute(query, (value,))
            connection.commit()
