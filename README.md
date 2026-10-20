# echo

一个双 agent 自对话进化项目：老板下发任务，两名员工在同一工作区交替协作，用日志、规范与 git 把每一轮的思考沉淀成下一轮可以直接复用的东西。

## 身份

- **老板 / boss**：项目创始人，下发 `tasks/N.md`，验收 `reports/N.md`，保留最终裁决权。
- **echo1**：员工 1，编码“1”，中文名“嚣”，英文名 **Castor**。
- **echo2**：员工 2，编码“2”，中文名“良”，英文名 **Pollux**。

名字来自双子星 Castor / Pollux，也对应《西京杂记》里的“嚣 / 良”。详见 `docs/`。

## 快速上手

```bash
cd /villa/huangyt24-srt/echo
git log --oneline -10          # 最近发生了什么
git status                     # 现在有什么没提交
ls tasks/ && cat tasks/README.md
cat conventions/communication.md
tail -50 logs/$(ls logs | grep task | tail -1)
```

- 工作区：`/villa/huangyt24-srt/echo/`
- 员工会话：tmux `echo1` / `echo2`
- 环境：当前会话使用 `base`（Python 3.13）；共享环境 `echo` 尚未创建，创建后切换
- 权限：两人都有 `huangyt24-srt` 用户级权限，可使用任何工具
- 交流前先读：`conventions/communication.md`、本任务日志末尾、`git diff`
- 通信实验（邮箱/ack）：见 [`scripts/README.md`](scripts/README.md)

## 目录地图

| 目录 | 放什么 | 谁能改 | 说明 |
| --- | --- | --- | --- |
| `tasks/` | 老板按顺序下发的任务 | 老板写正文；员工只维护 README | 任务编号即交付编号 |
| `reports/` | 每个任务的老板可读报告 | 员工 | 收尾时定稿，附建议与请求 |
| `logs/` | 按时间戳存档的交流过程 | 员工 | 追加式，不删改历史 |
| `conventions/` | 双方约定的协作规范 | 员工 | 分场景、可版本化 |
| `docs/` | 外部引用资料与身份材料 | 员工 | 记录来源与用途 |
| `scripts/` | 可执行工具（邮箱、校验等） | 员工 | 标准库优先，单文件优先 |
| `tmp/` | 临时文件 | 员工 | 不进 git |

每个目录都有自己的 README，先看目录 README 再动手。

## 工作流

1. 老板在 `tasks/N.md` 下发任务，可能指定截止时间与模式。
2. 员工读取任务、规范、日志末尾和 `git status` / `git diff`。
3. 两人交替工作：一轮结束在日志里点名交棒；共享文件遵守“单写窗口”。
4. 每轮尽量留下**可复用沉淀**：规范条目、脚本、可验证结论，而不是只留下“同意”。
5. 收尾时写 `reports/N.md`（目标 / 过程 / 结论与产出 / 风险与待办 / 待老板裁决），另一人复核。
6. 按 `conventions/git.md` 提交；老板验收后任务关闭。

## 模式

- **mode0**：自然讨论，双方认为话题结束即可收尾。
- **mode1**：讨论到老板指定时间；以 `date -u` 统一时间，截止前 10 分钟停止新话题并交接，**不要超时**。

## 规范索引

- [`conventions/communication.md`](conventions/communication.md)：时间、通道、单写窗口、有效轮次、进化证据。
- [`conventions/git.md`](conventions/git.md)：提交粒度、消息格式、push 与失败处理。
- 新增规范请先在 `conventions/README.md` 登记，再落文件。

## 当前阶段

task1 已关闭，交付了协作规范与交流机制。task2 正在进行：仓库结构规范化、README 体系、双 agent 通信效率。

> 给刚接手的 agent：先读日志末尾，不要从第一行读起；先看 `git status`，不要假设工作区是干净的；不确定的结论写成可证伪的判断，而不是模糊的共识。
