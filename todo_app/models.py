"""Task 与 TodoList：条目类 + 管理类的分工（对照通讯录的 Contact / storage）。

设计要点：
- Task 只管「一条待办」自己的事：校验、转字典、打印
- TodoList 管「一整份清单」：增删完成排序筛选——组合关系（has-a），
  能用组合就别硬上继承（继承是 is-a，待办清单显然不是一种待办）
- 异常体系：AppError 是父类，调用方一把接住
"""

from datetime import datetime
from pathlib import Path


class AppError(Exception):
    """本项目所有业务异常的父类。"""


class EmptyTitleError(AppError):
    """标题不合法：不能为空。"""


class TaskNotFoundError(AppError):
    """序号不合法：找不到对应的任务。"""


class Task:
    def __init__(self, title, done=False, created_at=None):
        title = (title or "").strip()
        if not title:
            raise EmptyTitleError("标题不能为空")

        self.title = title
        self.done = bool(done)
        # 不传就用当前时间；传了就尊重传入（load 读档、测试造数据都用得上）
        self.created_at = created_at or datetime.now()

    def to_dict(self):
        """对象 → 字典。只在 save 前那一刻调用。"""
        return {
            "title": self.title,
            "done": self.done,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, d):
        """字典 → 对象。load 完立刻转，之后全程操作对象。"""
        raw = d.get("created_at")
        return cls(
            title=d.get("title", ""),
            done=d.get("done", False),
            created_at=datetime.fromisoformat(raw) if raw else None,
        )

    def __str__(self):
        mark = "x" if self.done else " "
        return f"[{mark}] {self.title}（创建于 {self.created_at:%Y-%m-%d %H:%M}）"


class TodoList:
    """管理类：拥有一组 Task（组合 has-a）。"""

    def __init__(self, tasks=None):
        # 列表始终按创建时间有序（加分项：list_tasks 按创建时间排序）
        self.tasks = sorted(tasks or [], key=lambda t: t.created_at)

    def get(self, index):
        if not (0 <= index < len(self.tasks)):
            raise TaskNotFoundError("没有这个序号")
        return self.tasks[index]

    def add_task(self, title):
        task = Task(title)  # 校验在 Task 里，管理类不重复写——和通讯录共用校验同理
        self.tasks.append(task)
        self.tasks.sort(key=lambda t: t.created_at)
        return task

    def complete_task(self, index):
        task = self.get(index)
        task.done = True
        return task

    def remove_task(self, index):
        task = self.get(index)
        self.tasks.remove(task)
        return task

    def list_tasks(self):
        """全部任务（已按创建时间从早到晚），返回副本防外部乱改。"""
        return list(self.tasks)

    def filter_done(self, done):
        """加分项：支持传 True / False——只看已完成 / 只看未完成。"""
        return [t for t in self.tasks if t.done == done]

    def export_markdown(self, path):
        """加分项：导出 markdown 清单。"""
        lines = ["# 待办清单", ""]
        for heading, done in (("未完成", False), ("已完成", True)):
            lines.append(f"## {heading}")
            group = self.filter_done(done)
            if group:
                lines.extend(f"- [{'x' if done else ' '}] {t.title}（{t.created_at:%Y-%m-%d}）" for t in group)
            else:
                lines.append("- （无）")
            lines.append("")
        Path(path).write_text("\n".join(lines), encoding="utf-8")
