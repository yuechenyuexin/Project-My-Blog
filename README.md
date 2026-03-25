# 🚀 FastAPI 个人博客系统（含语义搜索）

> 基于 FastAPI + 异步 SQLAlchemy + MySQL + Chroma 向量库构建的现代化个人博客后端
>
> 支持用户认证、文章管理、分类管理、**语义搜索**，接口规范统一，结构清晰，可直接上线使用。

## ✨ 项目特性

- 🌐 **FastAPI 现代化架构**，自动生成 Swagger 接口文档
- 🔐 **JWT 登录认证**，密码 bcrypt 加密存储
- 📝 **完整文章 CRUD**，仅作者可编辑 / 删除自己的文章
- 🗂️ **分类管理 + 文章筛选 + 分页**
- 🧠 **语义搜索功能**（Chroma + Sentence-Transformers）
- 📦 **统一返回格式**：`code + msg + data`
- 🛡️ **全局异常捕获**，所有错误自动格式化
- ⚡ **全异步数据库操作**，性能更高
- 🧩 工程化分层设计，易于扩展与维护

## 🛠 技术栈

- **框架**：FastAPI
- **数据库**：MySQL + SQLAlchemy (async)
- **认证**：JWT + passlib[bcrypt]
- **向量库**：ChromaDB
- **向量模型**：sentence-transformers / text2vec-base-chinese
- **服务器**：Uvicorn
- **环境**：python-dotenv

## 🧩 功能模块

### 1. 用户模块

- 用户注册、登录、登出
- 获取 / 修改个人信息
- JWT 令牌校验

### 2. 分类模块

- 分类列表（分页）
- 文章按分类筛选

### 3. 文章模块

- 文章列表（分页 + 分类筛选）
- 文章详情（自动增加浏览量）
- 创建、修改、删除文章（权限控制）

### 4. 智能语义搜索（第二阶段）

- 文章标题 + 内容向量化存储
- 输入关键词即可**语义匹配**相关文章
- 支持按分类筛选搜索
- 新增 / 修改 / 删除文章自动同步向量库

## 🚀 快速开始

### 1. 克隆项目

```
git clone https://github.com/你的用户名/你的仓库名.git
cd 你的仓库名
```

### 2. 安装依赖

```
pip install -r requirements.txt
```

### 3. 配置 .env 文件

```
# 数据库
DB_USER=root
DB_PASSWORD=你的密码
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=blog_db

# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 4. 创建数据库

```
CREATE DATABASE blog_db DEFAULT CHARSET utf8mb4;
```

### 5. 初始化数据表

```
python create_tables.py
```

### 6. 启动项目

```
python main.py
```

### 7. 接口文档

- Swagger：http://127.0.0.1:8000/docs
- ReDoc：http://127.0.0.1:8000/redoc

------

## 🧠 语义搜索使用（第二阶段）

### 安装向量依赖

```
pip install chromadb sentence-transformers
```

### 同步现有文章到向量库

```
python sync_articles_to_vector.py
```

### 搜索接口

```
GET /api/articles/search?query=你的关键词
```

支持：

- 语义匹配
- 按分类筛选
- 相似度排序

------

## 📌 接口统一返回格式

所有接口统一返回结构，前端无需适配多种格式：

```
{
  "code": 200,
  "msg": "success",
  "data": {}
}
```

- `code=200` 成功
- `4xx` 客户端错误
- `500` 服务器异常

------

## 📂 项目结构

```
├── main.py                    # 项目入口
├── .env                       # 环境配置
├── README.md                  # 项目说明
├── requirements.txt           # 依赖
├── create_tables.py           # 建表脚本
├── sync_articles_to_vector.py # 向量同步脚本
├── vector_store.py            # 向量库核心逻辑
│
├── models/           # ORM 模型
├── schemas/          # Pydantic 校验
├── crud/             # 数据库操作
├── routers/          # 接口路由
├── dependencies/     # 登录依赖
├── utils/            # JWT 工具 和 全局异常处理
└── chroma_db/        # 向量库持久化目录
```

------

## 🧪 测试流程

1. 注册用户 → 登录获取 token
2. 创建分类
3. 发布文章
4. 同步向量库
5. 使用 `/api/articles/search` 测试语义搜索
6. 测试文章增删改自动同步向量

------

## 📦 部署建议

- 开发：`uvicorn main:app --reload`
- 生产：使用 Gunicorn + Uvicorn 部署
- 向量库：`chroma_db` 目录需要保留，不可删除
- 模型首次运行会自动下载，无需手动处理

------

## 📄 开源协议

MIT License — 可自由使用、修改、商用，保留作者信息即可。

------

## 🤝 贡献

欢迎提交 Issue、PR，一起优化功能：

- 评论模块
- 点赞收藏
- 文件上传
- 后台管理
- 搜索引擎优化

------

## 🧑‍💻 作者

基于 FastAPI 工程化个人学习实践构建

------

## 🎯 亮点总结

- 接口规范 ✅
- 权限控制 ✅
- 异步高性能 ✅
- 结构清晰易维护 ✅
- 可直接上线 ✅