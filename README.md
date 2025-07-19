# FastAPI 接口模板

基于 FastAPI 的 RESTful API 模板。

## 项目特性

- 🚀 基于 FastAPI 的高性能异步框架
- 📚 自动生成 API 文档 (Swagger UI / ReDoc)
- 🔐 JWT 认证和授权
- 🗄️ SQLAlchemy ORM 数据库操作
- 📝 结构化日志记录
- ✅ 完整的异常处理机制
- 🧪 测试框架支持
- 🐳 Docker 容器化支持

## 快速开始

### 环境要求

- Python 3.8+
- pip

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

复制环境变量示例文件并修改配置：

```bash
cp env.example .env
```

编辑 `.env` 文件，设置必要的配置项。

### 启动服务

```bash
# 方式1: 使用增强启动脚本（推荐）
python start.py

# 方式2: 使用 uvicorn 启动
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### 访问服务

- API 服务: http://localhost:8000
- API 文档: http://localhost:8000/docs
- ReDoc 文档: http://localhost:8000/redoc
- 健康检查: http://localhost:8000/health

## 项目结构

```
template/
├── app/                    # 应用主目录
│   ├── api/               # API 路由
│   │   └── v1/           # API v1 版本
│   │       ├── api.py    # 主路由
│   │       └── endpoints/ # API 端点
│   │           ├── auth.py    # 认证相关
│   │           └── users.py   # 用户管理
│   ├── core/             # 核心配置
│   │   ├── config.py     # 配置管理
│   │   ├── exceptions.py # 异常处理
│   │   └── logging.py    # 日志配置
│   ├── database/         # 数据库
│   │   └── database.py   # 数据库连接
│   ├── models/           # 数据模型
│   │   └── user.py       # 用户模型
│   ├── schemas/          # Pydantic 模式
│   │   └── user.py       # 用户模式
│   └── main.py           # 应用入口
├── docs/                 # 项目文档
├── scripts/              # 部署脚本
│   ├── docker-build.sh   # Docker构建脚本
│   └── docker-run.sh     # Docker运行脚本
├── tests/                # 测试文件
├── Dockerfile            # 生产环境Dockerfile
├── Dockerfile.dev        # 开发环境Dockerfile
├── docker-compose.yml    # 生产环境配置
├── docker-compose.dev.yml # 开发环境配置
├── docker-compose.override.yml # 本地开发覆盖配置
├── nginx.conf            # Nginx配置
├── init-db.sql           # 数据库初始化脚本
├── .dockerignore         # Docker忽略文件
├── requirements.txt      # Python 依赖
├── env.example          # 环境变量示例
├── start.py             # 便捷启动脚本
└── README.md            # 项目说明
```

## API 接口

### 认证接口

- `POST /api/v1/auth/login` - 用户登录
- `POST /api/v1/auth/register` - 用户注册
- `GET /api/v1/auth/me` - 获取当前用户信息
- `POST /api/v1/auth/logout` - 用户登出

### 用户管理接口

- `GET /api/v1/users/` - 获取用户列表
- `GET /api/v1/users/{user_id}` - 获取用户详情
- `POST /api/v1/users/` - 创建用户
- `PUT /api/v1/users/{user_id}` - 更新用户
- `DELETE /api/v1/users/{user_id}` - 删除用户

### 系统接口

- `GET /` - 根路径
- `GET /health` - 健康检查

## 开发指南

### 代码规范

- 遵循 PEP 8 代码规范
- 使用类型提示
- 添加详细的文档字符串
- 使用中文注释

### 测试

```bash
# 运行测试
pytest

# 运行测试并显示覆盖率
pytest --cov=app
```

### 代码格式化

```bash
# 格式化代码
black .

# 排序导入
isort .

# 检查代码质量
flake8
```

## 部署

### Docker 部署

#### 快速开始

```bash
# 1. 构建镜像
./scripts/docker-build.sh --production

# 2. 启动生产环境
./scripts/docker-run.sh start

# 3. 查看服务状态
./scripts/docker-run.sh status
```

#### 开发环境

```bash
# 启动开发环境（包含热重载）
./scripts/docker-run.sh dev

# 查看日志
./scripts/docker-run.sh logs app

# 进入容器
./scripts/docker-run.sh exec app
```

#### 手动操作

```bash
# 构建镜像
docker build -t fastapi-project:latest .

# 启动生产环境
docker-compose up -d

# 启动开发环境
docker-compose -f docker-compose.yml -f docker-compose.override.yml up -d

# 停止服务
docker-compose down

# 查看日志
docker-compose logs -f
```

#### 服务访问

- **生产环境**: http://localhost:8000
- **开发环境**: http://localhost:8000
- **API文档**: http://localhost:8000/docs
- **pgAdmin**: http://localhost:5050 (开发环境)
- **数据库**: localhost:5432
- **Redis**: localhost:6379

### 生产环境配置

1. 设置 `DEBUG=false`
2. 配置生产数据库
3. 设置强密钥
4. 配置反向代理 (Nginx)
5. 启用 HTTPS

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

MIT License

## 联系方式

如有问题或建议，请提交 Issue 或联系开发团队。
