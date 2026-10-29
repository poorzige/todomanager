"""菜单和 main：UI 只负责跟用户对话，业务在 TodoList，存取在 storage。

运行方式（在 todo-manager 目录下）：
    python -m todo_app.app

也支持直接运行：
    python todo_app/app.py
"""

import logging
import sys
from pathlib import Path


def ensure_project_root_on_path():
    """让直接运行脚本时也能解析顶层包 todo_app。"""
    project_root = Path(__file__).resolve().parent.parent
    root_str = str(project_root)
    if root_str not in sys.path:
        sys.path.insert(0, root_str)


ensure_project_root_on_path()

from todo_app import storage
from todo_app.models import AppError, Task, TaskNotFoundError, TodoList

# print 只留给用户，日志进文件（app.log 在项目根目录）
logging.basicConfig(
    level=logging.DEBUG,
    filename=str(storage.BASE_DIR / "app.log"),
    encoding="utf-8",
    format="%(asctime)s %(levelname)s %(message)s",
)

MENU = """
===== 待办管理器 todo-manager =====
1. 添加      2. 查看全部
3. 完成      4. 删除
5. 筛选      6. 导出 markdown
0. 退出
"""


def persist(todo_list):
    """save 前才 to_dict：对象在内存里流转，只有落盘那一刻变字典。"""
    storage.save([t.to_dict() for t in todo_list.tasks])


def show(tasks, title=""):
    if title:
        print(f"--- {title} ---")
    if not tasks:
        print("（没有任务）")
        return
    for i, task in enumerate(tasks, 1):
        print(f"{i}. {task}")  # 触发 Task.__str__


def pick_index(prompt):
    raw = input(f"{prompt}（序号，q 取消）: ").strip()
    if raw == "q":
        return None
    if not raw.isdigit():
        print("请输入数字序号")
        return None
    return int(raw) - 1  # 屏幕上给用户看的是 1 起，内部是 0 起


def add(todo_list):
    while True:
        title = input("任务标题: ").strip()
        try:
            task = todo_list.add_task(title)
            break
        except AppError as e:
            # 抛异常的担责任（Task），接异常的给体面（这里）——程序不崩，让用户重输
            print(f"✗ {e}，请重输")
            logging.warning("校验失败：%s", e)
    persist(todo_list)
    logging.info("添加任务：%s", task.title)
    print(f"✓ 已添加：{task}")


def complete(todo_list):
    show(todo_list.list_tasks(), "全部任务")
    if not todo_list.tasks:
        return
    idx = pick_index("要完成第几条")
    if idx is None:
        return
    try:
        task = todo_list.complete_task(idx)
    except TaskNotFoundError as e:
        print(f"✗ {e}")
        return
    persist(todo_list)
    logging.info("完成任务：%s", task.title)
    print(f"✓ 已完成：{task}")


def remove(todo_list):
    show(todo_list.list_tasks(), "全部任务")
    if not todo_list.tasks:
        return
    idx = pick_index("要删除第几条")
    if idx is None:
        return
    try:
        target = todo_list.get(idx)
    except TaskNotFoundError as e:
        print(f"✗ {e}")
        return
    # 自测第 3 条：删除必须二次确认
    sure = input(f"确认删除「{target.title}」？（y 确认，其他取消）: ").strip().lower()
    if sure != "y":
        print("已取消")
        return
    todo_list.remove_task(idx)
    persist(todo_list)
    logging.info("删除任务：%s", target.title)
    print(f"✓ 已删除 {target.title}")


def filter_menu(todo_list):
    choice = input("看 1 未完成 / 2 已完成: ").strip()
    if choice == "1":
        show(todo_list.filter_done(False), "未完成")
    elif choice == "2":
        show(todo_list.filter_done(True), "已完成")
    else:
        print("没有这个选项")


def export(todo_list):
    path = storage.BASE_DIR / "todo.md"
    todo_list.export_markdown(path)
    logging.info("导出 markdown：%s", path.name)
    print(f"✓ 已导出：{path}")


def main():
    tasks = []
    for d in storage.load():
        try:
            tasks.append(Task.from_dict(d))
        except (AppError, ValueError) as e:
            # 单条记录不合法：跳过并记 warning，不让一个坏条目弄崩整个程序
            logging.warning("跳过一条不合法的记录 %s：%s", d, e)
    todo_list = TodoList(tasks)
    print(f"已载入 {len(todo_list.tasks)} 条任务（数据文件：{storage.FILE_PATH.name}）")

    while True:
        print(MENU)
        choice = input("> ").strip()
        if choice == "1":
            add(todo_list)
        elif choice == "2":
            show(todo_list.list_tasks(), "全部任务（按创建时间）")
        elif choice == "3":
            complete(todo_list)
        elif choice == "4":
            remove(todo_list)
        elif choice == "5":
            filter_menu(todo_list)
        elif choice == "6":
            export(todo_list)
        elif choice == "0":
            print("再见")
            break
        else:
            print("没有这个选项")


if __name__ == "__main__":
    main()
