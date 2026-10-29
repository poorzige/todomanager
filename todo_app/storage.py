"""存取模块：load / save + .bak 备份（逻辑从 contact_app 的 storage.py 直接搬）。

两道保险：
- load 读到坏 json → 先备份成 .bak，再按空列表启动（批改 21「静默清空」的修复）
- save 覆盖前 → 先把旧文件备份成 .bak（万一这次写坏，上一份好数据还在）
"""

import json
import logging
import shutil
from pathlib import Path

# 数据文件放在 todo_app 的上一级（todo-manager 根目录）。用 __file__ 定位，
# 无论从哪个目录启动，路径都不会漂。
BASE_DIR = Path(__file__).resolve().parent.parent
FILE_PATH = BASE_DIR / "tasks.json"
BAK_PATH = BASE_DIR / "tasks.json.bak"


def load():
    """读 json，返回字典列表。"""
    if not FILE_PATH.exists():
        return []

    try:
        return json.loads(FILE_PATH.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        # 损坏 ≠ 清空：先备份再按空列表继续
        shutil.copy2(FILE_PATH, BAK_PATH)
        logging.error("tasks.json 损坏，原文件已备份为 tasks.json.bak，本次按空列表启动")
        return []


def save(tasks_as_dicts):
    """接收 to_dict() 之后的字典列表，写回 json。"""
    if FILE_PATH.exists():
        shutil.copy2(FILE_PATH, BAK_PATH)
    FILE_PATH.write_text(
        json.dumps(tasks_as_dicts, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
