#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
logx — Smart Log Analyzer
========================================
Quick analysis of any log file. Find errors, top patterns,
and time distribution in one command.

Usage:
  logx access.log                      # Full analysis
  logx errors.log -e                   # Show only errors
  logx app.log -t 10                   # Top 10 patterns
  logx server.log --time               # Time distribution
  logx nginx.log --status --top 20     # HTTP status breakdown

License: MIT
Donate:  0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697 (USDT ERC20)
"""
import argparse, collections, re, sys, os
from typing import Dict, List

__version__ = "1.0.0"
__wallet__  = "0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697"

# Common error/level patterns
ERROR_PATTERNS = [
    (r'\b(ERROR|FATAL|CRITICAL|FAIL|FAILED|500|502|503)\b', 'error'),
    (r'\b(WARN|WARNING|4[0-9]{2})\b', 'warn'),
    (r'\b(INFO|DEBUG|TRACE|200|201|204|30[0-9])\b', 'info'),
]

# HTTP status extraction
STATUS_RE = re.compile(r'"\s+(\d{3})\s')

def read_lines(path: str) -> List[str]:
    if path == "-":
        return sys.stdin.read().splitlines()
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        return f.read().splitlines()

def analyze_errors(lines: List[str]) -> Dict:
    counts = {"error": 0, "warn": 0, "info": 0}
    details = {"error": [], "warn": []}
    for line in lines:
        for pattern, level in ERROR_PATTERNS:
            if re.search(pattern, line, re.IGNORECASE):
                counts[level] += 1
                if level in ("error", "warn") and len(details[level]) < 20:
                    details[level].append(line.strip()[:120])
                break
    return {"counts": counts, "samples": details}

def analyze_patterns(lines: List[str], top_n: int = 20) -> List:
    """Find most common log message patterns."""
    # Normalize: replace timestamps, IDs, IPs with placeholders
    norm = re.compile(r'\d{4}[-/]\d{2}[-/]\d{2}|\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}|[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}|\d+')
    counter = collections.Counter()
    for line in lines:
        cleaned = norm.sub("<*>", line).strip()
        if len(cleaned) > 10:
            counter[cleaned[:160]] += 1
    return counter.most_common(top_n)

def analyze_time(lines: List[str]) -> Dict:
    """Analyze time distribution of log entries."""
    time_re = re.compile(r'(\d{2}):(\d{2}):(\d{2})|(\d{2}):(\d{2})')
    hours = collections.Counter()
    minutes = collections.Counter()
    for line in lines:
        m = time_re.search(line)
        if m:
            if m.group(1):
                h, mi = int(m.group(1)), int(m.group(2))
                hours[h] += 1
                minutes[(h, mi)] += 1
    return {"hours": sorted(hours.items()), "peak_hour": hours.most_common(1)[0] if hours else None}

def analyze_status(lines: List[str]) -> Dict:
    """HTTP status code breakdown."""
    status = collections.Counter()
    for line in lines:
        m = STATUS_RE.search(line)
        if m:
            code = m.group(1)
            # Group by category
            cat = code[0] + "xx"
            status[cat] += 1
            status[code] += 1
    return dict(status.most_common())

def main():
    parser = argparse.ArgumentParser(
        prog="logx",
        description="Smart log analyzer — errors, patterns, time distribution",
        epilog="Examples:\n  logx access.log\n  logx errors.log -e\n  logx server.log -t 20 --time\n  tail -f app.log | logx - -e",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("input", help="Log file path (or '-' for stdin)")
    parser.add_argument("-e", "--errors", action="store_true", help="Show error/warn samples")
    parser.add_argument("-t", "--top", type=int, default=0, metavar="N", help="Show top N message patterns")
    parser.add_argument("--time", action="store_true", help="Show time distribution")
    parser.add_argument("--status", action="store_true", help="Show HTTP status breakdown")
    parser.add_argument("--version", action="version", version=f"logx {__version__}")
    
    args = parser.parse_args()
    lines = read_lines(args.input)
    
    if not lines:
        print("No log lines found.")
        return
    
    total = len(lines)
    total_bytes = sum(len(l.encode()) for l in lines)
    
    print(f"\n  logx — Log Analysis Report")
    print(f"  {'─' * 50}")
    print(f"  File: {args.input}")
    print(f"  Lines: {total:,}  Size: {total_bytes:,} bytes")
    print(f"  {'─' * 50}")
    
    # Error analysis (always show summary)
    err = analyze_errors(lines)
    c = err["counts"]
    total_level = sum(c.values())
    print(f"\n  Level Summary:")
    print(f"    Errors:   {c['error']:>6,}  ({c['error']/total*100:.1f}%)" if total else "")
    print(f"    Warnings: {c['warn']:>6,}  ({c['warn']/total*100:.1f}%)" if total else "")
    print(f"    Info:     {c['info']:>6,}  ({c['info']/total*100:.1f}%)" if total else "")
    print(f"    Other:    {total - total_level:>6,}  ({(total - total_level)/total*100:.1f}%)" if total else "")
    
    if args.errors:
        if err["samples"]["error"]:
            print(f"\n  Error samples:")
            for s in err["samples"]["error"][:10]:
                print(f"    {s}")
        if err["samples"]["warn"]:
            print(f"\n  Warning samples:")
            for s in err["samples"]["warn"][:5]:
                print(f"    {s}")
    
    if args.top > 0:
        patterns = analyze_patterns(lines, args.top)
        print(f"\n  Top {args.top} Patterns:")
        for i, (p, count) in enumerate(patterns, 1):
            pct = count / total * 100
            bar = "█" * min(50, int(pct * 2))
            print(f"  {i:2d}. [{pct:5.1f}%] {bar}")
            print(f"      {p[:100]}")
    
    if args.time:
        at = analyze_time(lines)
        if at["hours"]:
            print(f"\n  Time Distribution (by hour):")
            max_h = max(c for _, c in at["hours"])
            for hour, count in at["hours"]:
                bar = "█" * int(count / max_h * 40)
                print(f"    {hour:02d}:00  {bar}  {count:>6,}")
            if at["peak_hour"]:
                print(f"\n  Peak: {at['peak_hour'][0]:02d}:00 ({at['peak_hour'][1]:,} entries)")
    
    if args.status:
        stats = analyze_status(lines)
        if stats:
            print(f"\n  HTTP Status Breakdown:")
            for code, count in sorted(stats.items()):
                pct = count / total * 100
                print(f"    {code:<6} {count:>6,}  ({pct:.1f}%)")
    
    print(f"\n  {'─' * 50}")
    print(f"  logx v{__version__} | Donate: {__wallet__[:10]}...\n")

if __name__ == "__main__":
    main()
