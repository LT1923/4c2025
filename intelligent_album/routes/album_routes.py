from flask import Blueprint, request, jsonify
from models.album import Album
from models.photo import Photo

album_bp = Blueprint('album', __name__)

@album_bp.route('/create', methods=['POST'])
def create_album():
    """
    创建新图集
    ---
    请求参数:
      - name: 图集名称
      - content: 图集描述
      - user_id: 用户ID
      - cover_url: 封面图片URL（可选）
    """
    data = request.get_json()
    
    if not data or 'name' not in data or 'user_id' not in data:
        return jsonify({
            'success': False,
            'message': '请提供图集名称和用户ID'
        }), 400
    
    name = data['name']
    content = data.get('content', '')
    user_id = data['user_id']
    cover_url = data.get('cover_url')
    
    result = Album.create(name, content, user_id, cover_url)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': '图集创建成功',
            'album_id': result['album_id']
        }), 201
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 400

@album_bp.route('/<int:album_id>', methods=['GET'])
def get_album(album_id):
    """
    获取图集信息
    ---
    路径参数:
      - album_id: 图集ID
    """
    album = Album.find_by_id(album_id)
    
    if album:
        # 获取图集中的照片数量
        photo_count = Album.get_photo_count(album_id)
        album['photo_count'] = photo_count
        
        return jsonify({
            'success': True,
            'album': album
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '图集不存在'
        }), 404

@album_bp.route('/user/<int:user_id>', methods=['GET'])
def get_user_albums(user_id):
    """
    获取用户的所有图集
    ---
    路径参数:
      - user_id: 用户ID
    """
    albums = Album.find_by_user(user_id)
    
    # 获取每个图集的照片数量
    for album in albums:
        album['photo_count'] = Album.get_photo_count(album['id'])
    
    return jsonify({
        'success': True,
        'albums': albums
    }), 200

@album_bp.route('/<int:album_id>', methods=['PUT'])
def update_album(album_id):
    """
    更新图集信息
    ---
    路径参数:
      - album_id: 图集ID
    请求参数:
      - name: 图集名称（可选）
      - content: 图集描述（可选）
      - cover_url: 封面图片URL（可选）
    """
    album = Album.find_by_id(album_id)
    
    if not album:
        return jsonify({
            'success': False,
            'message': '图集不存在'
        }), 404
    
    data = request.get_json()
    
    if not data:
        return jsonify({
            'success': False,
            'message': '请提供要更新的数据'
        }), 400
    
    name = data.get('name')
    content = data.get('content')
    cover_url = data.get('cover_url')
    
    result = Album.update(album_id, name, content, cover_url)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': '图集更新成功'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': result['message']
        }), 400

@album_bp.route('/<int:album_id>', methods=['DELETE'])
def delete_album(album_id):
    """
    删除图集
    ---
    路径参数:
      - album_id: 图集ID
    """
    album = Album.find_by_id(album_id)
    
    if not album:
        return jsonify({
            'success': False,
            'message': '图集不存在'
        }), 404
    
    result = Album.delete(album_id)
    
    if result['success']:
        return jsonify({
            'success': True,
            'message': '图集删除成功'
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '图集删除失败'
        }), 500

@album_bp.route('/<int:album_id>/photos', methods=['GET'])
def get_album_photos(album_id):
    """
    获取图集中的所有照片
    ---
    路径参数:
      - album_id: 图集ID
    """
    album = Album.find_by_id(album_id)
    
    if not album:
        return jsonify({
            'success': False,
            'message': '图集不存在'
        }), 404
    
    photos = Photo.find_by_album(album_id)
    
    return jsonify({
        'success': True,
        'photos': photos
    }), 200 