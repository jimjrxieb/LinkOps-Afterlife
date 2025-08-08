import sqlite3
import jwt
import os
from datetime import datetime, timedelta
from passlib.context import CryptContext
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT configuration
SECRET_KEY = os.getenv("SECRET_KEY", "your-default-secret-key-change-this")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

class AuthManager:
    def __init__(self, db_path: str = "/app/db/users.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        """Initialize the user database."""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                interactions_count INTEGER DEFAULT 0,
                daily_limit INTEGER DEFAULT 10,
                last_interaction TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS consent_records (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                session_id TEXT NOT NULL,
                consent_given BOOLEAN DEFAULT 0,
                consent_timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                consent_data TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        conn.commit()
        conn.close()
        
        logger.info("Database initialized successfully")
    
    def hash_password(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def create_user(self, username: str, password: str, email: Optional[str] = None) -> dict:
        """Create a new user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
            if cursor.fetchone():
                raise ValueError("Username already exists")
            
            if email:
                cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
                if cursor.fetchone():
                    raise ValueError("Email already exists")
            
            # Hash password and create user
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            
            user_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            logger.info(f"User created successfully: {username}")
            return {
                "id": user_id,
                "username": username,
                "email": email,
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            raise
    
    def authenticate_user(self, username: str, password: str) -> Optional[dict]:
        """Authenticate a user with username and password."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "SELECT id, username, email, password_hash, is_active FROM users WHERE username = ?",
                (username,)
            )
            user = cursor.fetchone()
            
            if not user or not user[4]:  # Check if user exists and is active
                return None
            
            if not self.verify_password(password, user[3]):
                return None
            
            # Update last login
            cursor.execute(
                "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?",
                (user[0],)
            )
            conn.commit()
            conn.close()
            
            return {
                "id": user[0],
                "username": user[1],
                "email": user[2]
            }
            
        except Exception as e:
            logger.error(f"Error authenticating user: {str(e)}")
            return None
    
    def create_access_token(self, user_data: dict) -> str:
        """Create a JWT access token."""
        to_encode = user_data.copy()
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
        to_encode.update({"exp": expire})
        
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    def verify_token(self, token: str) -> Optional[dict]:
        """Verify and decode a JWT token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning("Token has expired")
            return None
        except jwt.JWTError:
            logger.warning("Invalid token")
            return None
    
    def create_user_session(self, user_id: int, session_id: str) -> bool:
        """Create a new user session record."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                "INSERT INTO user_sessions (user_id, session_id) VALUES (?, ?)",
                (user_id, session_id)
            )
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error creating user session: {str(e)}")
            return False
    
    def check_usage_limits(self, user_id: int, session_id: str) -> dict:
        """Check if user has exceeded daily usage limits."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get today's interaction count
            cursor.execute("""
                SELECT interactions_count, daily_limit 
                FROM user_sessions 
                WHERE user_id = ? AND session_id = ?
                AND date(created_at) = date('now')
            """, (user_id, session_id))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                return {"allowed": True, "remaining": 10, "limit": 10}
            
            interactions_count, daily_limit = result
            remaining = max(0, daily_limit - interactions_count)
            
            return {
                "allowed": interactions_count < daily_limit,
                "remaining": remaining,
                "limit": daily_limit,
                "used": interactions_count
            }
            
        except Exception as e:
            logger.error(f"Error checking usage limits: {str(e)}")
            return {"allowed": False, "remaining": 0, "limit": 10}
    
    def increment_usage(self, user_id: int, session_id: str) -> bool:
        """Increment usage count for a user session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE user_sessions 
                SET interactions_count = interactions_count + 1,
                    last_interaction = CURRENT_TIMESTAMP
                WHERE user_id = ? AND session_id = ?
                AND date(created_at) = date('now')
            """, (user_id, session_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            logger.error(f"Error incrementing usage: {str(e)}")
            return False
    
    def store_consent(self, user_id: int, session_id: str, consent_data: dict) -> bool:
        """Store user consent information."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO consent_records (user_id, session_id, consent_given, consent_data)
                VALUES (?, ?, ?, ?)
            """, (user_id, session_id, True, str(consent_data)))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Consent stored for user {user_id}, session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error storing consent: {str(e)}")
            return False
    
    def check_consent(self, user_id: int, session_id: str) -> bool:
        """Check if user has given consent for a session."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT consent_given FROM consent_records 
                WHERE user_id = ? AND session_id = ?
                ORDER BY consent_timestamp DESC LIMIT 1
            """, (user_id, session_id))
            
            result = cursor.fetchone()
            conn.close()
            
            return result and result[0]
            
        except Exception as e:
            logger.error(f"Error checking consent: {str(e)}")
            return False
    
    def get_user_sessions(self, user_id: int) -> list:
        """Get all sessions for a user."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT session_id, created_at, interactions_count, last_interaction
                FROM user_sessions 
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            
            sessions = cursor.fetchall()
            conn.close()
            
            return [
                {
                    "session_id": session[0],
                    "created_at": session[1],
                    "interactions_count": session[2],
                    "last_interaction": session[3]
                }
                for session in sessions
            ]
            
        except Exception as e:
            logger.error(f"Error getting user sessions: {str(e)}")
            return []