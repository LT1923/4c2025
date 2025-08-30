# 相册应用后端

这是一个基于Flask的相册应用后端，提供用户管理、图集管理和照片管理的API。

## 功能特点

- 用户注册和登录
- 图集的创建、查询、更新和删除
- 照片的上传、查询、更新和删除
- 照片搜索功能
- 照片与图集的关联管理

## 技术栈

- Python 3.8+
- Flask
- MySQL

## 安装和配置

### 1. 克隆仓库

```bash
git clone <repository-url>
cd graph_server
```

### 2. 安装依赖

```bash
pip install -r requirements.txt
```

### 3. 配置数据库

在 `config/database.py` 中配置数据库连接信息：

```python
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123456',
    'database': 'graph'
}
```

### 4. 创建上传目录

应用会自动创建 `uploads` 目录用于存储上传的照片。

## 运行应用

```bash
python app.py
```

应用将在 `http://localhost:5000` 上运行。

## API 文档

### 用户相关

#### 注册用户

- **URL**: `/api/users/register`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "phone": "13800138000",
    "password": "password123"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "message": "注册成功",
    "user_id": 1
  }
  ```

#### 用户登录

- **URL**: `/api/users/login`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "phone": "13800138000",
    "password": "password123"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "message": "登录成功",
    "user": {
      "id": 1,
      "phone": "13800138000",
      "created_at": "2023-01-01T00:00:00"
    }
  }
  ```

#### 获取用户信息

- **URL**: `/api/users/{user_id}`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "success": true,
    "user": {
      "id": 1,
      "phone": "13800138000",
      "created_at": "2023-01-01T00:00:00"
    }
  }
  ```

### 图集相关

#### 创建图集

- **URL**: `/api/albums/`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "name": "我的旅行",
    "content": "记录美好的旅行时光",
    "user_id": 1,
    "cover_url": "uploads/1/example.jpg"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "message": "图集创建成功",
    "album_id": 1
  }
  ```

#### 获取图集信息

- **URL**: `/api/albums/{album_id}`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "success": true,
    "album": {
      "id": 1,
      "name": "我的旅行",
      "content": "记录美好的旅行时光",
      "cover_url": "uploads/1/example.jpg",
      "user_id": 1,
      "created_at": "2023-01-01T00:00:00",
      "photo_count": 5
    }
  }
  ```

#### 获取用户的所有图集

- **URL**: `/api/albums/user/{user_id}`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "success": true,
    "albums": [
      {
        "id": 1,
        "name": "我的旅行",
        "content": "记录美好的旅行时光",
        "cover_url": "uploads/1/example.jpg",
        "user_id": 1,
        "created_at": "2023-01-01T00:00:00",
        "photo_count": 5
      }
    ]
  }
  ```

#### 更新图集

- **URL**: `/api/albums/{album_id}`
- **方法**: `PUT`
- **请求体**:
  ```json
  {
    "name": "新的图集名称",
    "content": "新的图集描述",
    "cover_url": "uploads/1/new_cover.jpg"
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "message": "图集更新成功"
  }
  ```

#### 删除图集

- **URL**: `/api/albums/{album_id}`
- **方法**: `DELETE`
- **响应**:
  ```json
  {
    "success": true,
    "message": "图集删除成功"
  }
  ```

#### 获取图集中的所有照片

- **URL**: `/api/albums/{album_id}/photos`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "success": true,
    "photos": [
      {
        "id": 1,
        "address": "uploads/1/example.jpg",
        "text": "美丽的风景",
        "time": "2023-01-01T00:00:00",
        "album_id": 1,
        "user_id": 1
      }
    ]
  }
  ```

### 照片相关

#### 上传照片

- **URL**: `/api/photos/upload`
- **方法**: `POST`
- **表单数据**:
  - `photo`: 照片文件
  - `user_id`: 用户ID
  - `album_id`: 图集ID（可选）
  - `text`: 照片描述（可选）
- **响应**:
  ```json
  {
    "success": true,
    "message": "照片上传成功",
    "photo_id": 1,
    "photo_url": "uploads/1/20230101000000_example.jpg"
  }
  ```

#### 获取照片信息

- **URL**: `/api/photos/{photo_id}`
- **方法**: `GET`
- **响应**:
  ```json
  {
    "success": true,
    "photo": {
      "id": 1,
      "address": "uploads/1/example.jpg",
      "text": "美丽的风景",
      "time": "2023-01-01T00:00:00",
      "album_id": 1,
      "user_id": 1
    }
  }
  ```

#### 获取用户的所有照片

- **URL**: `/api/photos/user/{user_id}`
- **方法**: `GET`
- **查询参数**:
  - `limit`: 限制返回数量
  - `offset`: 偏移量（分页）
- **响应**:
  ```json
  {
    "success": true,
    "photos": [
      {
        "id": 1,
        "address": "uploads/1/example.jpg",
        "text": "美丽的风景",
        "time": "2023-01-01T00:00:00",
        "album_id": 1,
        "user_id": 1
      }
    ]
  }
  ```

#### 获取用户最近上传的照片

- **URL**: `/api/photos/recent/{user_id}`
- **方法**: `GET`
- **查询参数**:
  - `limit`: 限制返回数量（默认20）
- **响应**:
  ```json
  {
    "success": true,
    "photos": [
      {
        "id": 1,
        "address": "uploads/1/example.jpg",
        "text": "美丽的风景",
        "time": "2023-01-01T00:00:00",
        "album_id": 1,
        "user_id": 1
      }
    ]
  }
  ```

#### 更新照片信息

- **URL**: `/api/photos/{photo_id}`
- **方法**: `PUT`
- **请求体**:
  ```json
  {
    "text": "新的照片描述",
    "album_id": 2
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "message": "照片信息更新成功"
  }
  ```

#### 删除照片

- **URL**: `/api/photos/{photo_id}`
- **方法**: `DELETE`
- **响应**:
  ```json
  {
    "success": true,
    "message": "照片删除成功"
  }
  ```

#### 搜索照片

- **URL**: `/api/photos/search/{user_id}`
- **方法**: `GET`
- **查询参数**:
  - `keyword`: 搜索关键词
- **响应**:
  ```json
  {
    "success": true,
    "photos": [
      {
        "id": 1,
        "address": "uploads/1/example.jpg",
        "text": "美丽的风景",
        "time": "2023-01-01T00:00:00",
        "album_id": 1,
        "user_id": 1
      }
    ],
    "count": 1
  }
  ```

#### 将照片移动到指定图集

- **URL**: `/api/photos/move/{photo_id}`
- **方法**: `PUT`
- **请求体**:
  ```json
  {
    "album_id": 2
  }
  ```
- **响应**:
  ```json
  {
    "success": true,
    "message": "照片已移动到指定图集"
  }
  ```

## 依赖项

创建 `requirements.txt` 文件，包含以下依赖：

```
Flask==2.0.1
Flask-Cors==3.0.10
mysql-connector-python==8.0.26
Werkzeug==2.0.1
``` 