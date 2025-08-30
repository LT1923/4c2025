import mysql.connector
from mysql.connector import Error

# 数据库配置
DB_CONFIG = {
    # 'host': 'localhost',
    'host': 'rm-gc7c284ffw26udt08ho.mysql.cn-chengdu.rds.aliyuncs.com',
    'user': 'dbuser',
    'password': '2wTXYiNj+Tmp',
    'database': 'graph'
}


def get_db_connection():
    """
    获取数据库连接
    """
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except Error as e:
        print(f"数据库连接错误: {e}")
        return None


def db_init():
    """
    初始化数据库和表
    """
    try:
        # 连接MySQL服务器（不指定数据库）
        conn = mysql.connector.connect(
            host=DB_CONFIG['host'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )

        cursor = conn.cursor()

        # 创建数据库（如果不存在）
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
        cursor.execute(f"USE {DB_CONFIG['database']}")

        # 创建用户表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            phone VARCHAR(20) NOT NULL UNIQUE,
            password VARCHAR(255) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # 创建图集表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS albums (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            content TEXT,
            cover_url VARCHAR(255),
            user_id INT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        ''')

        # 创建照片表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS photos (
            id INT AUTO_INCREMENT PRIMARY KEY,
            address VARCHAR(255) NOT NULL,
            text TEXT,
            time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            album_id INT,
            user_id INT,
            status INT DEFAULT 0,
            FOREIGN KEY (album_id) REFERENCES albums(id) ON DELETE SET NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        ''')

        # 检查并添加 status 字段（如果不存在）
        try:
            cursor.execute("SHOW COLUMNS FROM photos LIKE 'status'")
            status_exists = cursor.fetchone() is not None

            if not status_exists:
                print("添加 status 字段到 photos 表")
                cursor.execute("ALTER TABLE photos ADD COLUMN status INT DEFAULT 0")
                # 将现有照片的状态设置为0（正常状态）
                cursor.execute("UPDATE photos SET status = 0 WHERE status IS NULL")
                conn.commit()
                print("status 字段添加成功")
        except Error as e:
            print(f"检查/添加 status 字段时出错: {e}")

        conn.commit()
        print("数据库初始化成功")

    except Error as e:
        print(f"数据库初始化错误: {e}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


def execute_query(query, params=None, fetch=False):
    """
    执行SQL查询
    todo: change this to model
    """
    conn = get_db_connection()
    result = None

    if conn:
        try:
            cursor = conn.cursor(dictionary=True)  # 创建一个游标对象 cursor，并通过 dictionary=True 设置返回的结果以字典形式表示
            cursor.execute(query, params or ())  # 执行 SQL 查询 query，并将参数 params 传递给查询。如果没有传递参数，则使用空元组 ()

            if fetch:  # 判断是否需要获取查询结果
                result = cursor.fetchall()  # 调用 cursor.fetchall() 获取所有查询结果，并将其赋值给 result
            else:
                conn.commit()
                result = cursor.lastrowid  # 调用 conn.commit() 提交事务（通常用于写操作，如插入、更新、删除），并将最后插入行的 ID (cursor.lastrowid) 赋值给 result

        except Error as e:
            print(f"查询执行错误: {e}")
        finally:
            if conn.is_connected():
                cursor.close()
                conn.close()

    return result  # 返回查询结果或最后插入行的 ID


if __name__ == '__main__':
    execute_query("SELECT * FROM albums")
