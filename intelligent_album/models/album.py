from config.database import execute_query


class Album:
    def __init__(self, id=None, name=None, content=None, cover_url=None, user_id=None, created_at=None):
        self.id = id
        self.name = name
        self.content = content
        self.cover_url = cover_url
        self.user_id = user_id
        self.created_at = created_at

    @staticmethod
    def create(name, content, user_id, cover_url=None):
        """
        创建新图集
        """
        query = """
        INSERT INTO albums (name, content, cover_url, user_id) 
        VALUES (%s, %s, %s, %s)
        """
        params = (name, content, cover_url, user_id)

        album_id = execute_query(query, params)
        if album_id:
            return {"success": True, "album_id": album_id}
        else:
            return {"success": False, "message": "创建图集失败"}

    @staticmethod
    def find_by_id(album_id):
        """
        通过ID查找图集
        todo: 把这里改成Model
        """
        query = "SELECT * FROM albums WHERE id = %s"
        params = (album_id,)
        albums = execute_query(query, params, fetch=True)

        if albums and len(albums) > 0:
            return albums[0]
        return None

    @staticmethod
    def find_by_user(user_id):
        """
        查找用户的所有图集
        """
        query = "SELECT * FROM albums WHERE user_id = %s ORDER BY created_at DESC"
        params = (user_id,)
        return execute_query(query, params, fetch=True)

    @staticmethod
    def update(album_id, name=None, content=None, cover_url=None):
        """
        更新图集信息
        """
        # 构建动态更新查询
        update_fields = []
        params = []

        if name is not None:
            update_fields.append("name = %s")
            params.append(name)

        if content is not None:
            update_fields.append("content = %s")
            params.append(content)

        if cover_url is not None:
            update_fields.append("cover_url = %s")
            params.append(cover_url)

        if not update_fields:
            return {"success": False, "message": "没有提供要更新的字段"}

        query = f"UPDATE albums SET {', '.join(update_fields)} WHERE id = %s"
        params.append(album_id)

        execute_query(query, tuple(params))
        return {"success": True}

    @staticmethod
    def delete(album_id):
        """
        删除图集
        """
        query = "DELETE FROM albums WHERE id = %s"
        params = (album_id,)

        execute_query(query, params)
        return {"success": True}

    @staticmethod
    def get_photo_count(album_id):
        """
        获取图集中的照片数量
        """
        query = "SELECT COUNT(*) as count FROM photos WHERE album_id = %s"
        params = (album_id,)
        result = execute_query(query, params, fetch=True)

        if result and len(result) > 0:
            return result[0]['count']
        return 0

    @staticmethod
    def update_cover(album_id, cover_url):
        """
        更新图集封面
        """
        query = "UPDATE albums SET cover_url = %s WHERE id = %s"
        params = (cover_url, album_id)

        execute_query(query, params)
        return {"success": True}
