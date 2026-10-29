#!/usr/bin/env python3
"""从自己的旧朋友圈存档里按关键词找相似的圈，给写新圈当语气样本。

用法: python3 -I find_my_posts.py --file 存档路径 关键词1 关键词2 ... [--n 6] [--since 2023]

存档格式：纯文本，每条圈以「YYYY-MM-DD HH:MM」单独一行开头，下面是正文。
没有时间戳的存档，按空行分段，每段算一条。
"""
import re, sys, os


def load(path):
    t = open(os.path.expanduser(path), encoding="utf8", errors="ignore").read()
    parts = re.split(r"\n(?=\d{4}-\d{2}-\d{2} \d{2}:\d{2}\n)", t)
    out = []
    for p in parts:
        m = re.match(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2})\n(.*)", p, re.S)
        if m:
            out.append((m[1], m[2].strip()))
    if not out:  # 没有时间戳：按空行分段
        out = [("", b.strip()) for b in re.split(r"\n\s*\n", t) if b.strip()]
    return out


def main():
    args, n, since, path = [], 6, "0000", None
    it = iter(sys.argv[1:])
    for a in it:
        if a in ("--n", "--since", "--file"):
            v = next(it, None)
            if v is None:
                sys.exit(f"{a} 后面要跟一个值\n{__doc__}")
            if a == "--n":
                if not v.isdigit():
                    sys.exit(f"--n 后面要跟数字，收到的是：{v}")
                n = int(v)
            elif a == "--since": since = v
            else: path = v
        else: args.append(a)
    if not args or not path:
        print(__doc__); return
    if not os.path.exists(os.path.expanduser(path)):
        sys.exit(f"找不到存档：{path}")
    scored = []
    for ts, body in load(path):
        if (ts and ts[:4] < since) or len(body) < 40:
            continue
        hits = sum(body.count(k) for k in args)
        kinds = sum(1 for k in args if k in body)
        if kinds:
            # 关键词覆盖面优先，其次命中次数，再偏向近年
            scored.append((kinds, hits, ts, body))
    scored.sort(key=lambda x: (x[0], x[1], x[2]), reverse=True)
    for kinds, hits, ts, body in scored[:n]:
        print(f"==== {ts}  (命中{kinds}词)\n{body[:900]}\n")


if __name__ == "__main__":
    main()
