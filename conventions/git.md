# git 规范 v1.1

老板已把 commit / push 权限交给员工。权限越大，越要留下能看懂的历史。

## 1. 基本原则

- 一主题一 commit：不把“改 README”“写脚本”“修格式”混在一起。
- 只 stage 自己确认过的文件；禁止无脑 `git add -A`。
- 提交前检查：`git status`、`git diff`、`git diff --cached`。
- 不提交密钥、token、个人隐私、未授权数据、生成缓存。
- 不改写已推送的历史；不 force push。
- 工作区在交接时应是干净的，或明确说明哪些文件故意未提交。

## 2. Commit 消息

格式：

```
task<N>: <一句话主题>

<可选正文：为什么改、验证了什么、有哪些限制>
```

示例：

```
task2: standardize READMEs and add git convention
task2: add JSONL message transport prototype
task1: deliver collaboration spec v1.2, task1 log and report
```

- 主题用祈使句或名词短语，不超过 72 字符。
- 正文只在需要解释“为什么”时写；不要复述 diff。
- 中文或英文均可，同一任务内保持一致。

## 3. 粒度与顺序

推荐顺序：

1. 规范 / 结构变更；
2. 代码或脚本；
3. 文档与报告；
4. 收尾时的日志与链接修正。

- 逻辑独立的改动分开提交，便于回滚。
- 较大的实验先提交一个可运行的最小版本，再迭代。
- 提交前跑一次与改动相关的检查（脚本能跑、链接存在、格式没坏）。

## 4. Push

- 远端：`origin` 使用 SSH（`git@github.com:Humorhunter/echo.git`）。本机 HTTPS 凭据助手不可用，不要改回 HTTPS。
- 日常：`git push origin main`；SSH 已验证可用（2026-10-20，`Hi Humorhunter!`）。
- 时机：一个整体任务收尾前，或老板明确要求时。
- push 前先 `git fetch` / 确认远端状态，避免覆盖他人提交。
- push 失败时：
  1. 保留本地 commit，不 `reset --hard`；
  2. 在 `logs/` 写 `ERROR:` 块，记录完整错误、原因、影响、处理；
  3. **不要查找、猜测或索取凭据**；
  4. 继续可做的本地工作，在报告中说明“已本地提交、未推送”。

## 5. 禁止事项

- `git push --force` / `--force-with-lease`（除非老板明确要求且确认影响）。
- 提交 `tmp/`、`__pycache__/`、模型权重、数据集等大文件。
- 把凭据写进 remote URL、脚本或文档。
- 用 `git commit --amend` 修改已推送的提交。
- 为了“让历史好看”而压缩掉真实的失败与回滚。

## 6. 与报告的关系

`reports/N.md` 的“结论与产出”应能对应到 commit（哈希或消息），让老板可以从历史直接复核。没有 commit 的产出，视为未固化。
