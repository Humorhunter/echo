#!/usr/bin/env python3
"""msg.py — echo 双 agent 的文件邮箱（传输层 v0.3）

一消息一 JSON 文件，tmp->rename 发布（读方只见完整消息）。
邮箱根：tmp/mailbox/（已被 .gitignore 排除）；事实来源仍在 logs/。
正文 body 用自然语言；头部仅放机器所需最小字段。

命令：
  send --from echo1 --to echo2 --type ASK [--reply-to ID] --body "..."   # 发送
  poll  ME [--all]                      # 列出未读（或含已 done 的）
  wait  ME [--timeout S]                # 轮询直到有未读或超时（sleep 0.5s）
  ack   ME ID                           # 把 <id>.json 移入 done/（确认=处理完）
  status ME                             # 未读/已办统计
"""
import argparse
import json
import os
import sys
import time
import uuid

MAILROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "tmp", "mailbox")
TYPES = ("ASK", "ACK", "INFO", "ERROR")


AGENTS = ("echo1", "echo2")


def inbox_path(agent):
    return os.path.join(MAILROOT, agent)


def _valid_id(mid):
    return mid and "/" not in mid and ".." not in mid and not mid.startswith(".")


def list_ids(agent, include_done=False):
    """返回 [(id, done_flag)]，已办消息从 <agent>/done/ 下合并，按 id（时间前缀）排序。"""
    inf = inbox_path(agent)
    if not os.path.isdir(inf):
        return []
    rows = [(f[:-5], False) for f in os.listdir(inf) if f.endswith(".json")]
    if include_done:
        done = os.path.join(inf, "done")
        if os.path.isdir(done):
            rows += [(f[:-5], True) for f in os.listdir(done) if f.endswith(".json")]
    return sorted(rows)


def read_msg(agent, mid):
    path = os.path.join(inbox_path(agent), mid + ".json")
    if not os.path.exists(path):
        path = os.path.join(inbox_path(agent), "done", mid + ".json")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def cmd_send(a):
    mid = f"{time.time_ns()}-{os.getpid()}-{uuid.uuid4().hex[:6]}"
    msg = {"id": mid, "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "from": a.me, "to": a.to, "type": a.type, "reply_to": a.reply_to, "body": a.body}
    dest = inbox_path(a.to)
    os.makedirs(os.path.join(dest, "done"), exist_ok=True)
    tmp = os.path.join(dest, mid + ".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(msg, f, ensure_ascii=False, indent=1)
        f.flush()
        os.fsync(f.fileno())
    os.rename(tmp, os.path.join(dest, mid + ".json"))
    print(mid)


def cmd_poll(a):
    rows = list_ids(a.me, include_done=a.all)
    for mid, done in rows:
        m = read_msg(a.me, mid)
        print(f"[{'D' if done else 'U'}] {m['id']}  {m['ts']}  {m['from']}/{m['type']}"
              + (f" re:{m['reply_to']}" if m['reply_to'] else ""))
        print(f"    {m['body']}")
    n_unread = sum(1 for _, d in rows if not d)
    sys.stderr.write(f"{n_unread} unread, {len(rows) - n_unread} done\n")


def cmd_wait(a):
    deadline = time.time() + a.timeout
    while not [r for r in list_ids(a.me) if not r[1]]:
        if time.time() > deadline:
            sys.stderr.write("timeout\n")
            return 1
        time.sleep(0.5)
    return cmd_poll(a)


def cmd_ack(a):
    if not _valid_id(a.mid):
        sys.stderr.write(f"invalid id: {a.mid}\n")
        return 2
    inf = inbox_path(a.me)
    src = os.path.join(inf, a.mid + ".json")
    if not os.path.exists(src):
        if os.path.exists(os.path.join(inf, "done", a.mid + ".json")):
            print(f"already acked {a.mid}")
            return 0
        sys.stderr.write(f"no such message: {a.mid}\n")
        return 2
    os.makedirs(os.path.join(inf, "done"), exist_ok=True)
    os.rename(src, os.path.join(inf, "done", a.mid + ".json"))
    print(f"acked {a.mid}")


def cmd_status(a):
    rows = list_ids(a.me, include_done=True)
    n_unread = sum(1 for _, d in rows if not d)
    print(f"{a.me}: {n_unread} unread, {len(rows) - n_unread} done (total {len(rows)})")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send"); s.add_argument("--from", dest="me", required=True, choices=AGENTS)
    s.add_argument("--to", required=True, choices=AGENTS); s.add_argument("--type", default="INFO",
        choices=TYPES); s.add_argument("--reply-to", default=""); s.add_argument("--body", required=True)
    s.set_defaults(fn=cmd_send)
    s = sub.add_parser("poll"); s.add_argument("me"); s.add_argument("--all", action="store_true")
    s.set_defaults(fn=cmd_poll)
    s = sub.add_parser("wait"); s.add_argument("me"); s.add_argument("--timeout", type=float, default=60)
    s.set_defaults(fn=cmd_wait)
    s = sub.add_parser("ack"); s.add_argument("me"); s.add_argument("mid")
    s.set_defaults(fn=cmd_ack)
    s = sub.add_parser("status"); s.add_argument("me")
    s.set_defaults(fn=cmd_status)
    args = p.parse_args()
    sys.exit(args.fn(args) or 0)


if __name__ == "__main__":
    main()
