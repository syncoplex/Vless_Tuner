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

---

## 📋 پیش‌نیازها

- **Python 3.8+** — بدون نیاز به هیچ پکیج خارجی (فقط stdlib)
- **xray** *(اختیاری)* — برای تأیید end-to-end در فاز ۲

---

## 🚀 شروع سریع

### اجرا از سورس

```bash
# کلون کردن مخزن
git clone https://github.com/Syncoplex/vless-tuner.git
cd vless-tuner

# اجرای مستقیم — نیاز به نصب نیست
python vless_tuner.py
```

### اجرای EXE آماده (ویندوز)

آخرین فایل `.exe` را از [Releases](../../releases) دانلود کنید و روی آن دابل‌کلیک کنید.  
تمام فایل‌های خروجی در همان پوشه‌ای که EXE قرار دارد ذخیره می‌شوند.

---

## 🏗️ ساخت EXE خودت

```bash
# نصب PyInstaller
pip install pyinstaller

# ساخت یک فایل اجرایی portable
pyinstaller --onefile --console --name "VlessTuner" vless_tuner.py

# خروجی: dist/VlessTuner.exe
```

> **توجه:** روی همان سیستم‌عاملی build کنید که می‌خواهید اجرا کنید.  
> اگر آنتی‌ویروس آن را flag کرد، پوشه `dist/` را به استثناها اضافه کنید — این یک false positive است که به روش پکیج‌سازی PyInstaller مربوط می‌شود.

---

## 📖 راهنمای استفاده

```
STEP 0 — انتخاب حالت
  [1] Scan & Inject Clean IPs    ← همه IP‌ها را با IP‌های تمیز جدید جایگزین کن
  [2] Format Converter / Rename  ← IP‌های اصلی را نگه دار، فقط فرمت/نام را تغییر بده

STEP 1 — منبع ورودی
  [1] آدرس URL سابسکریپشن آنلاین
  [2] پیست دستی (vless:// / JSON / Base64)

STEP 2 — پیشوند نام برای کانفیگ‌های خروجی

STEP 3 — موتور اسکن  (فقط در حالت 1)
  [1] اسکن خودکار رنج‌های Cloudflare
  [2] Deep scan — اندازه دلخواه
  [3] Proximity scan اطراف یک IP پایه
  [4] لیست IP استاتیک
  [5] رد شدن (بدون IP injection)

STEP 4 — بهینه‌سازی پروتکل
  [1] AI Auto-Pilot (بنچمارک و انتخاب بهترین پروفایل TLS)
  [2] دستی (Fingerprint / ALPN / TFO)
```

### فایل‌های خروجی

| فایل | محتوا |
|---|---|
| `PREFIX_YYYY-MM-DD_configs.txt` | لینک‌های `vless://` ساده، هر کدام در یک خط |
| `PREFIX_YYYY-MM-DD_sub.txt` | سابسکریپشن Base64 (مستقیم در v2rayNG / Hiddify وارد کنید) |
| `vless_tuner.log` | لاگ debug برای عیب‌یابی |
| `scan_intelligence.log` | subnet‌های golden کش‌شده برای اسکن سریع‌تر در آینده |

---

## 🔬 توضیح pipeline اسکن

```
IP Candidate
    │
    ▼
Stage 1 ── TCP Multi-try ──────► avg / min / jitter / loss
    │              (3 probe با jitter تصادفی بین تلاش‌ها)
    │ alive?
    ▼
Stage 2 ── TLS Handshake ──────► latency · handshake OK?
    │              (SNI خنثی: speed.cloudflare.com)
    ▼
Stage 3 ── HTTP /cdn-cgi/trace ► colo واقعی · rotating SNI
    │
    ▼  (اختیاری، وقتی TLS پاس شد)
Stage 4 ── WebSocket Probe ────► idle hold 2s + WS upgrade
    │
    ▼  (فقط روی TLS ports)
Stage 5 ── Speed Test ─────────► KB/s از endpoint دانلود
    │
    ▼  (اختیاری، نیاز به xray در PATH)
Phase 2 ── xray End-to-End ────► اتصال واقعی از طریق تانل
```

**امتیاز کیفیت** (کمتر = بهتر) به این صورت محاسبه می‌شود:

```
score = best_latency
      + (packet_loss  × 3)
      + (jitter       × 0.5)
      + (200  اگر TLS شکست خورد)
      + (150  اگر WebSocket بلاک بود)
```

---

## ❓ سوالات متداول

**س: TLS scan نشان می‌دهد blocked / ‎-1 ms — آیا کانفیگ‌هایم خراب هستند؟**  
ج: نه. اسکنر برای probe کردن IP‌ها از TLS مستقیم استفاده می‌کند که اغلب جداگانه فیلتر می‌شود. کانفیگ‌های شما داخل xray اجرا می‌شوند که TLS را به‌صورت داخلی مدیریت می‌کند و از این فیلتر عبور می‌کند. برای تست واقعی از Phase 2 (xray validation) استفاده کنید.

**س: WebSocket probe دقیقاً چه چیزی را تست می‌کند؟**  
ج: بررسی می‌کند که آیا مسیر شبکه اجازه اتصالات WebSocket طولانی‌مدت را می‌دهد یا نه. یک `✗` در اینجا یعنی ممکن است DPI روی این IP اتصالات TLS بیکار را reset کند یا WS upgrade را بلاک کند — که روی کانفیگ‌های VLESS در حالت ws تأثیر می‌گذارد.

**س: چرا ابزار فایل `scan_intelligence.log` را ذخیره می‌کند؟**  
ج: IP‌های خوب در subnet‌ها خوشه‌بندی می‌شوند. ابزار به یاد می‌آورد که کدام بلوک‌های /24 نتایج زنده داشتند و اسکن‌های بعدی را با آن subnet‌ها seed می‌کند — که اجراهای بعدی را به‌طور قابل‌توجهی سریع‌تر می‌کند.

**س: فقط یک کانفیگ دارم و بعد از dedup یک core باقی ماند — چه اتفاقی می‌افتد؟**  
ج: Saturation Mode به‌صورت خودکار فعال می‌شود: ابزار ۵ IP برتر شما را روی چهار port ایمن (443، 8443، 2053، 2096) با fingerprint‌های تصادفی‌شده cross می‌کند و تا ۲۰ variant لینک از یک core تولید می‌کند.

---

## 📁 ساختار پروژه

```
vless-tuner/
├── vless_tuner.py          # اسکریپت اصلی
├── README.md               # راهنمای انگلیسی
├── README.fa.md            # این فایل (راهنمای فارسی)
├── LICENSE                 # مجوز MIT
└── dist/
    └── VlessTuner.exe      # نسخه portable آماده ویندوز (در Releases)
```

---

## 📜 مجوز

مجوز MIT — برای جزئیات به [LICENSE](LICENSE) مراجعه کنید.

---

<div align="center">

ساخته شده با ❤️ توسط **Syncoplex**  
[![Telegram](https://img.shields.io/badge/Contact-@Syncoplex-2CA5E0?style=for-the-badge&logo=telegram)](https://t.me/Syncoplex)

</div>
