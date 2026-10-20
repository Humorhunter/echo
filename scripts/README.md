# scripts

可执行工具。工具只做传输与校验，事实来源永远是 `logs/` 与 git。

## msg.py — echo1/echo2 的文件邮箱（通信实验两臂中的臂②）

设计依据：`docs/agent-communication.md`（三篇论文结论）+ `conventions/communication.md` v1.3。

- 存储：一消息一 JSON 文件，`tmp/mailbox/<to>/<id>.json`；`id = <time_ns>-<pid>-<rand6>`
- 原子性：先写 `.json.tmp` + fsync，再 `rename` 发布——读方只见完整消息
- 去重与排序：`id` 自带毫秒/纳秒时间前缀，无全局锁；重放安全
- read 证据 ≠ 唤醒证据：tmux `send-keys` 只是铃；`ack`（移入 `done/`）才是已处理
- 正文字段 `body` 一律自然语言（NLT 复现研究支持：结构做信封、语义留正文）

### 常用命令

```bash
# 发送（echo1 -> echo2）
python scripts/msg.py send --from echo1 --to echo2 --type ASK --body "请复核 reports/2.md"

# 看未读（每封带 U/D 标记）
python scripts/msg.py poll echo2

# 等新消息（60s 超时）
python scripts/msg.py wait echo2 --timeout 60

# 处理完回执（移入 done/）
python scripts/msg.py ack echo2 <id>

# 首尾统计
python scripts/msg.py status echo2
```

### 与现行规范的衔接

1. 日志 `logs/YYYY-MM-DD-task*.md` 仍是唯一事实来源；邮箱消息用于**通知与流转**，重要结论仍须落日志。
2. `type` 取值：`ASK`（需对方行动）/ `ACK`（已完成回执，`reply_to` 指向原 id）/ `INFO` / `ERROR`。
3. 与单写窗口兼容：收件方处理完后用 `ACK` 类型消息交棒，被点名方再动共享文件。
