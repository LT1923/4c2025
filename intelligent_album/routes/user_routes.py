from flask import Blueprint, request, jsonify
from models.user import User

user_bp = Blueprint('user', __name__)

@user_bp.route('/register', methods=['POST'])
def register():
    """
    用户注册
    ---
    请求参数:
      - phone: 手机号
      - password: 密码
    """
    data = request.get_json()
    
    if not data or 'phone' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': '请提供手机号和密码'
        }), 400
    
    phone = data['phone']
    password = data['password']
    
    # 验证手机号格式
    if not User.validate_phone(phone):
        return jsonify({
            'success': False,
            'message': '手机号格式不正确'
        }), 400
    
    # 验证密码长度
    if len(password) < 6:
        return jsonify({
            'success': False,
            'message': '密码长度不能少于6位'
        }), 400
    
    result = User.create(phone, password)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': '注册成功',
            'user_id': result['user_id']
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 400

@user_bp.route('/login', methods=['POST'])
def login():
    """
    用户登录
    ---
    请求参数:
      - phone: 手机号
      - password: 密码
    """
    data = request.get_json()
    
    if not data or 'phone' not in data or 'password' not in data:
        return jsonify({
            'success': False,
            'message': '请提供手机号和密码'
        }), 400
    
    phone = data['phone']
    password = data['password']
    
    result = User.login(phone, password)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': '登录成功',
            'user': result['user']
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 401

@user_bp.route('/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """
    获取用户信息
    ---
    路径参数:
      - user_id: 用户ID
    """
    user = User.find_by_id(user_id)
    
    if user:
        # 不返回密码
        user.pop('password', None)
        return jsonify({
            'success': True,
            'user': user
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '用户不存在'
        }), 404 