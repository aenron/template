# CI/CD 流水线配置

本文档描述了项目中配置的各种CI/CD流水线，支持多种平台和自动化流程。

## 支持的平台

### 1. GitHub Actions

#### CI流水线 (`.github/workflows/ci.yml`)
- **触发条件**: 推送到 `main` 或 `develop` 分支，或创建PR
- **功能**:
  - 代码测试（包含PostgreSQL和Redis服务）
  - 代码质量检查（flake8, black, isort）
  - 安全扫描（Bandit, Safety）
  - Docker镜像构建和测试
  - 代码覆盖率报告

#### CD流水线 (`.github/workflows/cd.yml`)
- **触发条件**: 推送到 `main` 分支或创建版本标签
- **功能**:
  - Docker镜像构建和推送到GitHub Container Registry
  - 自动部署到测试环境（develop分支）
  - 手动部署到生产环境（版本标签）
  - 自动回滚机制

### 2. Gitea Actions

#### CI流水线 (`.gitea/workflows/ci.yml`)
- **触发条件**: 推送到 `main` 或 `develop` 分支，或创建PR
- **功能**:
  - 代码测试（包含PostgreSQL和Redis服务）
  - 代码质量检查（flake8, black, isort）
  - 安全扫描（Bandit, Safety）
  - Docker镜像构建和测试
  - 代码覆盖率报告
  - 代码质量统计

#### CD流水线 (`.gitea/workflows/cd.yml`)
- **触发条件**: 推送到 `main` 分支或创建版本标签
- **功能**:
  - Docker镜像构建和推送到Gitea Container Registry
  - 自动部署到测试环境（main分支）
  - 手动部署到生产环境（版本标签）
  - 自动回滚机制
  - 部署结果通知

#### 发布流水线 (`.gitea/workflows/release.yml`)
- **触发条件**: 创建版本标签（v*）
- **功能**:
  - 构建发布版本
  - 安全扫描
  - 推送到Gitea Container Registry
  - 创建Gitea Release
  - 生成变更日志
  - 生产环境部署
  - 发布通知

### 3. GitLab CI/CD

#### 流水线配置 (`.gitlab-ci.yml`)
- **触发条件**: 推送到 `main` 或 `develop` 分支，或创建版本标签
- **阶段**:
  - **测试阶段**: 代码测试、覆盖率报告
  - **安全阶段**: 安全扫描
  - **构建阶段**: Docker镜像构建和推送
  - **部署阶段**: 自动部署到测试/生产环境

### 4. Azure DevOps

#### 流水线配置 (`azure-pipelines.yml`)
- **触发条件**: 推送到 `main` 或 `develop` 分支，或创建版本标签
- **阶段**:
  - **测试阶段**: 代码测试、覆盖率报告
  - **安全阶段**: 安全扫描
  - **构建阶段**: Docker镜像构建
  - **部署阶段**: 环境部署

### 5. Jenkins

#### 流水线配置 (`Jenkinsfile`)
- **触发条件**: 代码推送或手动触发
- **阶段**:
  - 代码检出
  - Python环境设置
  - 代码检查
  - 测试执行
  - 安全扫描
  - Docker构建
  - 部署（测试/生产）

### 6. CircleCI

#### 流水线配置 (`.circleci/config.yml`)
- **触发条件**: 代码推送
- **任务**:
  - 测试任务
  - 安全扫描
  - Docker构建
  - 环境部署

## 环境配置

### 测试环境
- **分支**: `develop`
- **自动部署**: 是
- **健康检查**: 是
- **回滚机制**: 是

### 生产环境
- **分支**: `main` 或版本标签
- **自动部署**: 仅版本标签
- **手动确认**: 是
- **健康检查**: 是
- **回滚机制**: 是

## 部署脚本

### 通用部署脚本 (`scripts/deploy.sh`)
```bash
# 部署到测试环境
./scripts/deploy.sh staging

# 部署到生产环境
./scripts/deploy.sh production v1.0.0
```

**功能特性**:
- 环境验证
- SSH连接检查
- 自动备份
- 健康检查
- 自动回滚
- 资源清理

### Gitea部署脚本 (`scripts/deploy-gitea.sh`)
```bash
# 部署到测试环境
./scripts/deploy-gitea.sh staging

# 部署到生产环境
./scripts/deploy-gitea.sh production v1.0.0
```

**功能特性**:
- Gitea容器注册表集成
- Gitea Token认证
- 部署日志记录
- 环境特定配置
- 自动回滚机制

## 环境变量配置

### GitHub Actions
```yaml
# 在仓库设置中配置以下Secrets
DATABASE_URL: postgresql://user:pass@host:port/db
SECRET_KEY: your-secret-key
DOCKER_REGISTRY: ghcr.io
```

### Gitea Actions
```yaml
# 在仓库设置中配置以下Secrets
DATABASE_URL: postgresql://user:pass@host:port/db
SECRET_KEY: your-secret-key
GITEA_TOKEN: your-gitea-token
GITEA_USER: your-gitea-username
GITEA_REGISTRY: gitea.example.com
```

### GitLab CI/CD
```yaml
# 在项目设置中配置以下变量
DATABASE_URL: postgresql://user:pass@host:port/db
SECRET_KEY: your-secret-key
CI_REGISTRY: registry.gitlab.com
```

### Azure DevOps
```yaml
# 在项目设置中配置以下变量
DATABASE_URL: postgresql://user:pass@host:port/db
SECRET_KEY: your-secret-key
DOCKER_REGISTRY: your-registry.azurecr.io
```

## 安全扫描

### 工具配置
- **Bandit**: Python安全漏洞扫描
- **Safety**: 依赖包安全扫描
- **配置**: 在流水线中自动执行

### 扫描规则
- 低级别警告
- 中等置信度
- 生成JSON报告

## 代码质量检查

### 工具配置
- **flake8**: 代码风格检查
- **black**: 代码格式化检查
- **isort**: 导入排序检查

### 配置规则
```ini
# flake8配置
max-line-length = 88
extend-ignore = E203,W503

# black配置
line-length = 88
target-version = py311

# isort配置
profile = black
line_length = 88
```

## 测试配置

### 测试框架
- **pytest**: 测试执行
- **pytest-cov**: 覆盖率报告
- **pytest-asyncio**: 异步测试支持

### 测试环境
- **数据库**: PostgreSQL 15
- **缓存**: Redis 7
- **覆盖率**: XML和终端报告

## Docker配置

### 镜像构建
- **多阶段构建**: 优化镜像大小
- **缓存优化**: 利用GitHub Actions缓存
- **健康检查**: 内置健康检查端点

### 镜像标签策略
- `latest`: 最新版本
- `{commit-sha}`: 提交哈希
- `{branch}-{build-id}`: 分支构建
- `v{version}`: 版本标签

## 监控和通知

### 健康检查
- **端点**: `/health`
- **检查内容**: 数据库连接、Redis连接
- **超时**: 10秒

### 通知机制
- **成功通知**: 部署成功消息
- **失败通知**: 错误详情和回滚状态
- **支持平台**: Slack、邮件、Webhook

## 故障排除

### 常见问题

1. **Docker构建失败**
   - 检查Dockerfile语法
   - 验证依赖包版本
   - 检查网络连接

2. **测试失败**
   - 检查数据库连接
   - 验证环境变量
   - 查看测试日志

3. **部署失败**
   - 检查SSH连接
   - 验证服务器权限
   - 查看健康检查日志

### 调试命令
```bash
# 查看流水线日志
# GitHub Actions: 在Actions页面查看
# GitLab: 在CI/CD页面查看
# Jenkins: 在构建页面查看

# 手动测试健康检查
curl -f http://localhost:8000/health

# 查看Docker容器状态
docker-compose ps

# 查看应用日志
docker-compose logs app
```

## 最佳实践

1. **分支策略**
   - 使用功能分支开发
   - 通过PR合并到develop
   - 定期合并develop到main

2. **版本管理**
   - 使用语义化版本号
   - 创建版本标签触发生产部署
   - 保持版本历史记录

3. **安全考虑**
   - 定期更新依赖包
   - 使用安全扫描工具
   - 保护敏感信息

4. **监控告警**
   - 设置健康检查告警
   - 监控部署状态
   - 记录部署历史 