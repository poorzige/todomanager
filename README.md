# todo-manager —— 命令行待办管理器

Task 条目类 + TodoList 管理类（组合）、tasks.json 持久化（损坏自动 .bak）、logging 分级日志、pytest 全绿。

## 运行（venv 三步）

在项目根目录（todo-manager/）：

    python -m venv .venv
    .venv\Scripts\activate            # PowerShell 用：.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    python -m todo_app.app

> 必须用 `python -m todo_app.app` 运行；直接 `python todo_app/app.py` 会 ModuleNotFoundError（包要从包外用 -m 运行）。

## 功能

- 添加（空标题被 EmptyTitleError 拒绝，程序不崩，让用户重输）
- 查看全部（按创建时间排序）、筛选（未完成 / 已完成）
- 完成、删除（删除有二次确认）
- 导出 markdown 清单（todo.md）——加分项
- 每次改动自动落盘 tasks.json；load 读到坏文件、save 覆盖之前，都会先备份 .bak

## 测试

    python -m pytest -v

8 个用例（要求 ≥ 5，必含损坏备份测试）：空标题拒绝、字典往返、增改、True/False 筛选、按时间排序、非法序号、缺文件返回 []、损坏自动 .bak。

