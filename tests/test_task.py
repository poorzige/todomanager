"""todo-manager 的测试：8 个用例（要求 ≥ 5，必含损坏备份）。

在 todo-manager 目录下运行：
    python -m pytest -v
"""

import sys
from datetime import datetime
from pathlib import Path

import pytest

from todo_app import app, storage
from todo_app.models import EmptyTitleError, Task, TaskNotFoundError, TodoList


def test_bootstrap_adds_project_root_to_path(monkeypatch):
    project_root = str(Path(__file__).resolve().parents[1])
    monkeypatch.setattr(sys, "path", [p for p in sys.path if p != project_root])
    app.ensure_project_root_on_path()
    assert project_root in sys.path


def test_empty_title_rejected():
    # 空标题（含纯空格）→ 必须抛 EmptyTitleError
    with pytest.raises(EmptyTitleError):
        Task("   ")


def test_task_round_trip():
    # 往返测试：存出去再读回来，字段一分不丢（created_at 用固定值才好比）
    d = {"title": "买牛奶", "done": False, "created_at": "2026-10-24T10:00:00"}
    assert Task.from_dict(d).to_dict() == d


def test_add_and_complete():
    todo_list = TodoList()
    todo_list.add_task("写周报")
    assert len(todo_list.tasks) == 1
    todo_list.complete_task(0)
    assert todo_list.tasks[0].done is True


def test_filter_done_true_false():
    # 加分项：filter_done 支持传 True / False
    todo_list = TodoList()
    todo_list.add_task("a")
    todo_list.add_task("b")
    todo_list.add_task("c")
    todo_list.complete_task(1)
    assert [t.title for t in todo_list.filter_done(True)] == ["b"]
    assert len(todo_list.filter_done(False)) == 2


def test_list_sorted_by_created_at():
    # 加分项：list_tasks 按创建时间排序（故意乱序传入）
    old = Task("旧任务", created_at=datetime(2026, 10, 20))
    new = Task("新任务", created_at=datetime(2026, 10, 26))
    todo_list = TodoList([new, old])
    assert [t.title for t in todo_list.list_tasks()] == ["旧任务", "新任务"]


def test_invalid_index_rejected():
    todo_list = TodoList()
    todo_list.add_task("a")
    with pytest.raises(TaskNotFoundError):
        todo_list.complete_task(5)


def test_load_missing_file(tmp_path, monkeypatch):
    # FILE_PATH 指向不存在的路径 → load 返回 []，而不是崩溃
    monkeypatch.setattr(storage, "FILE_PATH", tmp_path / "nope.json")
    assert storage.load() == []


def test_corrupt_file_backed_up(tmp_path, monkeypatch):
    # 自测第 4 条的守护：坏 json → 返回 [] 且 .bak 出现——数据安全从此有测试站岗
    bad = tmp_path / "tasks.json"
    bad.write_text("{这不是合法json", encoding="utf-8")
    monkeypatch.setattr(storage, "FILE_PATH", bad)
    monkeypatch.setattr(storage, "BAK_PATH", tmp_path / "tasks.json.bak")
    assert storage.load() == []
    assert (tmp_path / "tasks.json.bak").exists()
