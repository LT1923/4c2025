from config.database import execute_query
# from intelligent_album.config.database import execute_query
from datetime import datetime, timedelta


class Photo:
    def __init__(self, id=None, address=None, text=None, time=None, album_id=None, user_id=None, status=0):
        self.id = id
        self.address = address
        self.text = text
        self.time = time
        self.album_id = album_id
        self.user_id = user_id
        self.status = status

    @staticmethod
    def create(address, user_id, text=None, album_id=None, time=None, status=0):
        """
        创建新照片
        """
        if time is None:
            time = datetime.now()

        query = """
        INSERT INTO photos (address, text, time, album_id, user_id, status) 
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        params = (address, text, time, album_id, user_id, status)

        photo_id = execute_query(query, params)
        if photo_id:
            return {"success": True, "photo_id": photo_id}
        else:
            return {"success": False, "message": "上传照片失败"}

    @staticmethod
    def find_by_id(photo_id):
        """
        通过ID查找照片
        """
        query = "SELECT * FROM photos WHERE id = %s"  # 查找id是字符串类型的图片
        params = (photo_id,)
        photos = execute_query(query, params, fetch=True)

        if photos and len(photos) > 0:
            return photos[0]
        return None

    @staticmethod
    def find_by_user(user_id, limit=None, offset=None):
        """
        查找用户的所有正常照片（不包括回收站和封面的照片）
        """
        # 首先修复任何无效的状态
        Photo.fix_photo_status()

        query = """
        SELECT * FROM photos 
        WHERE user_id = %s AND status = 0 
        ORDER BY time DESC
        """
        params = [user_id]

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

            if offset is not None:
                query += " OFFSET %s"
                params.append(offset)

        print(f"find_by_user: 查询用户 {user_id} 的正常照片")
        print(f"执行查询: {query} 参数: {params}")
        result = execute_query(query, tuple(params), fetch=True)
        print(f"查询结果: 找到 {len(result) if result else 0} 条记录")

        return result

    @staticmethod
    def find_by_album(album_id):
        """
        查找图集中的所有照片（不包括回收站和封面的照片）
        """
        query = "SELECT * FROM photos WHERE album_id = %s AND status = 0 ORDER BY time DESC"
        params = (album_id,)
        return execute_query(query, params, fetch=True)

    @staticmethod
    def fix_photo_status():
        """
        修复所有照片的状态
        将所有 status 为 NULL 或无效值的照片设置为 0（正常状态）
        有效状态: 0(正常), 1(回收站), 2(封面)
        """
        query = """
        UPDATE photos 
        SET status = 0 
        WHERE status IS NULL OR status NOT IN (0, 1, 2)
        """
        execute_query(query)
        return {"success": True, "message": "照片状态已修复"}

    @staticmethod
    def find_in_trash(user_id, limit=None, offset=None):
        """
        查找用户回收站中的照片（状态为1，不包括正常照片和封面照片）
        """
        print(f"find_in_trash: 查询用户 {user_id} 的回收站照片")

        # 首先修复任何无效的状态
        Photo.fix_photo_status()

        query = """
        SELECT * FROM photos 
        WHERE user_id = %s AND status = 1 
        ORDER BY time DESC
        """
        params = [user_id]

        if limit is not None:
            query += " LIMIT %s"
            params.append(limit)

            if offset is not None:
                query += " OFFSET %s"
                params.append(offset)

        print(f"执行查询: {query} 参数: {params}")
        result = execute_query(query, tuple(params), fetch=True)
        print(f"查询结果: 找到 {len(result) if result else 0} 条记录")

        return result

    @staticmethod
    def update_status(photo_id, status):
        """
        更新照片状态
        """
        query = "UPDATE photos SET status = %s WHERE id = %s"
        params = (status, photo_id)

        execute_query(query, params)
        return {"success": True}

    @staticmethod
    def update(photo_id, text=None, album_id=None, status=None):
        """
        更新照片信息
        """
        # 构建动态更新查询
        update_fields = []
        params = []

        if text is not None:
            update_fields.append("text = %s")
            params.append(text)

        if album_id is not None:
            update_fields.append("album_id = %s")
            params.append(album_id)

        if status is not None:
            update_fields.append("status = %s")
            params.append(status)

        if not update_fields:
            return {"success": False, "message": "没有提供要更新的字段"}

        query = f"UPDATE photos SET {', '.join(update_fields)} WHERE id = %s"
        params.append(photo_id)

        execute_query(query, params)
        return {"success": True}

    @staticmethod
    def delete(photo_id):
        """
        删除照片
        """
        query = "DELETE FROM photos WHERE id = %s"
        params = (photo_id,)

        execute_query(query, params)
        return {"success": True}

    @staticmethod
    def search(user_id, addr, keyword=None):
        """
        搜索正常状态的照片（status = 0）
        update: 去掉了keyword这一筛选条件，改成使用图片路径addr筛选
        todo: 测试能否正常使用
        """
        """
        # 原实现
        query = "SELECT * FROM photos WHERE user_id = %s AND status = 0 AND text LIKE %s ORDER BY time DESC"
        params = (user_id, f"%{keyword}%")
        return execute_query(query, params, fetch=True)
        """
        query = "SELECT * FROM photos WHERE user_id = %s AND status = 0 AND address = %s ORDER BY time DESC"
        params = (user_id, addr)
        return execute_query(query, params, fetch=True)

    @staticmethod
    def search_in_trash(user_id, addr, keyword=None):
        """
        搜索回收站中的照片（status = 1）
        update: 去掉了keyword这一筛选条件，改成使用图片路径addr筛选
        todo: 测试能否正常使用
        """
        """
        # 原实现
        query = "SELECT * FROM photos WHERE user_id = %s AND status = 1 AND text LIKE %s ORDER BY time DESC"
        params = (user_id, f"%{keyword}%")
        return execute_query(query, params, fetch=True)
        """
        query = "SELECT * FROM photos WHERE user_id = %s AND status = 1 AND address = %s ORDER BY time DESC"
        params = (user_id, addr)
        return execute_query(query, params, fetch=True)

    @staticmethod
    def search_recent(user_id, addr, keyword=None):
        """
        搜索最近一周上传的正常照片（status = 0）
        update: 去掉了keyword这一筛选条件，改成使用图片路径addr筛选
        todo: 测试能否正常使用
        """
        # 原实现
        # # 获取一周前的时间戳
        # one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
        #
        # query = """
        # SELECT * FROM photos
        # WHERE user_id = %s AND status = 0 AND text LIKE %s AND time >= %s
        # ORDER BY time DESC
        # """
        # params = (user_id, f"%{keyword}%", one_week_ago)
        # return execute_query(query, params, fetch=True)

        # 获取一周前的时间戳
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

        query = """
        SELECT * FROM photos 
        WHERE user_id = %s AND status = 0 AND address = %s AND time >= %s
        ORDER BY time DESC
        """
        params = (user_id, addr, one_week_ago)
        return execute_query(query, params, fetch=True)

    @staticmethod
    def get_recent(user_id, limit=20):
        """
        获取用户最近上传的照片（正常状态，不包括回收站和封面照片）
        """
        # 获取一周前的时间戳
        one_week_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')

        query = """
        SELECT * FROM photos 
        WHERE user_id = %s AND status = 0 AND time >= %s 
        ORDER BY time DESC LIMIT %s
        """
        params = (user_id, one_week_ago, limit)
        return execute_query(query, params, fetch=True)

    @staticmethod
    def move_to_album(photo_id, album_id):
        """
        将照片移动到指定图集
        """
        query = "UPDATE photos SET album_id = %s WHERE id = %s"
        params = (album_id, photo_id)

        execute_query(query, params)
        return {"success": True}


if __name__ == '__main__':
    print(Photo.search(1, 'uploads/1/boat.jpg'))
