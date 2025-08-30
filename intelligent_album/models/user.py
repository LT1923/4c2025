from config.database import execute_query
import hashlib
import uuid
import re

class User:
    def __init__(self, id=None, phone=None, password=None, created_at=None):
        self.id = id
        self.phone = phone
        self.password = password
        self.created_at = created_at
    
    @staticmethod
    def hash_password(password):
        """
        对密码进行哈希处理
        """
        salt = uuid.uuid4().hex
        hashed_password = hashlib.sha256(salt.encode() + password.encode()).hexdigest()
        return f"{salt}${hashed_password}"
    
    @staticmethod
    def verify_password(stored_password, provided_password):
        """
        验证密码
        """
        salt, hashed_password = stored_password.split('$')
        calculated_hash = hashlib.sha256(salt.encode() + provided_password.encode()).hexdigest()
        return calculated_hash == hashed_password
    
    @staticmethod
    def validate_phone(phone):
        """
        验证手机号格式
        """
        pattern = r'^1[3-9]\d{9}$'  # 中国手机号格式
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def create(phone, password):
        """
        创建新用户
        """
        if not User.validate_phone(phone):
            return {"success": False, "message": "手机号格式不正确"}
        
        # 检查手机号是否已存在
        existing_user = User.find_by_phone(phone)
        if existing_user:
            return {"success": False, "message": "该手机号已注册"}
        
        hashed_password = User.hash_password(password)
        query = "INSERT INTO users (phone, password) VALUES (%s, %s)"
        params = (phone, hashed_password)
        
        user_id = execute_query(query, params)
        if user_id:
            return {"success": True, "user_id": user_id}
        else:
            return {"success": False, "message": "用户创建失败"}
    
    @staticmethod
    def login(phone, password):
        """
        用户登录
        """
        user = User.find_by_phone(phone)
        if not user:
            return {"success": False, "message": "用户不存在"}
        
        if User.verify_password(user['password'], password):
            # 不返回密码
            user.pop('password', None)
            return {"success": True, "user": user}
        else:
            return {"success": False, "message": "密码错误"}
    
    @staticmethod
    def find_by_id(user_id):
        """
        通过ID查找用户
        """
        query = "SELECT * FROM users WHERE id = %s"
        params = (user_id,)
        users = execute_query(query, params, fetch=True)
        
        if users and len(users) > 0:
            return users[0]
        return None
    
    @staticmethod
    def find_by_phone(phone):
        """
        通过手机号查找用户
        """
        query = "SELECT * FROM users WHERE phone = %s"
        params = (phone,)
        users = execute_query(query, params, fetch=True)
        
        if users and len(users) > 0:
            return users[0]
        return None 