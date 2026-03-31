# 王者荣耀体验服自动兑换系统

### King of Glory Experience Server Auto-Exchange System

[中文](#中文) | [English](#english)

---

## 中文

### 项目简介

这是一个基于 Flask 的王者荣耀体验服奖励自动兑换系统，主要功能包括：

- **自动兑换**：每日定时（每3小时）自动使用存储的 Cookie 兑换皮肤/英雄碎片
- **更新监控**：定时（每小时）检测体验服更新并推送通知
- **Web 管理界面**：支持提交 cURL、查询账号状态、管理账号
- **企业微信通知**：兑换结果实时推送至企业微信

### 技术栈

| 类别 | 技术 |
|------|------|
| 后端框架 | Flask 2.1.2 |
| 数据库 | MySQL + SQLAlchemy + Flask-Migrate |
| 定时任务 | Flask-APScheduler |
| 前端 UI | LayUI |
| 部署 | Docker / Docker Compose |

### 项目结构

```
WZRYTYF/
├── app.py                  # Flask 应用入口
├── config/
│   ├── config.py           # 配置文件
│   ├── models.py           # 数据库模型
│   ├── decorators.py       # 装饰器
│   └── exts.py            # 扩展初始化
├── blueprints/
│   ├── index.py           # 主页面与兑换逻辑
│   ├── search.py          # 搜索查询
│   └── exchange.py        # 体验服更新检测
├── templates/             # HTML 模板
├── static/                # 静态资源
├── utils/
│   ├── utils.py           # 工具函数
│   └── serverchan.py      # Server 酱推送
├── migrations/            # 数据库迁移
└── requirements.txt       # 依赖列表
```

### 快速开始

#### 1. 环境要求

- Python 3.7+
- MySQL 5.7+
- Docker (可选)

#### 2. 本地运行

```bash
# 安装依赖
pip install -r requirements.txt

# 配置数据库（创建 secret.json）
# 参考 config/config.py 中的配置格式

# 初始化数据库
flask db upgrade

# 启动服务
python app.py
# 或
flask run --host=0.0.0.0 --port=5005
```

#### 3. Docker 部署

```bash
# 启动服务
docker-compose up -d

# 访问服务
http://localhost:5700
```

### 配置说明

创建 `config/secret.json` 文件：

```json
{
  "HOSTNAME": "localhost",
  "PORT": "3306",
  "DATABASE": "wzry_db",
  "USERNAME": "root",
  "PASSWORD": "your_password",
  "SECRET_KEY": "your_secret_key",
  "SCHEDULER_API_PREFIX": "/scheduler",
  "MAIL_SERVER": "smtp.example.com",
  "MAIL_PORT": 465,
  "MAIL_USE_TLS": false,
  "MAIL_USE_SSL": true,
  "MAIL_DEBUG": true,
  "MAIL_USERNAME": "your_email@example.com",
  "MAIL_PASSWORD": "email_password",
  "MAIL_DEFAULT_SENDER": "your_email@example.com",
  "WECOM_CID": "your_corp_id",
  "WECOM_AID": "your_agent_id",
  "WECOM_SECRET": "your_agent_secret",
  "WECOM_TOUID": "@all",
  "WECOM_SECRET_KEY": "your_key",
  "SERVER_KEY": "your_server_key"
}
```

### 功能说明

#### cURL 提交
在浏览器中打开体验服官网 → F12 → 选择兑换请求 → Copy as cURL(bash) → 粘贴到网页表单

#### 定时任务
- `SkinDebris`: 每 3 小时执行一次自动兑换
- `CheckWZRY`: 每 1 小时检测体验服更新

#### 账号状态
| 状态码 | 说明 |
|--------|------|
| 801 | 新增 |
| 802 | 更新 |
| 803 | 过期 |
| 804 | 成功 |
| 805 | 体验币不足 |
| 806 | 暂停 |
| 807 | 重启 |
| 808 | 发放完 |

---

## English

### Project Overview

A Flask-based automated exchange system for King of Glory (王者荣耀) Experience Server rewards. Key features:

- **Auto Exchange**: Automatically exchange skin/hero fragments using stored cookies (runs every 3 hours)
- **Update Monitoring**: Check Experience Server updates hourly and send notifications
- **Web Management UI**: Submit cURL, query account status, manage accounts
- **WeChat Work Notifications**: Real-time notification of exchange results

### Tech Stack

| Category | Technology |
|----------|------------|
| Backend | Flask 2.1.2 |
| Database | MySQL + SQLAlchemy + Flask-Migrate |
| Scheduler | Flask-APScheduler |
| Frontend | LayUI |
| Deployment | Docker / Docker Compose |

### Project Structure

```
WZRYTYF/
├── app.py                  # Flask application entry
├── config/
│   ├── config.py           # Configuration
│   ├── models.py           # Database models
│   ├── decorators.py      # Decorators
│   └── exts.py            # Extensions init
├── blueprints/
│   ├── index.py           # Main page & exchange logic
│   ├── search.py          # Search & query
│   ├── exchange.py        # Update monitoring
├── templates/             # HTML templates
├── static/                # Static resources
├── utils/
│   ├── utils.py          # Utilities
│   └── serverchan.py     # Server Chan push
├── migrations/           # Database migrations
└── requirements.txt      # Dependencies
```

### Quick Start

#### 1. Requirements

- Python 3.7+
- MySQL 5.7+
- Docker (optional)

#### 2. Local Run

```bash
# Install dependencies
pip install -r requirements.txt

# Configure database (create secret.json)
# See config/config.py for format

# Initialize database
flask db upgrade

# Start service
python app.py
# or
flask run --host=0.0.0.0 --port=5005
```

#### 3. Docker Deployment

```bash
# Start service
docker-compose up -d

# Access service
http://localhost:5700
```

### Configuration

Create `config/secret.json`:

```json
{
  "HOSTNAME": "localhost",
  "PORT": "3306",
  "DATABASE": "wzry_db",
  "USERNAME": "root",
  "PASSWORD": "your_password",
  "SECRET_KEY": "your_secret_key",
  "SCHEDULER_API_PREFIX": "/scheduler",
  "MAIL_SERVER": "smtp.example.com",
  "MAIL_PORT": 465,
  "MAIL_USE_TLS": false,
  "MAIL_USE_SSL": true,
  "MAIL_DEBUG": true,
  "MAIL_USERNAME": "your_email@example.com",
  "MAIL_PASSWORD": "email_password",
  "MAIL_DEFAULT_SENDER": "your_email@example.com",
  "WECOM_CID": "your_corp_id",
  "WECOM_AID": "your_agent_id",
  "WECOM_SECRET": "your_agent_secret",
  "WECOM_TOUID": "@all",
  "WECOM_SECRET_KEY": "your_key",
  "SERVER_KEY": "your_server_key"
}
```

### Feature Guide

#### cURL Submission
Open Experience Server website → F12 → Select exchange request → Copy as cURL(bash) → Paste to web form

#### Scheduled Tasks
- `SkinDebris`: Auto exchange every 3 hours
- `CheckWZRY`: Check updates every 1 hour

#### Account Status Codes
| Code | Description |
|------|-------------|
| 801 | Added |
| 802 | Updated |
| 803 | Expired |
| 804 | Success |
| 805 | Insufficient Experience Coins |
| 806 | Paused |
| 807 | Restarted |
| 808 | Out of Stock |

---

### License

MIT License