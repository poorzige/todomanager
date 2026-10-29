# todo-manager —— 命令行待办管理器

W2 周六大作业：Task 条目类 + TodoList 管理类（组合）、tasks.json 持久化（损坏自动 .bak）、logging 分级日志、pytest 全绿。

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

## 开发中遇到的 3 个问题及解决

1. **pip install 卡死不动**：本机系统代理残留 `127.0.0.1:31181`，pip 自动继承，流量全灌向一个已经关掉的代理口。解决：加 `NO_PROXY=*` 绕开（PowerShell：`$env:NO_PROXY="*"`），并换清华镜像 `-i https://pypi.tuna.tsinghua.edu.cn/simple`。
2. **`python todo_app/app.py` 报 ModuleNotFoundError**：直接运行包内文件时，模块搜索路径里没有项目根，`import todo_app` 找不到。解决：统一从项目根用 `python -m todo_app.app`（和通讯录是同一个坑）。
3. **json 损坏会把数据静默清空**：load 遇到坏 json 若直接返回空列表，下一次 save 就把好数据覆盖没了——错误被「吞掉」且不可逆。解决：load 失败先把坏文件复制成 .bak 再按空列表启动；save 覆盖前也先备份——两头都有后悔药。

## 换台电脑怎么跑（部署的雏形）

    git clone <本仓库地址>
    cd todo-manager
    python -m venv .venv
    .venv\Scripts\activate
    pip install -r requirements.txt
    python -m todo_app.app

venv 不进仓库（.gitignore 已排除）：它只是本机依赖副本，任何机器凭 requirements.txt 三步重建。

## 首次发布到 GitHub（独立仓库，不是 learning-log 的子目录）

    git init
    git add .gitignore todo_app/__init__.py && git commit -m "chore: 项目骨架"
    git add todo_app/models.py      && git commit -m "feat: Task 与 TodoList 模型"
    git add todo_app/storage.py     && git commit -m "feat: 持久化与 .bak 备份"
    git add todo_app/app.py         && git commit -m "feat: 菜单与日志"
    git add conftest.py tests/      && git commit -m "test: 8 个用例全绿"
    git add README.md requirements.txt && git commit -m "docs: 运行说明与问题记录"
    git branch -M main
    git remote add origin <你的GitHub仓库地址>
    git push -u origin main

> tasks.json / todo.md / app.log 是运行时产物，已在 .gitignore 里，不会被提交。
