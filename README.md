# 📖 小说阅读器 (Novel Reader)

本项目是一个基于 Flask 开发的私人自建小说阅读器，旨在提供纯净、无广告、响应迅速的极致阅读体验。支持多源小说搜索、个人书架、阅读进度精确保存、以及应对高级反爬的自动渲染机制。

---

## 🛠️ 服务器端运行模式与部署架构 (Server Deployment)

为了便于后续开发人员和 AI 助理快速接管、维护服务器，以下是该项目在生产服务器上的部署信息：

### 1. 运行环境与路径
*   **服务器类型**：Azure VM (Ubuntu / Linux)
*   **部署路径**：`/home/azureuser/my-first-project`
*   **Python 虚拟环境**：`/home/azureuser/my-first-project/.venv`
*   **运行主入口**：`web_app.py`
*   **运行端口**：`5000`

### 2. 服务管理与进程守护 (Systemd)
项目在服务器上已配置为 `systemd` 系统服务，实现了后台常驻、故障自动重启、开机自启以及标准日志收集。
*   **服务名称**：`novel-reader`
*   **配置文件路径**：`/etc/systemd/system/novel-reader.service`
*   **运行用户**：`azureuser`

### 3. 服务器端常用命令（极简速查）
在服务器上，一旦本地代码提交并推送到 GitHub 后，只需执行以下命令即可完成部署更新：

```bash
# 1. 进入服务器项目根目录
cd /home/azureuser/my-first-project

# 2. 从 GitHub 拉取最新代码
git pull origin main

# 3. 重启小说阅读器系统服务 (自动重新加载新代码)
sudo systemctl restart novel-reader

# 4. 查看当前服务运行状态与最新日志
sudo systemctl status novel-reader
```

> 💡 **更详尽的服务器维护手册**：请参阅项目根目录下的 [server_debugging_guide.md](server_debugging_guide.md) 文件，其中包含了详尽的日志追踪 (`journalctl`)、环境依赖管理 (`Playwright`) 以及端口与资源监测命令。

---

## 💻 本地运行与开发指南

### 1. 环境准备
项目依赖 Python 3.8+ 及 Playwright 渲染引擎。
```bash
# 安装 Python 依赖
pip install -r requirements.txt

# 安装 Playwright 浏览器内核
playwright install chromium
```

### 2. 初始密码设置
由于本项目内置了访问保护机制，在首次启动前需要初始化管理员密码：
```bash
python setup_password.py
```
这将在本地自动生成一个 `.env` 配置文件，包含加密后的密码哈希和 `SECRET_KEY`。

### 3. 运行本地服务
```bash
python web_app.py
```
*   默认本地服务地址：`http://localhost:5000`

---

## 🔒 项目安全机制说明
1.  **Session 登录鉴权**：所有主要阅读界面和数据交互 API 都经过 `@login_required` 安全装饰器保护，未授权的请求将被重定向至登录页。
2.  **环境变量与密钥隔离**：密钥（`SECRET_KEY`）和密码哈希（`PASSWORD_HASH`）保存在 `.env` 环境变量中，该文件已配置在 `.gitignore` 中，极不推荐且绝不会被上传至公共代码仓库。
3.  **防刷安全拦截**：设置了 API 的合理访问频率，同时采用了“写临时文件 + 原子替换”机制存储书架数据，规避了并发读写文件损坏的风险。
