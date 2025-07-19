# Gitea CI/CD 配置指南

本文档详细说明了如何在Gitea中配置和使用CI/CD流水线。

## Gitea Actions 简介

Gitea Actions是Gitea的CI/CD解决方案，语法与GitHub Actions兼容，支持自动化构建、测试和部署。

## 前置要求

### 1. Gitea版本要求
- Gitea 1.17.0 或更高版本
- 启用Actions功能

### 2. 系统要求
- 至少2GB RAM
- 支持Docker的环境
- 网络访问权限

## 配置文件说明

### 1. CI流水线 (`.gitea/workflows/ci.yml`)

**功能**:
- 代码测试和验证
- 代码质量检查
- 安全扫描
- Docker镜像构建

**触发条件**:
- 推送到 `main` 或 `develop` 分支
- 创建Pull Request

**主要任务**:
- **test**: 运行单元测试和集成测试
- **security**: 执行安全扫描
- **docker-build**: 构建和测试Docker镜像
- **code-quality**: 代码质量检查

### 2. CD流水线 (`.gitea/workflows/cd.yml`)

**功能**:
- 自动部署到不同环境
- Docker镜像推送
- 部署通知

**触发条件**:
- 推送到 `main` 分支
- 创建版本标签（v*）
- 手动触发

**主要任务**:
- **build-and-push**: 构建和推送Docker镜像
- **deploy-staging**: 部署到测试环境
- **deploy-production**: 部署到生产环境
- **rollback**: 自动回滚
- **notify**: 部署结果通知

### 3. 发布流水线 (`.gitea/workflows/release.yml`)

**功能**:
- 发布版本管理
- 创建Gitea Release
- 生成变更日志

**触发条件**:
- 创建版本标签（v*）

**主要任务**:
- **build**: 构建发布版本
- **security-scan**: 安全扫描
- **push-image**: 推送Docker镜像
- **create-release**: 创建Gitea Release
- **deploy-production**: 生产环境部署

## 环境配置

### 1. 仓库设置

在Gitea仓库中配置以下Secrets：

```yaml
# 必需的环境变量
DATABASE_URL: postgresql://user:pass@host:port/db
SECRET_KEY: your-secret-key

# Gitea特定配置
GITEA_TOKEN: your-gitea-token
GITEA_USER: your-gitea-username
GITEA_REGISTRY: gitea.example.com

# 部署配置
STAGING_HOST: staging.example.com
PRODUCTION_HOST: production.example.com
STAGING_USER: deploy
PRODUCTION_USER: deploy
```

### 2. 获取Gitea Token

1. 登录Gitea
2. 进入个人设置
3. 选择"Applications"
4. 生成新的Token
5. 复制Token到仓库Secrets

### 3. 配置容器注册表

如果使用Gitea的容器注册表：

```bash
# 登录Gitea容器注册表
docker login gitea.example.com -u your-username -p your-token

# 推送镜像
docker tag fastapi-project:latest gitea.example.com/username/repo:latest
docker push gitea.example.com/username/repo:latest
```

## 部署脚本使用

### 1. Gitea专用部署脚本

```bash
# 设置环境变量
export GITEA_TOKEN="your-gitea-token"
export GITEA_USER="your-gitea-username"
export GITEA_REGISTRY="gitea.example.com"
export GITEA_STAGING_HOST="staging.example.com"
export GITEA_PRODUCTION_HOST="production.example.com"

# 部署到测试环境
./scripts/deploy-gitea.sh staging

# 部署到生产环境
./scripts/deploy-gitea.sh production v1.0.0
```

### 2. 脚本功能特性

- **Gitea集成**: 自动登录Gitea容器注册表
- **环境管理**: 支持测试和生产环境
- **自动回滚**: 部署失败时自动回滚
- **日志记录**: 详细的部署日志
- **健康检查**: 部署后验证服务状态

## 工作流程

### 1. 开发流程

```bash
# 1. 创建功能分支
git checkout -b feature/new-feature

# 2. 开发功能
# ... 编写代码 ...

# 3. 提交代码
git add .
git commit -m "Add new feature"

# 4. 推送分支
git push origin feature/new-feature

# 5. 创建Pull Request
# 在Gitea界面创建PR
```

### 2. 发布流程

```bash
# 1. 合并到main分支
# 通过PR合并

# 2. 创建版本标签
git tag v1.0.0
git push origin v1.0.0

# 3. 自动触发发布流水线
# Gitea Actions会自动执行发布流程
```

### 3. 部署流程

1. **自动部署**: 推送到main分支自动部署到测试环境
2. **手动部署**: 创建版本标签触发生产环境部署
3. **回滚**: 部署失败时自动回滚到上一个版本

## 监控和日志

### 1. 查看流水线状态

- 在Gitea仓库页面查看Actions标签
- 查看每个任务的执行状态和日志
- 下载构建产物和报告

### 2. 日志分析

```bash
# 查看部署日志
ssh user@server "cd /opt/fastapi-project && tail -f deploy-*.log"

# 查看应用日志
docker-compose logs app

# 查看健康检查
curl -f http://localhost:8000/health
```

### 3. 通知配置

可以配置以下通知方式：
- 邮件通知
- Webhook通知
- Slack通知
- 自定义通知脚本

## 故障排除

### 1. 常见问题

**流水线失败**:
- 检查Gitea版本是否支持Actions
- 验证环境变量配置
- 查看详细错误日志

**Docker构建失败**:
- 检查Dockerfile语法
- 验证网络连接
- 确认Docker服务状态

**部署失败**:
- 检查SSH连接
- 验证服务器权限
- 查看健康检查日志

### 2. 调试命令

```bash
# 检查Gitea Actions状态
curl -H "Authorization: token $GITEA_TOKEN" \
  "https://gitea.example.com/api/v1/repos/username/repo/actions/runs"

# 查看流水线日志
curl -H "Authorization: token $GITEA_TOKEN" \
  "https://gitea.example.com/api/v1/repos/username/repo/actions/runs/{run_id}/logs"

# 手动触发流水线
curl -X POST -H "Authorization: token $GITEA_TOKEN" \
  "https://gitea.example.com/api/v1/repos/username/repo/actions/runs" \
  -d '{"ref":"main","workflow_id":"ci.yml"}'
```

### 3. 性能优化

- 使用缓存减少构建时间
- 并行执行独立任务
- 优化Docker镜像大小
- 使用本地Runner提高性能

## 最佳实践

### 1. 安全考虑

- 使用最小权限原则
- 定期轮换Token
- 加密敏感信息
- 审计访问日志

### 2. 代码质量

- 强制执行代码检查
- 保持高测试覆盖率
- 定期更新依赖
- 使用语义化版本

### 3. 部署策略

- 使用蓝绿部署
- 实施渐进式发布
- 监控关键指标
- 准备回滚计划

### 4. 团队协作

- 建立代码审查流程
- 使用分支保护规则
- 记录部署历史
- 分享最佳实践 