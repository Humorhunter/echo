# Scoped Day 1：可运行的 MCP 权限层 MVP

日期：2026-10-20 ｜ 执行：echo1 ｜ 对抗测试：echo2

## 1. 现在能做什么

`scoped/` 已从方案落成可运行代码：

- **策略引擎**：TOML/JSON/YAML，`allow / ask / deny`，按顺序 first-match；支持工具 glob、参数 equals/contains/regex、SQL 关键词集合。
- **MCP stdio 代理**：在客户端与真实 MCP server 之间逐帧裁决；deny 不转发、ask 走审批、allow 原样转发；批处理 fail-closed。
- **审计收据**：JSONL + SHA-256 hash chain；`scoped audit verify` 能抓单条篡改；secret key 默认脱敏，长值截断。
- **CLI**：`init` / `check` / `proxy` / `audit verify` / `audit tail`。
- **Demo**：`python3 examples/demo.py` 展示“允许普通读、拦 `.env`、拦 `DROP TABLE`、允许 `SELECT`、审批 shell”，最后验证 5 张收据。
- **文档**：`README.md`、`docs/threat-model.md`、`docs/receipts.md`；Apache-2.0 + NOTICE。

## 2. 验证结果

```text
python3 -m unittest discover -s tests -v          -> 14/14 OK
tests/adversarial/run.py (echo2)                  -> 3 PASS, exit 0
examples/demo.py                                  -> 2 blocked, 3 allowed, 5 receipts verified
```

Demo 实际输出：

```text
read_file examples/scoped.toml       ALLOWED
read_file .env                       BLOCKED scoped: deny by deny-secret-paths
run_sql DROP TABLE users             BLOCKED scoped: deny by deny-destructive-sql
run_sql SELECT 1                     ALLOWED
shell echo hi                        ALLOWED
OK: 5 receipts verified
```

## 3. echo2 对抗测试的两个真 bug（已修）

1. **B1 批处理帧崩代理**：`proxy.py` 对 JSON-RPC array 取 `.get` 触发 AttributeError，exit 1、请求丢失、无审计。
   - 修复：批处理逐条裁决；任一条 deny/ask-deny 则整批 fail-closed，不转发 server，逐条回 error、逐条记 receipt。
2. **B2 默认策略放行 `.env`**：`DEFAULT_POLICY` 无条件 allow `read_file`，与“禁 `.env`”承诺冲突。
   - 修复：增加 `deny-secret-paths` 且放在 allow 前；覆盖 `.env`、`.env.*`、`.ssh/*`、`credentials`、`authorized_keys`、`id_rsa`、`id_ed25519`、`.aws/credentials`；普通文件仍 allow。
3. **redact 漏标**（S）：补 `bearer/pwd/credentials/session_key/private_key/access_key/refresh_token`。

同时修正 echo2 测试脚本的一个测试 bug：`cli_main()` 返回 int 而非抛 `SystemExit`，B2 原会永远判成 `code=0`；改为 `code = cli_main() or 0`，不改变测试意图。

## 4. 诚实边界

- 只覆盖 **MCP stdio**；Claude Code 的 shell/文件调用还没接 `PreToolUse` hook，不能用“全拦截”宣传。
- **不是 sandbox**；允许的 MCP server 仍能读它能读的一切。
- SQL 是关键词启发式，不是 parser；生产应配只读 DB role。
- 审计链防编辑、不防整文件重写；外部锚定是后续工作。
- 当前审批用 `/dev/tty`；无 TTY 时 ask 默认 deny。

## 5. 下一步（不等老板指令，按计划推进）

1. 做 Claude Code `PreToolUse` hook 适配器：同一策略/收据引擎，先覆盖 shell 与文件路径。
2. 用一个真实 stdio MCP server 做端到端 demo（优先 filesystem server），录 30 秒可复现命令。
3. 把 `examples/demo.py` 变成 CI smoke test；补 batch/ask/tamper 的回归。
4. 再做 HTTP egress allowlist 与 Postgres 只读 adapter；外部收据锚定放最后。

## 6. 需要老板看的

- 项目在 `scoped/`，可直接跑：`cd scoped && python3 examples/demo.py`。
- 目前没有要老板决策的阻塞项；按“至少完成整个项目、要有用”继续，不追 star 叙事。
