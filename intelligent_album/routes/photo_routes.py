from flask import Blueprint, request, jsonify
from models.photo import Photo
from models.album import Album
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from retrieval_model.retrieval import RetrievalModel
from config.database import execute_query
import requests
import random
import json
from hashlib import md5

appid = '20250419002337307'
appkey = 'w1cCl8NKAPl9JWsLgWIP'

photo_bp = Blueprint('photo', __name__)

# 配置上传文件存储路径
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                             'uploads')  # 此处生成的路径为/intelligent_album/uploads
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 定义检索模型！！
# todo:希望这是一个全局变量，在每个用户登录时初始化
# 测试能不能正常使用。模型加载路径在audoDL服务器上
# retrieval_model = RetrievalModel(
#     quantized=True,
#     use_bitblas=False
# )
retrieval_model = RetrievalModel(
    quantized=False,
    use_bitblas=False
)


def allowed_file(filename):
    """
    检查文件扩展名是否允许
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def chinese_to_english(text):
    from_lang = 'zh'
    to_lang = 'en'
    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + text + str(salt) + appkey)

    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'appid': appid,
        'q': text,
        'from': from_lang,
        'to': to_lang,
        'salt': salt,
        'sign': sign
    }

    try:
        r = requests.post(url, params=payload, headers=headers)
        result = r.json()
        if 'trans_result' in result:
            return '\n'.join([item['dst'] for item in result['trans_result']])
        return f"Error: {result.get('error_msg', 'Unknown error')}"
    except Exception as e:
        return f"Request failed: {str(e)}"


@photo_bp.route('/upload', methods=['POST'])
def upload_photo():
    """
    上传照片 -- 模型版
    ---
    表单参数:
      - photo: 照片文件
      - user_id: 用户ID
      - album_id: 图集ID（可选）
      - text: 照片描述（可选）
    """
    print("开始处理上传请求...")
    print(f"请求表单数据: {request.form}")
    print(f"请求文件: {request.files}")

    if 'photo' not in request.files:
        print("错误: 没有找到'photo'文件")
        return jsonify({
            'success': False,
            'message': '没有提供照片文件'
        }), 400

    file = request.files['photo']

    if file.filename == '':
        print("错误: 文件名为空")
        return jsonify({
            'success': False,
            'message': '没有选择文件'
        }), 400

    if not allowed_file(file.filename):
        print(f"错误: 不支持的文件类型 {file.filename}")
        return jsonify({
            'success': False,
            'message': '不支持的文件类型'
        }), 400

    user_id = request.form.get('user_id')
    if not user_id:
        print("错误: 没有提供用户ID")
        return jsonify({
            'success': False,
            'message': '请提供用户ID'
        }), 400

    print(f"处理用户 {user_id} 的上传请求")

    # 生成安全的文件名
    filename = secure_filename(file.filename)
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    new_filename = f"{timestamp}_{filename}"

    # 确定用户目录
    user_folder = os.path.join(UPLOAD_FOLDER, str(user_id))  # 创建用户目录: /intelligent_album/uploads/user_id
    os.makedirs(user_folder, exist_ok=True)

    # 保存文件
    file_path = os.path.join(user_folder, new_filename)
    file.save(file_path)
    print(f"文件保存到: {file_path}")

    # 检索模型添加索引
    # text = request.form.get('text', '')
    # print(text)
    text = ''
    retrieval_model.add_image(user_id=user_id, new_image_path=file_path)
    print(retrieval_model.get_all_image_annotation_pairs(user_id=user_id))
    # 相对路径，用于存储在数据库中
    relative_path = f"uploads/{user_id}/{new_filename}"  # 数据库中的路径格式是：uploads/user_id/filename

    # 获取其他参数
    album_id = request.form.get('album_id')
    status = request.form.get('status', 0)  # 获取status参数，默认为0（正常状态）

    try:
        # 确保status是整数
        status = int(status)
        # 验证status值的合法性
        if status not in [0, 1, 2]:
            print(f"警告: 无效的status值 {status}，默认使用0")
            status = 0
    except ValueError:
        print(f"警告: 无法将status转换为整数，使用默认值0")
        status = 0

    print(f"将照片保存到数据库: address={relative_path}, user_id={user_id}, album_id={album_id}, status={status}")

    # 保存到数据库 -- 调用Photo类的create函数
    result = Photo.create(
        address=relative_path,
        user_id=user_id,
        text=text,
        album_id=album_id,
        status=status  # 使用接收到的status或默认值
    )

    if result['success']:
        # 如果是第一张照片，并且有图集ID，则设置为图集封面
        if album_id:
            album = Album.find_by_id(album_id)
            if album and not album['cover_url']:
                Album.update_cover(album_id, relative_path)

        print(f"上传成功: photo_id={result['photo_id']}")
        response = {
            'success': True,
            'message': '照片上传成功',
            'photo_id': result['photo_id'],
            'photo_url': relative_path
        }
        print(f"返回响应: {response}")
        return jsonify(response), 201
    else:
        print(f"上传失败: {result['message']}")
        return jsonify({
            'success': False,
            'message': result['message']
        }), 400


@photo_bp.route('/<int:photo_id>', methods=['GET'])
def get_photo(photo_id):
    """
    获取照片信息
    ---
    路径参数:
      - photo_id: 照片ID
    """
    photo = Photo.find_by_id(photo_id)

    if photo:
        return jsonify({
            'success': True,
            'photo': photo
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '照片不存在'
        }), 404


@photo_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_photos(user_id):
    """
    获取用户的所有正常照片（不包括回收站的照片）
    ---
    路径参数:
      - user_id: 用户ID
    查询参数:
      - limit: 限制返回数量
      - offset: 偏移量（分页）
    """
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    photos = Photo.find_by_user(user_id, limit, offset)

    return jsonify({
        'success': True,
        'photos': photos
    }), 200


@photo_bp.route('/recent/<int:user_id>', methods=['GET'])
def get_recent_photos(user_id):
    """
    获取用户最近上传的照片
    ---
    路径参数:
      - user_id: 用户ID
    查询参数:
      - limit: 限制返回数量
    """
    limit = request.args.get('limit', 20, type=int)

    photos = Photo.get_recent(user_id, limit)

    return jsonify({
        'success': True,
        'photos': photos
    }), 200


@photo_bp.route('/trash/<int:user_id>', methods=['GET'])
def get_trash_photos(user_id):
    """
    获取用户回收站中的照片
    ---
    路径参数:
      - user_id: 用户ID
    查询参数:
      - limit: 限制返回数量
      - offset: 偏移量（分页）
    """
    print(f"获取用户 {user_id} 的回收站照片")
    limit = request.args.get('limit', type=int)
    offset = request.args.get('offset', type=int)

    # 调用模型方法获取回收站照片
    photos = Photo.find_in_trash(user_id, limit, offset)

    # 添加调试信息
    print(f"查询到 {len(photos)} 张回收站照片")
    if photos:
        # 检查是否有状态不为 1 的照片
        wrong_status_photos = [p for p in photos if p.get('status') != 1]
        if wrong_status_photos:
            print(f"警告: 发现 {len(wrong_status_photos)} 张状态不为 1 的照片在回收站中!")
            for p in wrong_status_photos:
                print(f"  - 照片ID: {p.get('id')}, 状态: {p.get('status')}")

    # 确保只返回状态为 1 的照片（双重检查）
    photos = [p for p in photos if p.get('status') == 1]
    print(f"过滤后返回 {len(photos)} 张回收站照片")

    return jsonify({
        'success': True,
        'photos': photos
    }), 200


@photo_bp.route('/<int:photo_id>', methods=['PUT'])
def update_photo(photo_id):
    """
    更新照片的文本/图集信息
    ---
    路径参数:
      - photo_id: 照片ID
    请求参数:
      - text: 照片描述（可选）
      - album_id: 图集ID（可选）
    """
    photo = Photo.find_by_id(photo_id)

    if not photo:
        return jsonify({
            'success': False,
            'message': '照片不存在'
        }), 404

    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'message': '请提供要更新的数据'
        }), 400

    text = data.get('text')
    album_id = data.get('album_id')

    result = Photo.update(photo_id, text, album_id)

    if result['success']:
        return jsonify({
            'success': True,
            'message': '照片信息更新成功'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 400


@photo_bp.route('/<int:photo_id>/status', methods=['PUT'])
def update_photo_status(photo_id):
    """
    更新照片状态（移动到回收站或从回收站恢复）
    ---
    路径参数:
      - photo_id: 照片ID
    请求参数:
      - status: 照片状态（0:正常, 1:回收站）
    """
    photo = Photo.find_by_id(photo_id)

    if not photo:
        return jsonify({
            'success': False,
            'message': '照片不存在'
        }), 404

    data = request.get_json()

    if not data or 'status' not in data:
        return jsonify({
            'success': False,
            'message': '请提供照片状态'
        }), 400

    status = data['status']

    if status not in [0, 1]:
        return jsonify({
            'success': False,
            'message': '状态值无效，请使用 0(正常) 或 1(回收站)'
        }), 400

    result = Photo.update_status(photo_id, status)

    if result['success']:
        return jsonify({
            'success': True,
            'message': '照片状态更新成功'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '照片状态更新失败'
        }), 500


@photo_bp.route('/<int:photo_id>', methods=['DELETE'])
def delete_photo(photo_id):
    """
    永久删除照片 -- 模型版
    ---
    路径参数:
      - photo_id: 照片ID
    """
    photo = Photo.find_by_id(photo_id)

    if not photo:
        return jsonify({
            'success': False,
            'message': '照片不存在'
        }), 404

    # 删除文件
    try:
        # 从图片相对路径构建绝对路径
        file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), photo['address'])
        if os.path.exists(file_path):
            os.remove(file_path)

        # 模型索引文件删除该图片
        retrieval_model.delete_image(user_id=photo['user_id'], image_path=file_path)
        print(retrieval_model.get_all_image_annotation_pairs(photo['user_id']))
    except Exception as e:
        print(f"删除文件错误: {e}")

    # 从数据库中删除记录
    result = Photo.delete(photo_id)

    if result['success']:
        return jsonify({
            'success': True,
            'message': '照片删除成功'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '照片删除失败'
        }), 500


@photo_bp.route('/search/<int:user_id>', methods=['GET'])
def search_photos(user_id):
    """
    搜索照片 -- 模型版
    ---
    路径参数:
      - user_id: 用户ID
    查询参数:
      - keyword: 搜索查询语句
      - view: 当前视图（"all", "trash", "recent"）

    修改此函数为检索模型版本
    """
    query = request.args.get('keyword', '')
    en_query = chinese_to_english(query)
    view = request.args.get('view', 'all')  # 默认为"all"视图

    if not query:
        return jsonify({
            'success': False,
            'message': '请提供查询语句'
        }), 400

    # 第一步：模型检索，返回检索结果列表
    model_results = retrieval_model.query(user_id=user_id,
                                          text_input=en_query)  # model_results是一个列表，列表中每个元素是一个元组，元组第一个元素是图片绝对路径
    # print(model_results)
    if type(model_results) is list:
        # 第二步：mysql筛选，从检索结果列表中筛选mysql中符合条件的记录
        base_path = os.path.dirname(os.path.dirname(__file__))
        photos = []  # 最终检索结果。是一个列表，列表中每个元素是一个字典，也就是数据库的一条记录
        bucket = {}
        for item in model_results:
            file_path = item[0]  # 获取元组的第一个元素
            # 获取相对路径
            rel_path = os.path.relpath(file_path, base_path)
            print("rel_path:", rel_path)
            # 根据视图类型搜索不同状态的照片
            if view == 'trash':
                # 在回收站中搜索（status=1）
                db_results = Photo.search_in_trash(user_id, rel_path)
            elif view == 'recent':
                # 搜索最近的照片（status=0，一周内）
                db_results = Photo.search_recent(user_id, rel_path)
            else:
                # 默认搜索正常照片（status=0）
                db_results = Photo.search(user_id, rel_path)

            # print(db_results)
            # 将记录加入最终检索结果
            for record in db_results:
                if bucket.get(record['id']) is None:
                    bucket[record['id']] = record
                    photos.append(record)

        return jsonify({
            'success': True,
            'photos': photos,
            'count': len(photos)
        }), 200
    else:
        return jsonify({
            'success': False,
            'type': str(type(model_results)),
            'message': '模型检索结果类型有误'
        }), 200


@photo_bp.route('/move/<int:photo_id>', methods=['PUT'])
def move_to_album(photo_id):
    """
    将照片移动到指定图集
    ---
    路径参数:
      - photo_id: 照片ID
    请求参数:
      - album_id: 图集ID
    """
    photo = Photo.find_by_id(photo_id)

    if not photo:
        return jsonify({
            'success': False,
            'message': '照片不存在'
        }), 404

    data = request.get_json()

    if not data or 'album_id' not in data:
        return jsonify({
            'success': False,
            'message': '请提供图集ID'
        }), 400

    album_id = data['album_id']

    # 验证图集是否存在
    if album_id is not None and not Album.find_by_id(album_id):
        return jsonify({
            'success': False,
            'message': '图集不存在'
        }), 404

    result = Photo.move_to_album(photo_id, album_id)

    if result['success']:
        # 如果图集没有封面，则设置此照片为封面
        if album_id:
            album = Album.find_by_id(album_id)
            if album and not album['cover_url']:
                Album.update_cover(album_id, photo['address'])

        return jsonify({
            'success': True,
            'message': '照片已移动到指定图集'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '移动照片失败'
        }), 500
