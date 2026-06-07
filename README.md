<div align="center">

```
██╗   ██╗██╗     ███████╗███████╗    ████████╗██╗   ██╗███╗   ██╗███████╗██████╗
██║   ██║██║     ██╔════╝██╔════╝    ╚══██╔══╝██║   ██║████╗  ██║██╔════╝██╔══██╗
██║   ██║██║     █████╗  ███████╗       ██║   ██║   ██║██╔██╗ ██║█████╗  ██████╔╝
╚██╗ ██╔╝██║     ██╔══╝  ╚════██║       ██║   ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗
 ╚████╔╝ ███████╗███████╗███████║       ██║   ╚██████╔╝██║ ╚████║███████╗██║  ██║
  ╚═══╝  ╚══════╝╚══════╝╚══════╝       ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
```

**Advanced VLESS Config Manager & Clean IP Scanner**

[![Version](https://img.shields.io/badge/version-1.0-cyan?style=flat-square)](.)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)](.)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-@Syncoplex-2CA5E0?style=flat-square&logo=telegram)](https://t.me/Syncoplex)

*A powerful terminal tool to manage, scan, and rebuild VLESS configs with clean Cloudflare IPs.*

</div>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🔁 **Multi-try TCP Probe** | Measures avg / min / jitter / loss across multiple attempts with anti-scanner jitter |
| 🔐 **DPI-safe TLS Test** | Full TLS handshake using neutral Cloudflare SNIs — avoids triggering deep packet inspection |
| 🌐 **CF Trace Probe** | Fetches `/cdn-cgi/trace` to confirm real datacenter (colo) code |
| 🧬 **WebSocket DPI Test** | Two-phase idle-hold + WS upgrade test to detect DPI blocking |
| 📡 **Neighbor Scan** | Automatically discovers nearby clean IPs around good results |
| 🔄 **Rotating SNI** | Cycles through multiple neutral Cloudflare hostnames per scan |
| ⚡ **Speed Test** | Downloads from `speed.cloudflare.com/__down` for accurate throughput measurement |
| 🔬 **xray Validation** | Optional end-to-end Phase 2 test via real xray tunnel |
| 🧠 **AI Memory** | Saves productive subnets and re-injects them on future runs |
| 📦 **Multi-format Parser** | Accepts `vless://` URIs, JSON configs, and Base64-encoded subscriptions |
| 🔁 **Loop Mode** | Press `1` after finishing to start a new session without restarting |

---

## 🖥️ Preview

```
🔮 ⚡ ══════════════════════════════════════════════════════════════════ ⚡ 🔮
  ██╗   ██╗██╗     ███████╗███████╗    ████████╗██╗   ██╗███╗   ██╗███████╗
  ...
🔮 ⚡ ══════════════════════════════════════════════════════════════════ ⚡ 🔮

  Multi-try TCP · DPI-safe TLS · CF Trace · WebSocket Probe · Neighbor Scan · Speed Test

  v1.0  —  by Syncoplex  ·  Telegram: @Syncoplex
```

```
    ┌──────────────────────────────────────────────────────────────────────────┐
    │                         📡  SCAN MATRIX REPORT                          │
    └──────────────────────────────────────────────────────────────────────────┘
    IP                  TCP   Jit  Loss  TLS   HTTP  Colo  WS   KB/s
    ────────────────── ────── ───── ───── ──── ────── ──── ─── ───────
    🔹 104.16.45.12        38    4    0%    ✓      41  AMS   ✓    1840
    🔹 172.64.12.91        52    8    0%    ✓      58  FRA   ✓    1320
    🔹 108.162.201.5       71   12    0%    ✓      79  LHR   ─     890
```

---

## 📋 Requirements

- **Python 3.8+** — no third-party packages required (stdlib only)
- **xray** *(optional)* — for Phase 2 end-to-end validation

---

## 🚀 Quick Start

### Run from source

```bash
# Clone the repository
git clone https://github.com/Syncoplex/vless-tuner.git
cd vless-tuner

# Run directly — no installation needed
python vless_tuner.py
```

### Run the portable EXE (Windows)

Download the latest `.exe` from [Releases](../../releases) and double-click.  
All output files are saved in the same folder as the executable.

---

## 🏗️ Build EXE yourself

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file portable executable
pyinstaller --onefile --console --name "VlessTuner" vless_tuner.py

# Output: dist/VlessTuner.exe
```

> **Note:** Build on the same OS you want to run on.  
> If your antivirus flags it, add the `dist/` folder as an exception — it's a false positive caused by PyInstaller's packing method.

---

## 📖 Usage Guide

```
STEP 0 — Select mode
  [1] Scan & Inject Clean IPs    ← replace all IPs with fresh clean ones
  [2] Format Converter / Rename  ← keep original IPs, just reformat/rename

STEP 1 — Input source
  [1] Online subscription URL
  [2] Manual paste (vless:// / JSON / Base64)

STEP 2 — Name prefix for output configs

STEP 3 — Scan engine  (mode 1 only)
  [1] Auto-scan Cloudflare ranges
  [2] Deep scan — custom size
  [3] Proximity scan around a base IP
  [4] Static IP list
  [5] Skip (no IP injection)

STEP 4 — Protocol optimisation
  [1] AI Auto-Pilot (benchmarks and picks best TLS profile)
  [2] Manual (Fingerprint / ALPN / TFO)
```

### Output files

| File | Contents |
|---|---|
| `PREFIX_YYYY-MM-DD_configs.txt` | Plain `vless://` links, one per line |
| `PREFIX_YYYY-MM-DD_sub.txt` | Base64-encoded subscription (import directly into v2rayNG / Hiddify) |
| `vless_tuner.log` | Debug log for troubleshooting |
| `scan_intelligence.log` | Cached golden subnets for faster future scans |

---

## 🔬 Scan Pipeline Explained

```
IP Candidate
    │
    ▼
Stage 1 ── TCP Multi-try ──────► avg / min / jitter / loss
    │              (3 probes with random jitter between attempts)
    │ alive?
    ▼
Stage 2 ── TLS Handshake ──────► latency · handshake OK?
    │              (neutral SNI: speed.cloudflare.com)
    ▼
Stage 3 ── HTTP /cdn-cgi/trace ► real colo · rotating SNI
    │
    ▼  (optional, when TLS passed)
Stage 4 ── WebSocket Probe ────► idle hold 2s + WS upgrade
    │
    ▼  (TLS ports only)
Stage 5 ── Speed Test ─────────► KB/s via /__down endpoint
    │
    ▼  (optional, requires xray in PATH)
Phase 2 ── xray End-to-End ────► real tunnel connectivity
```

**Quality score** (lower = better) is computed as:

```
score = best_latency
      + (packet_loss  × 3)
      + (jitter       × 0.5)
      + (200  if TLS failed)
      + (150  if WebSocket blocked)
```

---

## ❓ FAQ

**Q: TLS scan shows blocked / -1 ms — are my configs broken?**  
A: No. The scanner uses direct TLS to probe IPs, which is often filtered separately from proxy traffic. Your configs run inside xray which handles TLS internally and bypasses this filtering. Use Phase 2 (xray validation) for a real end-to-end test.

**Q: What is the WebSocket probe testing?**  
A: It checks whether the network path allows long-lived WebSocket connections. A `✗` here means the path may have DPI that resets idle TLS or blocks WS upgrades — which would affect ws-mode VLESS configs on that IP.

**Q: Why does the tool save `scan_intelligence.log`?**  
A: Good IPs cluster in subnets. The tool remembers which /24 blocks produced live results and seeds future scans with those subnets first — making subsequent runs significantly faster.

**Q: I only have one config and filtering left one core — what happens?**  
A: Saturation Mode activates automatically: the tool crosses your top 5 IPs against all four safe ports (443, 8443, 2053, 2096) with randomised fingerprints, generating up to 20 link variants from a single core.

---

## 📁 Project Structure

```
vless-tuner/
├── vless_tuner.py          # Main script
├── README.md               # This file
├── LICENSE                 # MIT License
└── dist/
    └── VlessTuner.exe      # Pre-built Windows portable (see Releases)
```

---

## 📜 License

MIT License — see [LICENSE](LICENSE) for details.

---

<div align="center">

Made with ❤️ by **Syncoplex**  
[![Telegram](https://img.shields.io/badge/Contact-@Syncoplex-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/Syncoplex)

</div>
