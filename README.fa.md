<div align="center">

```
██╗   ██╗██╗     ███████╗███████╗    ████████╗██╗   ██╗███╗   ██╗███████╗██████╗
██║   ██║██║     ██╔════╝██╔════╝    ╚══██╔══╝██║   ██║████╗  ██║██╔════╝██╔══██╗
██║   ██║██║     █████╗  ███████╗       ██║   ██║   ██║██╔██╗ ██║█████╗  ██████╔╝
╚██╗ ██╔╝██║     ██╔══╝  ╚════██║       ██║   ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗
 ╚████╔╝ ███████╗███████╗███████║       ██║   ╚██████╔╝██║ ╚████║███████╗██║  ██║
  ╚═══╝  ╚══════╝╚══════╝╚══════╝       ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝
```

**مدیر پیشرفته کانفیگ VLESS و اسکنر IP تمیز**

[![Version](https://img.shields.io/badge/version-1.0-cyan?style=flat-square)](.)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20Linux%20%7C%20macOS-lightgrey?style=flat-square)](.)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Telegram](https://img.shields.io/badge/Telegram-@Syncoplex-2CA5E0?style=flat-square&logo=telegram)](https://t.me/Syncoplex)

*یک ابزار ترمینال قدرتمند برای مدیریت، اسکن و بازسازی کانفیگ‌های VLESS با IP‌های تمیز Cloudflare.*

</div>

---

<div dir="rtl">

## ✨ قابلیت‌ها

| قابلیت | توضیح |
|---|---|
| 🔁 **Multi-try TCP Probe** | اندازه‌گیری avg / min / jitter / loss در چند تلاش با jitter ضد-اسکنر |
| 🔐 **TLS ایمن در برابر DPI** | دست‌دهی TLS کامل با SNI‌های خنثی Cloudflare — بدون فعال‌کردن DPI |
| 🌐 **CF Trace Probe** | دریافت `/cdn-cgi/trace` برای تأیید کد datacenter واقعی (colo) |
| 🧬 **WebSocket DPI Test** | تست دو‌مرحله‌ای idle-hold + WS upgrade برای تشخیص بلاک DPI |
| 📡 **Neighbor Scan** | کشف خودکار IP‌های تمیز مجاور نزدیک به نتایج خوب |
| 🔄 **Rotating SNI** | چرخش روی چند hostname خنثی Cloudflare در هر اسکن |
| ⚡ **Speed Test** | دانلود از `speed.cloudflare.com/__down` برای اندازه‌گیری دقیق throughput |
| 🔬 **xray Validation** | تست اختیاری end-to-end فاز ۲ از طریق تانل واقعی xray |
| 🧠 **AI Memory** | ذخیره subnet‌های مفید و تزریق مجدد در اجراهای بعدی |
| 📦 **Multi-format Parser** | پشتیبانی از URI‌های `vless://`، کانفیگ JSON و سابسکریپشن Base64 |
| 🔁 **Loop Mode** | بعد از پایان، با فشردن `1` یک جلسه جدید بدون راه‌اندازی مجدد شروع کن |

---

## 🖥️ پیش‌نمایش

</div>

<div dir="ltr">

```
🔮 ⚡ ══════════════════════════════════════════════════════════════════ ⚡ 🔮
  ██╗   ██╗██╗     ███████╗███████╗    ████████╗██║   ██║███╗   ██╗███████╗
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

</div>

---

<div dir="rtl">

## 📋 پیش‌نیازها

- **Python 3.8+** — بدون نیاز به هیچ پکیج خارجی (فقط stdlib)
- **xray** *(اختیاری)* — برای تأیید end-to-end در فاز ۲

---

## 🚀 شروع سریع

### اجرا از سورس

</div>

<div dir="ltr">

```bash
# Clone the repository
git clone https://github.com/Syncoplex/vless-tuner.git
cd vless-tuner

# Run directly — no installation needed
python vless_tuner.py
```

</div>

<div dir="rtl">

### اجرای EXE آماده (ویندوز)

آخرین فایل `.exe` را از [Releases](../../releases) دانلود کنید و روی آن دابل‌کلیک کنید.
تمام فایل‌های خروجی در همان پوشه‌ای که EXE قرار دارد ذخیره می‌شوند.

---

## 🏗️ ساخت EXE خودت

</div>

<div dir="ltr">

```bash
# Install PyInstaller
pip install pyinstaller

# Build single-file portable executable
pyinstaller --onefile --console --name "VlessTuner" vless_tuner.py

# Output: dist/VlessTuner.exe
```

</div>

<div dir="rtl">

> **توجه:** روی همان سیستم‌عاملی build کنید که می‌خواهید اجرا کنید.
> اگر آنتی‌ویروس آن را flag کرد، پوشه `dist/` را به استثناها اضافه کنید — این یک false positive ناشی از روش پکیج‌سازی PyInstaller است.

---

## 📖 راهنمای استفاده

</div>

<div dir="ltr">

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

</div>

<div dir="rtl">

### فایل‌های خروجی

| فایل | محتوا |
|---|---|
| `PREFIX_YYYY-MM-DD_configs.txt` | لینک‌های `vless://` ساده، هر کدام در یک خط |
| `PREFIX_YYYY-MM-DD_sub.txt` | سابسکریپشن Base64 (مستقیم در v2rayNG / Hiddify وارد کنید) |
| `vless_tuner.log` | لاگ debug برای عیب‌یابی |
| `scan_intelligence.log` | subnet‌های golden کش‌شده برای اسکن سریع‌تر در آینده |

---

## 🔬 توضیح Pipeline اسکن

</div>

<div dir="ltr">

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

</div>

<div dir="rtl">

**امتیاز کیفیت** (کمتر = بهتر) به این صورت محاسبه می‌شود:

</div>

<div dir="ltr">

```
score = best_latency
      + (packet_loss  × 3)
      + (jitter       × 0.5)
      + (200  if TLS failed)
      + (150  if WebSocket blocked)
```

</div>

---

<div dir="rtl">

## ❓ سوالات متداول

**س: TLS scan نشان می‌دهد blocked / ‎-1 ms — آیا کانفیگ‌هایم خراب هستند؟**

ج: نه. اسکنر برای probe کردن IP‌ها از TLS مستقیم استفاده می‌کند که اغلب جداگانه فیلتر می‌شود. کانفیگ‌های شما داخل xray اجرا می‌شوند که TLS را به‌صورت داخلی مدیریت می‌کند و از این فیلتر عبور می‌کند. برای تست واقعی از Phase 2 (xray validation) استفاده کنید.

**س: WebSocket probe دقیقاً چه چیزی را تست می‌کند؟**

ج: بررسی می‌کند که آیا مسیر شبکه اجازه اتصالات WebSocket طولانی‌مدت را می‌دهد یا نه. یک `✗` در اینجا یعنی ممکن است DPI روی این IP اتصالات TLS بیکار را reset کند یا WS upgrade را بلاک کند — که روی کانفیگ‌های VLESS در حالت ws تأثیر می‌گذارد.

**س: چرا ابزار فایل `scan_intelligence.log` را ذخیره می‌کند؟**

ج: IP‌های خوب در subnet‌ها خوشه‌بندی می‌شوند. ابزار به یاد می‌آورد که کدام بلوک‌های /24 نتایج زنده داشتند و اسکن‌های بعدی را با آن subnet‌ها seed می‌کند — که اجراهای بعدی را به‌طور قابل‌توجهی سریع‌تر می‌کند.

**س: فقط یک کانفیگ دارم و بعد از dedup یک core باقی ماند — چه اتفاقی می‌افتد؟**

ج: Saturation Mode به‌صورت خودکار فعال می‌شود: ابزار ۵ IP برتر شما را روی چهار port ایمن (443، 8443، 2053، 2096) با fingerprint‌های تصادفی cross می‌کند و تا ۲۰ variant لینک از یک core تولید می‌کند.

---

## 📁 ساختار پروژه

</div>

<div dir="ltr">

```
vless-tuner/
├── vless_tuner.py          # Main script
├── README.md               # English guide
├── README.fa.md            # Persian guide (این فایل)
├── LICENSE                 # MIT License
└── dist/
    └── VlessTuner.exe      # Pre-built Windows portable (see Releases)
```

</div>

---

<div dir="rtl">

## 📜 مجوز

مجوز MIT — برای جزئیات به [LICENSE](LICENSE) مراجعه کنید.

</div>

---

<div align="center">

ساخته شده با ❤️ توسط **Syncoplex**
[![Telegram](https://img.shields.io/badge/Contact-@Syncoplex-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/Syncoplex)

</div>
