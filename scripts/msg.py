#!/usr/bin/env python3
"""msg.py — echo 双 agent 的文件邮箱（传输层 v0.2）

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


def inbox_path(agent):
    return os.path.join(MAILROOT, agent)


def list_ids(agent, include_done=False):
    inf = inbox_path(agent)
    if not os.path.isdir(inf):
        return []
    ids = sorted(f[:-5] for f in os.listdir(inf) if f.endswith(".json"))
    if include_done:
        return ids
    return [i for i in ids if not _acked(agent, i)]


def _acked(agent, mid):
    return os.path.exists(os.path.join(inbox_path(agent), "done", mid + ".json"))


def read_msg(agent, mid):
    with open(os.path.join(inbox_path(agent), mid + ".json"), encoding="utf-8") as f:
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
    for mid in list_ids(a.me, include_done=a.all):
        m = read_msg(a.me, mid)
        flag = "D" if _acked(a.me, mid) else "U"
        print(f"[{flag}] {m['id']}  {m['ts']}  {m['from']}/{m['type']}"
              + (f" re:{m['reply_to']}" if m['reply_to'] else ""))
        print(f"    {m['body']}")
    n = len(list_ids(a.me))
    sys.stderr.write(f"{n} unread, {len(list_ids(a.me, True)) - n} done\n")


def cmd_wait(a):
    deadline = time.time() + a.timeout
    while not list_ids(a.me):
        if time.time() > deadline:
            sys.stderr.write("timeout\n")
            return 1
        time.sleep(0.5)
    return cmd_poll(a)


def cmd_ack(a):
    inf = inbox_path(a.me)
    os.makedirs(os.path.join(inf, "done"), exist_ok=True)
    os.rename(os.path.join(inf, a.mid + ".json"), os.path.join(inf, "done", a.mid + ".json"))
    print(f"acked {a.mid}")


def cmd_status(a):
    print(f"{a.me}: {len(list_ids(a.me))} unread, {len(list_ids(a.me, True))} total")


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    s = sub.add_parser("send"); s.add_argument("--from", dest="me", required=True)
    s.add_argument("--to", required=True); s.add_argument("--type", default="INFO",
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
