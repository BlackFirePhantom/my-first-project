# 小说阅读器 Linux 服务器调试与维护指南

本指南整理了在服务器（Azure VM）上维护和调试该小说阅读器项目时可能用到的常用命令，涵盖服务控制、日志查询、依赖维护、网络检测及代码同步等模块。

---

## 1. 服务生命周期管理 (systemd)

项目已配置为 systemd 系统服务，服务名称为 `novel-reader`。

*   **查看服务状态**：检查服务是否正在运行、已占用内存、PID 等。
    ```bash
    sudo systemctl status novel-reader
    ```
*   **重启服务**（修改代码/更新 Git 后必用）：
    ```bash
    sudo systemctl restart novel-reader
    ```
*   **启动服务**：
    ```bash
    sudo systemctl start novel-reader
    ```
*   **停止服务**：
    ```bash
    sudo systemctl stop novel-reader
    ```
*   **设置开机自启**：
    ```bash
    sudo systemctl enable novel-reader
    ```
*   **禁用开机自启**：
    ```bash
    sudo systemctl disable novel-reader
    ```

---

## 2. 日志监控与分析 (journalctl)

通过 systemd 收集的日志是排查报错（如解析失败、网络超时等）的关键入口。

*   **实时追踪最新日志**（最常用）：
    ```bash
    sudo journalctl -u novel-reader -f
    ```
*   **查看最近 $N$ 行日志**（不自动挂起，一次性输出）：
    ```bash
    sudo journalctl -u novel-reader -n 100 --no-pager
    ```
*   **只查看错误（Error）级别日志**：
    ```bash
    sudo journalctl -u novel-reader -p err --no-pager
    ```
*   **查看自今天以来的所有日志**：
    ```bash
    sudo journalctl -u novel-reader --since today --no-pager
    ```

---

## 3. 虚拟环境与 Playwright 管理

如果遇到浏览器环境报错或依赖缺失问题，可以使用 these 命令。

*   **进入项目目录**：
    ```bash
    cd /home/azureuser/my-first-project
    ```
*   **激活 Python 虚拟环境**：
    ```bash
    source .venv/bin/activate
    ```
*   **安装/修复 Playwright 系统依赖库**（当 Chromium 因缺失系统动态库报错时使用）：
    ```bash
    playwright install-deps
    ```
*   **手动下载 Chromium 浏览器内核**：
    ```bash
    playwright install chromium
    ```
*   **退出虚拟环境**：
    ```bash
    deactivate
    ```

---

## 4. Git 部署与代码同步

在本地开发电脑（Windows）上修改代码并 push 到 GitHub 后，在服务器上拉取并覆盖的命令。

*   **进入目录并拉取最新更改**：
    ```bash
    cd /home/azureuser/my-first-project
    git pull origin main
    ```
*   **强行覆盖本地修改**（如果服务器上的代码不小心被改乱了，用 GitHub 的最新版本强制覆盖）：
    > [!WARNING]
    > 这将丢弃服务器上所有未提交的本地修改，谨慎使用。
    ```bash
    git fetch --all
    git reset --hard origin/main
    ```

---

## 5. 端口与系统资源检测

*   **检查 5000 端口占用情况**（如果 Flask 启动报端口被占用错误）：
    ```bash
    sudo lsof -i :5000
    # 或者
    sudo netstat -tulnp | grep 5000
    ```
*   **强制关闭占用 5000 端口的进程**：
    ```bash
    sudo kill -9 <进程PID>
    ```
*   **查看服务器内存使用情况**（监控 Playwright 浏览器是否占用内存过多）：
    ```bash
    free -h
    ```
*   **实时查看 CPU 和内存占用进程**：
    ```bash
    top
    # 或者如果安装了 htop
    htop
    ```
