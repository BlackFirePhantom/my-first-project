# -*- coding: utf-8 -*-
"""
密码设置工具 - 运行一次即可
用法: python setup_password.py
会交互式地要求输入密码，然后将哈希值写入 .env 文件。
"""

import getpass
import os
import secrets
from pathlib import Path

from werkzeug.security import generate_password_hash


ENV_FILE = Path(__file__).parent / ".env"


def load_env() -> dict:
    """读取现有 .env 文件（若存在）"""
    env = {}
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text("utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, val = line.partition("=")
                env[key.strip()] = val.strip()
    return env


def save_env(env: dict):
    """将键值对写入 .env 文件"""
    lines = ["# 自动生成 — 请勿手动编辑，也不要提交到 Git\n"]
    for key, val in env.items():
        lines.append(f"{key}={val}\n")
    ENV_FILE.write_text("".join(lines), "utf-8")


def main():
    print("=" * 50)
    print("  小说阅读器 - 密码设置工具")
    print("=" * 50)

    env = load_env()

    # 生成或保留 SECRET_KEY
    if "SECRET_KEY" not in env:
        env["SECRET_KEY"] = secrets.token_hex(64)
        print("[OK] 已生成新的随机 SECRET_KEY")
    else:
        print("[OK] 保留现有 SECRET_KEY")

    # 设置密码
    while True:
        pwd = getpass.getpass("\n请输入新密码（输入时不显示）: ")
        if len(pwd) < 4:
            print("[ERROR] 密码至少需要 4 个字符，请重试。")
            continue
        pwd_confirm = getpass.getpass("请再次输入密码确认: ")
        if pwd != pwd_confirm:
            print("[ERROR] 两次输入不一致，请重试。")
            continue
        break

    env["PASSWORD_HASH"] = generate_password_hash(pwd)
    save_env(env)

    print(f"\n[OK] 密码已设置，配置已保存到 {ENV_FILE}")
    print("  现在可以运行 python web_app.py 启动应用了。\n")


if __name__ == "__main__":
    main()
