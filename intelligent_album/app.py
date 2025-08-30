from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from config.database import db_init
from routes.user_routes import user_bp
from routes.album_routes import album_bp
from routes.photo_routes import photo_bp
import os

app = Flask(__name__)
# 配置跨域，允许所有源
# CORS(app, resources={r"/*": {"origins": "*"}})
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)  # 允许跨域并支持凭据（如 Cookie）
# CORS(app, resources={r"/*": {"origins": "http://127.0.0.1:3000", "supports_credentials": True}},
#      allow_headers=["Content-Type", "Authorization"], methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

# 配置静态文件目录
uploads_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
os.makedirs(uploads_dir, exist_ok=True)
app.config['UPLOAD_FOLDER'] = uploads_dir

# 注册蓝图
app.register_blueprint(user_bp, url_prefix='/api/users')
app.register_blueprint(album_bp, url_prefix='/api/albums')
app.register_blueprint(photo_bp, url_prefix='/api/photos')

# 初始化数据库
db_init()


@app.route('/')
def hello():
    return jsonify({"message": "欢迎使用相册API"})


# 提供静态文件访问
@app.route('/uploads/<path:filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# 提供静态文件访问 - 带用户ID的路径
@app.route('/uploads/<user_id>/<path:filename>')
def user_uploaded_file(user_id, filename):
    user_folder = os.path.join(app.config['UPLOAD_FOLDER'], user_id)
    return send_from_directory(user_folder, filename)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
    # app.run(debug=True, host='0.0.0.0', port=5001)
    # app.run(debug=True, host='0.0.0.0', port=3000)
