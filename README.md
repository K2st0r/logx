<div align="center">

# logx

**Smart Log Analyzer — Find errors, top patterns, and time distribution in one command**

[![Python](https://img.shields.io/badge/Python-3.8+-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Version](https://img.shields.io/badge/Version-1.0.0-purple)](https://github.com/K2st0r/logx)
[![Donate](https://img.shields.io/badge/Donate-USDT-red)](#donate)

</div>

### 🎯 One-liner

```bash
logx access.log
# → Errors: 12, Warnings: 45, Peak: 14:00, Top pattern: "GET /api/users"
```

### ✨ Features

| Feature | Description |
|---------|-------------|
| **Error detection** | Auto-identifies ERROR/WARN/INFO levels |
| **Pattern analysis** | Finds most common log patterns (with normalization) |
| **Time distribution** | Histogram of log volume by hour |
| **HTTP status** | Breakdown of 2xx/3xx/4xx/5xx responses |
| **Pipe support** | `tail -f app.log | logx - -e` for live monitoring |

### 🚀 Usage

```bash
# Full analysis
logx access.log

# Show error samples
logx errors.log -e

# Top 20 patterns
logx server.log -t 20

# Time distribution
logx app.log --time

# HTTP status breakdown
logx nginx.log --status

# Pipe from live log
tail -f app.log | logx - -e

# Everything at once
logx access.log -e -t 10 --time --status
```

### 📊 Sample Output

```
logx — Log Analysis Report
──────────────────────────────────────────────────
File: nginx/access.log
Lines: 15,432  Size: 1,234,567 bytes
──────────────────────────────────────────────────

Level Summary:
  Errors:       42  (0.3%)
  Warnings:    156  (1.0%)
  Info:     14,892  (96.5%)

Top 5 Patterns:
   1. [ 45.2%] █████████████████████████
      GET /api/v1/users <*> HTTP/1.1 <*>
   2. [ 20.1%] █████████
      POST /api/v1/login <*> HTTP/1.1 <*>

Time Distribution:
  08:00  ████████  1,200
  12:00  ████████████████████████  4,567  ← Peak
  20:00  ██████  890
```

### 🎯 Use Cases

- Production incident triage — instantly see error count and samples
- SEO log analysis — find 404s and broken links
- Performance auditing — identify slow endpoints by pattern frequency
- Daily operations — quick health check before standups

## 💎 Donate

**USDT (ERC20):** `0xAfe9B67B1DF618FAeD32dC71E3458cf549f26697`

---

*MIT License · Made with ❤️ by [K2st0r](https://github.com/K2st0r)*
