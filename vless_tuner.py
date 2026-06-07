"""
VLESS Tuner - Advanced Edition
================================
Author   : SyncoPlex
Telegram : @SyncoPlex
Version  : 1.0
License  : MIT
"""

import json, urllib.parse, urllib.request, sys, os, threading, socket, ssl
import time, base64, random, logging, subprocess, tempfile
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Optional

# ─── ANSI Colors ───────────────────────────────────────────────────────────────
CLR_RESET   = "\033[0m";  CLR_TITLE   = "\033[1;36m";  CLR_STEP    = "\033[1;35m"
CLR_INFO    = "\033[0;33m"; CLR_SUCCESS = "\033[1;32m"; CLR_WARN    = "\033[1;93m"
CLR_ERROR   = "\033[1;31m"; CLR_TEXT    = "\033[0;37m"; CLR_CYAN    = "\033[0;36m"
CLR_GRAY    = "\033[90m";   CLR_MAGENTA = "\033[0;35m"; CLR_BLUE    = "\033[1;34m"
CLR_WHITE   = "\033[1;37m"

# ─── Constants ─────────────────────────────────────────────────────────────────
TOOL_NAME         = "VLESS Tuner"
VERSION           = "1.0"
AUTHOR            = "SyncoPlex"
TELEGRAM          = "@SyncoPlex"
INTELLIGENCE_FILE = "scan_intelligence.log"
DEFAULT_WORKERS   = 100
SAFE_PORTS        = [443, 8443, 2053, 2096]
PING_TIMEOUT      = 1.5
TLS_TIMEOUT       = 3.0
HTTP_TIMEOUT      = 5.0
WS_IDLE_HOLD      = 2.0
PROBE_TRIES       = 3

# Rotating SNI list — neutral Cloudflare hostnames for DPI-safe probing
SCAN_SNIS = [
    "speed.cloudflare.com",
    "www.cloudflare.com",
    "cloudflare.com",
    "1.1.1.1.cdn.cloudflare.net",
    "blog.cloudflare.com",
]
SCAN_SNI = SCAN_SNIS[0]

# Built-in Cloudflare CIDR ranges (fallback when live fetch fails)
CF_IP_RANGES_BUILTIN = [
    "173.245.48.0/20", "103.21.244.0/22", "103.22.200.0/22", "103.31.4.0/22",
    "141.101.64.0/18", "108.162.192.0/18", "190.93.240.0/20", "188.114.96.0/20",
    "197.234.240.0/22", "198.41.128.0/17", "162.158.0.0/15",
    "104.16.0.0/13",   "104.24.0.0/14",   "172.64.0.0/13",  "131.0.72.0/22",
]

FINGERPRINT_MAP = {"1": "chrome", "2": "safari", "3": "firefox", "4": "edge", "5": "random"}

logging.basicConfig(
    filename="vless_tuner.log", level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
log = logging.getLogger(__name__)

if os.name == "nt":
    os.system("")


# ─── Data Classes ──────────────────────────────────────────────────────────────
@dataclass
class VlessNode:
    """Represents a single parsed VLESS configuration node."""
    user_id: str;  address: str;  port: int;    host: str
    path:    str;  security: str; network: str; remarks: str


@dataclass
class ScanResult:
    """Holds complete scan metrics for one candidate IP address."""
    ip:              str
    tcp_latency_ms:  float = -1.0   # Average TCP round-trip time
    tcp_jitter_ms:   float = -1.0   # TCP latency standard deviation
    tcp_loss_pct:    float = 100.0  # Packet loss percentage
    tls_latency_ms:  float = -1.0   # Full TLS handshake duration
    tls_valid:       bool  = False   # Whether TLS handshake succeeded
    http_latency_ms: float = -1.0   # HTTP /cdn-cgi/trace response time
    colo:            str   = ""      # Cloudflare datacenter code
    http_ok:         bool  = False   # Whether HTTP trace returned valid data
    ws_ok:           bool  = False   # Whether WebSocket upgrade was accepted
    ws_tested:       bool  = False   # Whether WS test was attempted
    speed_kbps:      float = -1.0   # Download speed in KB/s
    alive:           bool  = False   # Whether IP is reachable at all

    @property
    def best_latency(self) -> float:
        """Return the most accurate available latency metric."""
        for v in [self.http_latency_ms, self.tls_latency_ms, self.tcp_latency_ms]:
            if v > 0:
                return v
        return -1.0

    @property
    def quality_score(self) -> float:
        """
        Composite quality score — lower is better.
        Factors: latency, jitter, packet loss, TLS validity, WS compatibility.
        """
        if not self.alive:
            return float("inf")
        score = self.best_latency
        if self.tcp_loss_pct > 0:
            score += self.tcp_loss_pct * 3
        if self.tcp_jitter_ms > 0:
            score += self.tcp_jitter_ms * 0.5
        if not self.tls_valid:
            score += 200
        if self.ws_tested and not self.ws_ok:
            score += 150
        return score


# ─── UI Helpers ────────────────────────────────────────────────────────────────
def draw_header() -> None:
    """Render the application banner with version, author, and feature summary."""
    os.system("cls" if os.name == "nt" else "clear")
    print(f"{CLR_TITLE}🔮 ⚡ ══════════════════════════════════════════════════════════════════ ⚡ 🔮{CLR_RESET}")
    print(f"{CLR_TITLE}  ██╗   ██╗██╗     ███████╗███████╗    ████████╗██╗   ██╗███╗   ██╗███████╗██████╗ {CLR_RESET}")
    print(f"{CLR_TITLE}  ██║   ██║██║     ██╔════╝██╔════╝    ╚══██╔══╝██║   ██║████╗  ██║██╔════╝██╔══██╗{CLR_RESET}")
    print(f"{CLR_TITLE}  ██║   ██║██║     █████╗  ███████╗       ██║   ██║   ██║██╔██╗ ██║█████╗  ██████╔╝{CLR_RESET}")
    print(f"{CLR_TITLE}  ╚██╗ ██╔╝██║     ██╔══╝  ╚════██║       ██║   ██║   ██║██║╚██╗██║██╔══╝  ██╔══██╗{CLR_RESET}")
    print(f"{CLR_TITLE}   ╚████╔╝ ███████╗███████╗███████║       ██║   ╚██████╔╝██║ ╚████║███████╗██║  ██║{CLR_RESET}")
    print(f"{CLR_TITLE}    ╚═══╝  ╚══════╝╚══════╝╚══════╝       ╚═╝    ╚═════╝ ╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝{CLR_RESET}")
    print(f"{CLR_TITLE}🔮 ⚡ ══════════════════════════════════════════════════════════════════ ⚡ 🔮{CLR_RESET}")
    # Feature summary line
    features = (
        f"  {CLR_CYAN}Multi-try TCP{CLR_RESET} ·"
        f" {CLR_CYAN}DPI-safe TLS{CLR_RESET} ·"
        f" {CLR_CYAN}CF Trace{CLR_RESET} ·"
        f" {CLR_CYAN}WebSocket Probe{CLR_RESET} ·"
        f" {CLR_CYAN}Neighbor Scan{CLR_RESET} ·"
        f" {CLR_CYAN}Rotating SNI{CLR_RESET} ·"
        f" {CLR_CYAN}Speed Test{CLR_RESET} ·"
        f" {CLR_CYAN}xray Validation{CLR_RESET}"
    )
    print(f"\n{features}")
    print(f"  {CLR_GRAY}v{VERSION}  —  by {CLR_WHITE}{AUTHOR}{CLR_RESET}  {CLR_GRAY}·  Telegram: {CLR_CYAN}{TELEGRAM}{CLR_RESET}\n")
    print(f"{CLR_TITLE}{'─'*72}{CLR_RESET}")


def _box_width() -> int:
    return 68


def print_box(title: str, logs: list) -> None:
    """Print a decorative log panel with animated line output."""
    w = _box_width()
    pad = max(0, w - len(title) - 2)
    print(f"\n    {CLR_STEP}┌─ 📡 {title} {'─'*pad}┐{CLR_RESET}")
    for line in logs:
        display = line[:w - 4]
        sys.stdout.write(
            f"    {CLR_STEP}│{CLR_RESET} {CLR_GRAY}⚡ {display:<{w-4}}{CLR_RESET}{CLR_STEP}│\n{CLR_RESET}"
        )
        sys.stdout.flush()
        time.sleep(0.025)
    print(f"    {CLR_STEP}└{'─'*w}┘{CLR_RESET}")


def print_section(title: str) -> None:
    """Print a bold section header."""
    print(f"\n{CLR_STEP}█▓▒░  {title}{CLR_RESET}")


def print_option(key: str, label: str) -> None:
    """Print a single menu option."""
    print(f"    {CLR_GRAY}│{CLR_RESET} [{CLR_TITLE}{key}{CLR_RESET}] {CLR_TEXT}{label}{CLR_RESET}")


def ask(prompt: str, default: str = "") -> str:
    """Prompt the user for input; return default if blank or interrupted."""
    try:
        val = input(f"    {CLR_GRAY}└──{CLR_CYAN} {prompt}: {CLR_RESET}").strip()
        return val if val else default
    except (EOFError, KeyboardInterrupt):
        return default


def ask_int(prompt: str, default: int, min_val: int = 1, max_val: int = 10_000) -> int:
    """Prompt for a bounded integer, looping until valid input is received."""
    while True:
        raw = ask(f"{prompt} (default: {default})", str(default))
        try:
            val = int(raw)
            if min_val <= val <= max_val:
                return val
            print(f"    {CLR_ERROR}❌  Value must be between {min_val} and {max_val}.{CLR_RESET}")
        except ValueError:
            print(f"    {CLR_ERROR}❌  Please enter a valid integer.{CLR_RESET}")


def pause_or_restart() -> bool:
    """
    Keep the window open after completion.
    Returns True if the user wants to start a new session, False to exit.
    """
    print(f"\n    {CLR_GRAY}┌────────────────────────────────────────────────┐{CLR_RESET}")
    print(f"    {CLR_GRAY}│  Press {CLR_WHITE}Enter{CLR_GRAY} to exit  ·  Enter {CLR_WHITE}1{CLR_GRAY} to start again  │{CLR_RESET}")
    print(f"    {CLR_GRAY}└────────────────────────────────────────────────┘{CLR_RESET}")
    try:
        choice = input(f"    {CLR_CYAN}Your choice: {CLR_RESET}").strip()
        return choice == "1"
    except (EOFError, KeyboardInterrupt):
        return False


# ─── Network: Fetch CF Ranges ──────────────────────────────────────────────────
def fetch_cf_ranges() -> list:
    """
    Download the latest Cloudflare IPv4 CIDR blocks from cloudflare.com/ips-v4/.
    Falls back to built-in list on any network error.
    """
    try:
        req = urllib.request.Request(
            "https://www.cloudflare.com/ips-v4/",
            headers={"User-Agent": "vless-tuner/1.0"}
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            raw = resp.read().decode().strip()
        ranges = [l.strip() for l in raw.splitlines() if l.strip()]
        if len(ranges) >= 5:
            log.info(f"CF ranges refreshed: {len(ranges)} CIDRs")
            return ranges
    except Exception as e:
        log.warning(f"fetch_cf_ranges: {e}")
    return CF_IP_RANGES_BUILTIN


# ─── Network: TCP Multi-Try Probe ─────────────────────────────────────────────
def tcp_ping_multi(
    ip: str,
    port: int = 443,
    tries: int = PROBE_TRIES,
    timeout: float = PING_TIMEOUT,
) -> tuple:
    """
    Probe a host multiple times to compute statistical TCP metrics.
    A small random jitter (10–60 ms) is inserted between attempts so the
    probe pattern does not look like a simple scanner to DPI systems.

    Returns:
        (avg_ms, min_ms, jitter_ms, loss_pct)
        All values are -1.0 / 100.0 when no attempt succeeded.
    """
    latencies = []
    for i in range(tries):
        start = time.perf_counter()
        try:
            with socket.create_connection((ip, port), timeout=timeout):
                latencies.append((time.perf_counter() - start) * 1000)
        except OSError:
            latencies.append(0.0)
        if i < tries - 1:
            time.sleep(random.uniform(0.01, 0.06))  # anti-scanner jitter

    successful = [l for l in latencies if l > 0]
    loss = (latencies.count(0.0) / tries) * 100

    if not successful:
        return -1.0, -1.0, -1.0, 100.0

    avg = sum(successful) / len(successful)
    mn  = min(successful)
    jitter = 0.0
    if len(successful) >= 2:
        variance = sum((l - avg) ** 2 for l in successful) / len(successful)
        jitter = variance ** 0.5

    return avg, mn, jitter, loss


def tcp_ping(ip: str, port: int = 443, timeout: float = PING_TIMEOUT) -> float:
    """Single TCP connect — lightweight check used by saturation mode."""
    start = time.perf_counter()
    try:
        with socket.create_connection((ip, port), timeout=timeout):
            return (time.perf_counter() - start) * 1000
    except OSError:
        return -1.0


# ─── Network: TLS Handshake ────────────────────────────────────────────────────
def tls_handshake_test(
    ip: str,
    sni: str = SCAN_SNI,
    port: int = 443,
    timeout: float = TLS_TIMEOUT,
) -> tuple:
    """
    Perform a full TLS handshake using a neutral Cloudflare SNI.
    Using speed.cloudflare.com (or similar) as the SNI instead of the
    actual proxy domain prevents DPI from identifying the probe as a
    proxy check.

    Returns:
        (latency_ms, handshake_ok)
        latency_ms is -1.0 on failure.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    try:
        ctx.minimum_version = ssl.TLSVersion.TLSv1_2
    except AttributeError:
        pass  # Python < 3.7 — skip version pinning

    start = time.perf_counter()
    try:
        raw = socket.create_connection((ip, port), timeout=timeout)
        raw.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        tls = ctx.wrap_socket(raw, server_hostname=sni, do_handshake_on_connect=False)
        tls.settimeout(timeout)
        tls.do_handshake()
        latency = (time.perf_counter() - start) * 1000
        tls.close()
        return latency, True
    except ssl.SSLError as e:
        elapsed = (time.perf_counter() - start) * 1000
        log.debug(f"TLS SSLError {ip}:{port} -> {e}")
        return (elapsed if elapsed < timeout * 1000 else -1.0), False
    except OSError:
        return -1.0, False


# ─── Network: HTTP /cdn-cgi/trace Probe ───────────────────────────────────────
def probe_http_trace(ip: str, port: int = 443, timeout: float = HTTP_TIMEOUT) -> tuple:
    """
    Issue GET /cdn-cgi/trace using rotating SNIs and parse the Cloudflare
    response to extract the actual datacenter (colo) code.

    Budget split: TCP=timeout/4, TLS=timeout/2, HTTP=remainder.

    Returns:
        (latency_ms, tls_ok, http_status, colo_code)
        colo_code is "" when the trace endpoint did not respond.
    """
    for sni in SCAN_SNIS:
        try:
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE

            raw = socket.create_connection((ip, port), timeout=timeout / 4)

            if port != 80:
                tls = ctx.wrap_socket(raw, server_hostname=sni, do_handshake_on_connect=False)
                tls.settimeout(timeout / 2)
                tls.do_handshake()
                conn = tls
                tls_ok = True
            else:
                conn = raw
                tls_ok = False

            conn.settimeout(timeout)
            request = (
                f"GET /cdn-cgi/trace HTTP/1.1\r\n"
                f"Host: {sni}\r\nUser-Agent: vless-tuner/1.0\r\n"
                f"Connection: close\r\n\r\n"
            )
            start = time.perf_counter()
            conn.sendall(request.encode())

            buf = b""
            while len(buf) < 4096:
                chunk = conn.recv(1024)
                if not chunk:
                    break
                buf += chunk
                if b"\r\n\r\n" in buf and len(buf) > 200:
                    break

            latency = (time.perf_counter() - start) * 1000
            conn.close()

            text = buf.decode("utf-8", errors="ignore")
            status = 0
            if text.startswith("HTTP/"):
                try:
                    status = int(text.split(" ")[1])
                except (IndexError, ValueError):
                    pass

            colo = ""
            for line in text.split("\n"):
                line = line.strip()
                if line.lower().startswith("cf-ray:"):
                    parts = line.split("-")
                    if len(parts) >= 2:
                        colo = parts[-1].strip()[:3].upper()
                if line.startswith("colo="):
                    colo = line[5:].strip()[:3].upper()

            if 200 <= status < 400 and colo:
                return latency, tls_ok, status, colo

        except Exception:
            continue

    return -1.0, False, 0, ""


# ─── Network: WebSocket DPI Probe ─────────────────────────────────────────────
def probe_websocket(
    ip: str,
    port: int = 443,
    sni: str = SCAN_SNI,
    ws_host: str = "",
    ws_path: str = "/",
    timeout: float = 5.0,
) -> bool:
    """
    Two-phase WebSocket DPI resistance test:

    Phase 1 — Idle hold:
        Hold a TLS connection open for WS_IDLE_HOLD seconds without sending
        any data.  If the connection is reset during this window, DPI is
        actively terminating long-lived TLS sessions.

    Phase 2 — WebSocket upgrade:
        Send a proper HTTP Upgrade request and check whether the server
        returns an HTTP response (meaning the TCP path allows WS traffic).

    Returns True only when both phases pass.
    """
    if not ws_host:
        ws_host = sni
    if not ws_path.startswith("/"):
        ws_path = "/" + ws_path

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    try:
        raw = socket.create_connection((ip, port), timeout=timeout / 3)
        tls = ctx.wrap_socket(raw, server_hostname=sni, do_handshake_on_connect=False)
        tls.settimeout(timeout)
        tls.do_handshake()

        # Phase 1: idle hold — detect aggressive DPI session teardown
        tls.settimeout(min(WS_IDLE_HOLD, timeout / 2))
        try:
            tls.recv(1)
        except socket.timeout:
            pass  # Expected — no data should arrive
        except OSError:
            tls.close()
            return False  # Connection was reset during idle — DPI detected

        # Phase 2: send WebSocket upgrade
        ws_req = (
            f"GET {ws_path} HTTP/1.1\r\n"
            f"Host: {ws_host}\r\n"
            f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==\r\n"
            f"Sec-WebSocket-Version: 13\r\n\r\n"
        )
        tls.settimeout(timeout / 2)
        tls.sendall(ws_req.encode())

        tls.settimeout(timeout / 3)
        resp = b""
        try:
            resp = tls.recv(1024)
        except OSError:
            pass
        tls.close()
        return b"HTTP/" in resp

    except Exception:
        return False


# ─── Network: Cloudflare Speed Test ───────────────────────────────────────────
def cf_speed_test(
    ip: str,
    port: int = 443,
    timeout: float = 5.0,
    sample_bytes: int = 65536,
) -> float:
    """
    Measure download throughput using Cloudflare's dedicated speed endpoint
    (speed.cloudflare.com/__down?bytes=N).  This endpoint returns exactly
    N random bytes, giving a clean measurement without HTTP overhead skew.

    Returns speed in KB/s, or -1.0 on failure.
    """
    try:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE

        raw = socket.create_connection((ip, port), timeout=timeout / 4)

        if port != 80:
            raw.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
            conn = ctx.wrap_socket(
                raw,
                server_hostname="speed.cloudflare.com",
                do_handshake_on_connect=False,
            )
            conn.settimeout(timeout / 2)
            conn.do_handshake()
        else:
            conn = raw

        conn.settimeout(timeout)
        request = (
            f"GET /__down?bytes={sample_bytes} HTTP/1.1\r\n"
            f"Host: speed.cloudflare.com\r\n"
            f"User-Agent: vless-tuner/1.0\r\nConnection: close\r\n\r\n"
        )
        conn.sendall(request.encode())

        start = time.perf_counter()
        received = 0
        while received < sample_bytes:
            chunk = conn.recv(8192)
            if not chunk:
                break
            received += len(chunk)

        elapsed = time.perf_counter() - start
        conn.close()
        return (received / 1024) / elapsed if elapsed > 0 and received > 8192 else -1.0

    except OSError:
        return -1.0


# ─── Full Four-Stage Probe Pipeline ───────────────────────────────────────────
def probe_ip_full(
    ip: str,
    port: int = 443,
    do_ws: bool = False,
    ws_host: str = "",
    ws_path: str = "/",
) -> ScanResult:
    """
    Complete IP quality assessment pipeline:

    Stage 1 — TCP multi-try   : avg latency, jitter, packet loss
    Stage 2 — TLS handshake   : DPI-safe, neutral SNI
    Stage 3 — HTTP /cdn-cgi/trace : real datacenter, rotating SNI
    Stage 4 — WebSocket probe : optional, only when TLS passed
    Stage 5 — Speed test      : optional, TLS ports only
    """
    result = ScanResult(ip=ip)

    # Stage 1: TCP
    avg, mn, jitter, loss = tcp_ping_multi(ip, port)
    result.tcp_latency_ms = avg
    result.tcp_jitter_ms  = jitter
    result.tcp_loss_pct   = loss
    if avg < 0 or loss >= 100:
        return result
    result.alive = True

    # Stage 2: TLS with randomly chosen neutral SNI
    sni = random.choice(SCAN_SNIS)
    tls_lat, tls_ok = tls_handshake_test(ip, sni=sni, port=port)
    result.tls_latency_ms = tls_lat
    result.tls_valid      = tls_ok

    # Stage 3: HTTP trace — reveals actual Cloudflare colo
    http_lat, http_tls, http_status, colo = probe_http_trace(ip, port)
    result.http_latency_ms = http_lat
    result.http_ok  = http_status >= 200 and colo != ""
    result.colo     = colo
    if http_tls:
        result.tls_valid = True  # Implicit TLS confirmation from trace

    # Stage 4: WebSocket DPI test (only when TLS is confirmed)
    if do_ws and result.tls_valid:
        result.ws_tested = True
        result.ws_ok = probe_websocket(ip, port, sni=sni, ws_host=ws_host, ws_path=ws_path)

    # Stage 5: Speed — TLS-capable ports only
    if result.tls_valid and port in (443, 8443):
        result.speed_kbps = cf_speed_test(ip, port)

    return result


# ─── Neighbor IP Generator ─────────────────────────────────────────────────────
def generate_neighbor_ips(
    good_ip: str,
    cf_ranges: list,
    radius: int = 32,
    limit_per_hit: int = 12,
) -> list:
    """
    Discover IPs adjacent to a known-good address that still fall within
    Cloudflare's published CIDR ranges.  Modelled on the neighbour-scanning
    concept where a good result implies that nearby addresses on the same
    physical infrastructure may also be clean.
    """
    try:
        parts   = list(map(int, good_ip.split(".")))
        base_int = (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

        cf_nets = []
        for cidr in cf_ranges:
            net_str, mask_str = cidr.split("/")
            p = list(map(int, net_str.split(".")))
            net_int  = (p[0] << 24) | (p[1] << 16) | (p[2] << 8) | p[3]
            mask_int = 0xFFFFFFFF & (0xFFFFFFFF << (32 - int(mask_str)))
            cf_nets.append((net_int, mask_int))

        def in_cf(ip_int: int) -> bool:
            return any(ip_int & m == n & m for n, m in cf_nets)

        def int_to_ip(v: int) -> str:
            return f"{(v>>24)&0xFF}.{(v>>16)&0xFF}.{(v>>8)&0xFF}.{v&0xFF}"

        neighbors = []
        for delta in range(1, radius + 1):
            for signed in (delta, -delta):
                candidate = base_int + signed
                if 0 < candidate <= 0xFFFFFFFF and in_cf(candidate):
                    neighbors.append(int_to_ip(candidate))
                    if len(neighbors) >= limit_per_hit:
                        return neighbors
        return neighbors
    except Exception as e:
        log.warning(f"generate_neighbor_ips: {e}")
        return []


# ─── IP Generators ─────────────────────────────────────────────────────────────
def cidr_to_ips(cidr: str, limit: Optional[int] = None) -> list:
    """
    Expand a CIDR block to a list of probe candidates.
    Step size scales with mask width to avoid generating millions of IPs
    for large blocks: /16 and wider use step=8, /17-/23 use step=2, /24+
    enumerate every host.
    """
    try:
        network, mask_str = cidr.split("/")
        mask  = int(mask_str)
        parts = list(map(int, network.split(".")))
        step  = 8 if mask <= 16 else (2 if mask <= 23 else 1)
        ips   = []

        if mask <= 16:
            for c in range(0, 256, step):
                for d in range(1, 255, step):
                    ips.append(f"{parts[0]}.{parts[1]}.{c}.{d}")
        elif mask <= 23:
            for d in range(1, 255, step):
                ips.append(f"{parts[0]}.{parts[1]}.{parts[2]}.{d}")
        else:
            for d in range(1, 255):
                ips.append(f"{parts[0]}.{parts[1]}.{parts[2]}.{d}")

        ips = list(set(ips))
        if limit and limit < len(ips):
            random.shuffle(ips)
            return ips[:limit]
        return ips
    except ValueError as e:
        log.warning(f"cidr_to_ips error '{cidr}': {e}")
        return []


def proximity_ips(base_ip: str, count: int = 100) -> list:
    """
    Generate IPs in the /21 neighbourhood of base_ip (±5 on the third octet).
    Useful for expanding around a single known-clean IP.
    """
    try:
        p = base_ip.split(".")
        ips = []
        for offset in range(-5, 6):
            t = int(p[2]) + offset
            if 0 <= t <= 255:
                for d in range(1, 255, 2):
                    ips.append(f"{p[0]}.{p[1]}.{t}.{d}")
        random.shuffle(ips)
        return ips[:count]
    except Exception:
        return []


# ─── Intelligence Storage ──────────────────────────────────────────────────────
def load_intelligence() -> list:
    """Load subnets that previously yielded live IPs."""
    subs = []
    if not os.path.exists(INTELLIGENCE_FILE):
        return subs
    try:
        with open(INTELLIGENCE_FILE, "r", encoding="utf-8") as f:
            for line in f:
                if "GOLDEN_SUBNET:" in line:
                    sub = line.split("GOLDEN_SUBNET:")[1].strip()
                    if sub not in subs:
                        subs.append(sub)
    except OSError:
        pass
    return subs


def save_intelligence(subnets: list) -> None:
    """Persist newly discovered productive subnets for future runs."""
    try:
        with open(INTELLIGENCE_FILE, "a", encoding="utf-8") as f:
            ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            for s in subnets:
                f.write(f"[{ts}] GOLDEN_SUBNET:{s}\n")
    except OSError:
        pass


# ─── Parallel Scan Engine ──────────────────────────────────────────────────────
def run_ip_scan(
    candidates: list,
    port: int = 443,
    workers: int = DEFAULT_WORKERS,
    do_ws: bool = False,
    ws_host: str = "",
    ws_path: str = "/",
) -> list:
    """
    Run probe_ip_full() across all candidates in parallel.
    When a result is both alive and fast (<200 ms), its neighbours are
    queued for a secondary scan pass — this catches additional clean IPs
    on the same physical infrastructure without scanning the entire range.
    """
    candidates = list(set(candidates))
    results: list = []
    done_cnt = 0
    lock = threading.Lock()
    neighbor_queue: list = []
    scanned_ips: set    = set(candidates)

    ws_label = " + WS probe" if do_ws else ""
    print(
        f"    {CLR_INFO}⏳  Scanning {len(candidates)} candidates "
        f"| {workers} threads{ws_label}{CLR_RESET}\n"
        f"    {CLR_GRAY}ℹ   Rotating SNI: {', '.join(SCAN_SNIS[:3])} …{CLR_RESET}\n"
    )

    def scan_one(ip: str) -> ScanResult:
        nonlocal done_cnt
        res = probe_ip_full(ip, port, do_ws=do_ws, ws_host=ws_host, ws_path=ws_path)
        with lock:
            done_cnt += 1
            total_now = len(candidates) + len(neighbor_queue)
            pct       = int(done_cnt / max(total_now, 1) * 38)
            bar       = "█" * pct + "░" * (38 - pct)
            alive_cnt = sum(1 for r in results if r.alive)
            sys.stdout.write(
                f"\r    {CLR_CYAN}[{bar}] {done_cnt}/{total_now}"
                f"  Live: {CLR_SUCCESS}{alive_cnt}{CLR_RESET}"
            )
            sys.stdout.flush()
            results.append(res)

            # Neighbor injection on fast, confirmed results
            if res.alive and res.best_latency < 200 and res.colo:
                for nb in generate_neighbor_ips(res.ip, CF_IP_RANGES_BUILTIN, radius=16, limit_per_hit=8):
                    if nb not in scanned_ips:
                        scanned_ips.add(nb)
                        neighbor_queue.append(nb)
        return res

    # Initial scan
    with ThreadPoolExecutor(max_workers=workers) as ex:
        for _ in as_completed([ex.submit(scan_one, ip) for ip in candidates]):
            pass

    # Secondary neighbor scan
    if neighbor_queue:
        sys.stdout.write(
            f"\n\n    {CLR_MAGENTA}🔍  Neighbor scan: "
            f"{len(neighbor_queue)} IPs near top results …{CLR_RESET}\n\n"
        )
        sys.stdout.flush()
        with ThreadPoolExecutor(max_workers=min(workers, 40)) as ex:
            for _ in as_completed([ex.submit(scan_one, ip) for ip in neighbor_queue]):
                pass

    sys.stdout.write("\n")
    return results


# ─── Scan Results Display ──────────────────────────────────────────────────────
def display_scan_results(results: list) -> list:
    """Print a sorted, colour-coded scan results table."""
    alive = sorted([r for r in results if r.alive], key=lambda r: r.quality_score)

    w = 76
    print(f"\n{CLR_TITLE}    ┌{'─'*w}┐{CLR_RESET}")
    print(f"{CLR_TITLE}    │{'📡  SCAN MATRIX REPORT':^{w}}│{CLR_RESET}")
    print(f"{CLR_TITLE}    └{'─'*w}┘{CLR_RESET}")

    hdr = (
        f"    {CLR_GRAY}"
        f"{'IP':<18} {'TCP':>6} {'Jit':>5} {'Loss':>5}"
        f" {'TLS':>4} {'HTTP':>6} {'Colo':>4} {'WS':>3} {'KB/s':>7}"
        f"{CLR_RESET}"
    )
    print(hdr)
    print(f"    {CLR_GRAY}{'─'*18} {'─'*6} {'─'*5} {'─'*5} {'─'*4} {'─'*6} {'─'*4} {'─'*3} {'─'*7}{CLR_RESET}")

    for r in alive:
        tcp_s  = f"{r.tcp_latency_ms:.0f}"  if r.tcp_latency_ms  > 0 else "─"
        jit_s  = f"{r.tcp_jitter_ms:.0f}"   if r.tcp_jitter_ms   > 0 else "─"
        los_s  = f"{r.tcp_loss_pct:.0f}%"   if r.tcp_loss_pct    > 0 else "0%"
        tls_s  = f"{CLR_SUCCESS}✓{CLR_RESET}" if r.tls_valid else f"{CLR_WARN}✗{CLR_RESET}"
        http_s = f"{r.http_latency_ms:.0f}" if r.http_latency_ms > 0 else "─"
        colo_s = r.colo if r.colo else "─"
        ws_s   = (
            f"{CLR_SUCCESS}✓{CLR_RESET}" if r.ws_ok else
            (f"{CLR_ERROR}✗{CLR_RESET}" if r.ws_tested else f"{CLR_GRAY}─{CLR_RESET}")
        )
        spd_s  = f"{r.speed_kbps:.0f}" if r.speed_kbps > 0 else "─"
        color  = (
            CLR_SUCCESS if r.best_latency < 150 else
            (CLR_WARN   if r.best_latency < 300 else CLR_TEXT)
        )
        print(
            f"    {color}🔹 {r.ip:<18}{CLR_RESET}"
            f" {tcp_s:>6} {jit_s:>5} {los_s:>5}"
            f" {tls_s:>4} {http_s:>6}"
            f" {CLR_MAGENTA}{colo_s:<4}{CLR_RESET}"
            f" {ws_s:>3} {spd_s:>7}"
        )

    colos    = sorted(set(r.colo for r in alive if r.colo))
    ws_total = sum(1 for r in alive if r.ws_tested)
    ws_ok    = sum(1 for r in alive if r.ws_ok)
    summary  = f"Alive: {len(alive)}  |  Colos: {', '.join(colos[:6]) or '─'}"
    if ws_total:
        summary += f"  |  WS: {ws_ok}/{ws_total}"
    print(f"\n    {CLR_SUCCESS}✅  {summary}{CLR_RESET}")
    return alive


# ─── xray Validation (Phase 2) ────────────────────────────────────────────────
def find_xray_binary() -> Optional[str]:
    """Locate the xray binary in PATH."""
    for name in ("xray", "xray.exe"):
        for directory in os.environ.get("PATH", "").split(os.pathsep):
            full = os.path.join(directory, name)
            if os.path.isfile(full) and os.access(full, os.X_OK):
                return full
    return None


def build_xray_config(node: VlessNode, ip: str, socks_port: int) -> dict:
    """Build a minimal xray JSON config that routes all traffic through the node."""
    users = [{"id": node.user_id, "encryption": "none"}]
    stream: dict = {"network": node.network, "security": node.security}

    if node.network == "ws":
        stream["wsSettings"] = {"path": node.path, "headers": {"Host": node.host}}
    if node.security == "tls":
        stream["tlsSettings"] = {"serverName": node.host}

    return {
        "log": {"loglevel": "none"},
        "inbounds": [{
            "tag": "socks-in", "port": socks_port, "listen": "127.0.0.1",
            "protocol": "socks", "settings": {"udp": True},
            "sniffing": {"enabled": False},
        }],
        "outbounds": [
            {"tag": "proxy", "protocol": "vless",
             "settings": {"vnext": [{"address": ip, "port": node.port, "users": users}]},
             "streamSettings": stream},
            {"tag": "direct", "protocol": "freedom", "settings": {}},
        ],
        "routing": {
            "domainStrategy": "AsIs",
            "rules": [{"type": "field", "outboundTag": "proxy", "network": "tcp,udp"}],
        },
    }


def validate_with_xray(
    node: VlessNode,
    ip: str,
    xray_bin: str,
    timeout: float = 15.0,
) -> tuple:
    """
    Start xray with a per-test config, expose a local SOCKS5 proxy,
    and verify end-to-end connectivity by fetching cloudflare.com/cdn-cgi/trace
    through that proxy.

    Returns:
        (success, latency_ms, speed_kbps, error_message)
    """
    socks_port = random.randint(20000, 25000)
    config     = build_xray_config(node, ip, socks_port)
    tmp        = tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False)

    try:
        json.dump(config, tmp)
        tmp.close()
        proc = subprocess.Popen(
            [xray_bin, "run", "-c", tmp.name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )

        # Wait for SOCKS port to become available (up to 6 seconds)
        for _ in range(30):
            time.sleep(0.2)
            try:
                with socket.create_connection(("127.0.0.1", socks_port), timeout=0.3):
                    break
            except OSError:
                pass
        else:
            proc.kill()
            proc.wait()
            return False, -1.0, -1.0, "SOCKS port timeout"

        try:
            handler = urllib.request.SOCKSHandler(  # type: ignore[attr-defined]
                socks_proxy=f"127.0.0.1:{socks_port}"
            )
        except AttributeError:
            proc.kill()
            proc.wait()
            return False, -1.0, -1.0, "SOCKSHandler unavailable (install pysocks)"

        opener = urllib.request.build_opener(handler)
        start  = time.perf_counter()
        try:
            req = urllib.request.Request(
                "https://cloudflare.com/cdn-cgi/trace",
                headers={"User-Agent": "vless-tuner/1.0"},
            )
            with opener.open(req, timeout=timeout) as resp:
                body = resp.read().decode("utf-8", errors="ignore")
            latency = (time.perf_counter() - start) * 1000

            if "colo=" not in body:
                proc.kill()
                proc.wait()
                return False, latency, -1.0, "no colo in trace response"

            proc.kill()
            proc.wait()
            return True, latency, -1.0, ""

        except Exception as e:
            proc.kill()
            proc.wait()
            return False, -1.0, -1.0, str(e)
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass


# ─── Subscription Fetcher ──────────────────────────────────────────────────────
def fetch_subscription(url: str) -> Optional[str]:
    """Download a subscription URL in a background thread with a live countdown."""
    result_holder: list = [None]
    done = threading.Event()

    def worker() -> None:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.build_opener(urllib.request.ProxyHandler()).open(req, timeout=25) as r:
                result_holder[0] = r.read().decode("utf-8")
        except Exception as e:
            log.warning(f"fetch_subscription: {e}")
            result_holder[0] = ""
        finally:
            done.set()

    threading.Thread(target=worker, daemon=True).start()
    for remaining in range(25, 0, -1):
        if done.wait(timeout=1):
            break
        sys.stdout.write(f"\r    {CLR_WARN}⏳  Syncing endpoint… {remaining}s remaining {CLR_RESET}")
        sys.stdout.flush()
    sys.stdout.write("\r" + " " * 60 + "\r")
    data = result_holder[0]
    return data if data else None


# ─── VLESS Config Parser ───────────────────────────────────────────────────────
def parse_vless_nodes(raw: str, mode: str) -> list:
    """
    Parse VLESS configs from any supported format:
      - vless:// URI lines
      - JSON array / single object with outbounds
      - Base64-encoded block of either of the above

    Deduplication key:
      mode "1" (IP injection)    — UUID + host
      mode "2" (format convert)  — UUID + host + path + address + port
    """
    logs = ["Initialising deduplication pipeline…"]
    text = raw.strip()

    # Attempt Base64 decode when input looks like neither JSON nor URI
    if not (text.startswith("{") or text.startswith("[") or text.startswith("vless://")):
        try:
            text = base64.b64decode(text).decode("utf-8", errors="ignore").strip()
            logs.append("Base64 block decoded successfully.")
        except Exception:
            pass

    raw_nodes = []

    # Parse vless:// URI lines
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("vless://"):
            continue
        try:
            body = line[8:]
            uid, rest = body.split("@", 1)
            addr_part, qh = rest.split("?", 1)
            addr, port_str = addr_part.rsplit(":", 1)
            qs, *rem = qh.split("#", 1)
            remarks = urllib.parse.unquote(rem[0]) if rem else "Node"
            params  = urllib.parse.parse_qs(qs)
            raw_nodes.append(VlessNode(
                user_id  = uid.strip(),
                address  = addr.strip(),
                port     = int(port_str),
                host     = params.get("host",     [addr])[0].strip(),
                path     = params.get("path",     ["/"])[0].strip(),
                security = params.get("security", ["none"])[0].strip(),
                network  = params.get("type",     ["ws"])[0].strip(),
                remarks  = remarks,
            ))
        except Exception:
            continue

    # Parse JSON configs
    try:
        parsed = json.loads(text)
        for cfg in (parsed if isinstance(parsed, list) else [parsed]):
            try:
                vout = next(
                    (o for o in cfg.get("outbounds", []) if o.get("protocol") == "vless"),
                    None,
                )
                if not vout:
                    continue
                vnext = vout["settings"]["vnext"][0]
                ss    = vout.get("streamSettings", {})
                ws    = ss.get("wsSettings", {})
                raw_nodes.append(VlessNode(
                    user_id  = vnext["users"][0]["id"].strip(),
                    address  = vnext["address"].strip(),
                    port     = int(vnext["port"]),
                    host     = ws.get("host",  vnext["address"]).strip(),
                    path     = ws.get("path",  "/").strip(),
                    security = ss.get("security", "none").strip(),
                    network  = ss.get("network",  "ws").strip(),
                    remarks  = cfg.get("remarks", "VLESS_Node"),
                ))
            except (KeyError, IndexError, TypeError):
                continue
    except (json.JSONDecodeError, ValueError):
        pass

    logs.append(f"Raw entries loaded: {len(raw_nodes)}")

    # Deduplication
    seen:   set  = set()
    unique: list = []
    for n in raw_nodes:
        sig = (
            f"{n.user_id.lower()}@{n.host.lower()}"
            if mode == "1"
            else f"{n.user_id.lower()}@{n.host.lower()}{n.path.lower()}_{n.address.lower()}:{n.port}"
        )
        if sig not in seen:
            seen.add(sig)
            unique.append(n)
        else:
            logs.append(f"Pruned duplicate: {sig[:55]}")

    logs.append(f"Unique cores ready: {len(unique)}")
    print_box("DEDUPLICATION PIPELINE", logs)
    return unique


# ─── VLESS Link Builder ────────────────────────────────────────────────────────
def build_vless_link(
    node:        VlessNode,
    target_ip:   str,
    target_port: int,
    fp:          str,
    enable_alpn: bool,
    enable_tfo:  bool,
    remarks:     str,
) -> str:
    """Assemble a vless:// URI from node parameters and protocol tweaks."""
    if fp == "random":
        fp = random.choice(["chrome", "safari", "firefox", "edge"])

    q = (
        f"encryption=none"
        f"&security={node.security}"
        f"&type={node.network}"
        f"&host={node.host}"
        f"&path={urllib.parse.quote(node.path, safe='')}"
    )
    if enable_tfo:
        q += "&tfo=1"
    if node.security == "tls":
        q += f"&sni={node.host}&fp={fp}"
        if enable_alpn:
            q += "&alpn=http%2F1.1%2Ch2"

    return f"vless://{node.user_id}@{target_ip}:{target_port}?{q}#{urllib.parse.quote(remarks)}"


# ─── Saturation Mode ───────────────────────────────────────────────────────────
def saturation_mode(node: VlessNode, ips: list, name_prefix: str) -> list:
    """
    Emergency fallback when only one unique core remains after deduplication.
    Generates maximum link variants by crossing the top 5 IPs against all
    SAFE_PORTS with randomised TLS fingerprints.
    """
    print_box("SATURATION SHIELD", [
        "Single core detected — activating multi-port saturation.",
        f"Testing top-5 IPs × {len(SAFE_PORTS)} safe ports via TCP.",
    ])
    links: list = []
    fps  = ["chrome", "safari", "edge"]
    idx  = 1

    for ip in ips[:5]:
        for port in SAFE_PORTS:
            if tcp_ping(ip, port, 1.5) > 0:
                fp   = random.choice(fps)
                alpn = "http%2F1.1" if port in (2053, 2096) else "http%2F1.1%2Ch2"
                q    = (
                    f"encryption=none&security={node.security}&type={node.network}"
                    f"&host={node.host}&path={urllib.parse.quote(node.path, safe='')}"
                    f"&tfo=1&fp={fp}&alpn={alpn}"
                )
                if node.security == "tls":
                    q += f"&sni={node.host}"
                r = urllib.parse.quote(f"{name_prefix}_Core{idx}_P{port}_⚡")
                links.append(f"vless://{node.user_id}@{ip}:{port}?{q}#{r}")
                idx += 1

    print(f"    {CLR_SUCCESS}✅  {len(links)} link variants generated via saturation.{CLR_RESET}")
    return links


# ─── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    draw_header()

    # ── STEP 0: Operation Mode ────────────────────────────────────────────────
    print_section("STEP 0 ── SELECT OPERATION MODE")
    print_option("1", "Scan & Inject Clean IPs   (ignore raw IP/Port/Path duplicates)")
    print_option("2", "Format Converter / Rename  (keep all distinct IPs and ports)")
    mode = ask("Select mode (1/2)", "1")
    if mode not in ("1", "2"):
        mode = "1"

    # ── STEP 1: Input Gateway ─────────────────────────────────────────────────
    print_section("STEP 1 ── INPUT GATEWAY")
    print_option("1", "Online subscription URL")
    print_option("2", "Manual paste  (JSON / Base64 / vless:// URIs)")
    src = ask("Select source (1/2)", "1")

    raw = ""
    if src == "1":
        raw = fetch_subscription(ask("Enter subscription URL")) or ""
    else:
        print(f"\n    {CLR_INFO}👇  Paste configs below — type END on a new line to finish:{CLR_RESET}")
        lines: list = []
        while True:
            try:
                line = input(f"    {CLR_GRAY}│{CLR_RESET} ")
            except (EOFError, KeyboardInterrupt):
                break
            if line.strip() == "END":
                break
            lines.append(line)
        raw = "\n".join(lines).strip()

    if not raw:
        print(f"    {CLR_ERROR}❌  Input is empty or connection timed out.{CLR_RESET}")
        return

    nodes = parse_vless_nodes(raw, mode)
    if not nodes:
        print(f"    {CLR_ERROR}❌  No valid VLESS nodes detected in input.{CLR_RESET}")
        return
    print(f"    {CLR_SUCCESS}✅  {len(nodes)} unique core(s) locked into pipeline.{CLR_RESET}")

    # ── STEP 2: Node Branding ─────────────────────────────────────────────────
    print_section("STEP 2 ── NODE BRANDING")
    custom_name = ask("Config name prefix  (blank = keep original remarks)", "")

    # ── STEP 3: IP Scan Engine (mode 1 only) ──────────────────────────────────
    final_ips:    list = []
    xray_results: dict = {}

    if mode == "1":
        print_section("STEP 3 ── CLEAN IP SCAN ENGINE")
        print_option("1", "Auto-scan  — live Cloudflare ranges  (fetched from cloudflare.com/ips-v4/)")
        print_option("2", "Deep scan  — custom grid size")
        print_option("3", "Proximity  — cluster around a base IP")
        print_option("4", "Static list — paste IPs manually")
        print_option("5", "Bypass IP injection")
        ip_choice = ask("Scan mode (1-5)", "1")

        # Thread count
        print(f"\n    {CLR_STEP}┌── Thread Configuration{CLR_RESET}")
        print_option("1", f"Default ({DEFAULT_WORKERS} threads) — recommended")
        print_option("2", "Custom  (manual entry, 10–300)")
        t_mode  = ask("Thread mode (1/2)", "1")
        workers = ask_int("Number of threads", DEFAULT_WORKERS, 10, 300) if t_mode == "2" else DEFAULT_WORKERS
        print(f"    {CLR_INFO}ℹ   Thread count: {CLR_WHITE}{workers}{CLR_RESET}")

        # WebSocket probe option
        ws_probe = ask("Enable WebSocket DPI probe? (y/n)", "y").lower() in ("y", "yes")
        ws_host  = nodes[0].host if nodes else ""
        ws_path  = nodes[0].path if nodes else "/"

        candidates: list = []

        # Load Cloudflare ranges
        print(f"\n    {CLR_INFO}🌐  Loading Cloudflare IP ranges…{CLR_RESET}")
        try:
            cf_ranges = fetch_cf_ranges()
            print(f"    {CLR_SUCCESS}✅  {len(cf_ranges)} CIDR blocks loaded.{CLR_RESET}")
        except Exception:
            cf_ranges = CF_IP_RANGES_BUILTIN
            print(f"    {CLR_WARN}⚠   Using built-in ranges ({len(cf_ranges)} CIDRs).{CLR_RESET}")

        # Inject previously discovered subnets
        prior_subs = load_intelligence()
        if prior_subs and ip_choice in ("1", "2"):
            print(f"    {CLR_INFO}🧠  Injecting {len(prior_subs)} golden subnet(s) from memory.{CLR_RESET}")
            for s in prior_subs:
                candidates.extend(cidr_to_ips(s, limit=50))

        if ip_choice == "1":
            for sub in cf_ranges:
                candidates.extend(cidr_to_ips(sub, limit=80))
        elif ip_choice == "2":
            grid = ask_int("Total candidate count to scan", 600)
            per  = max(1, grid // len(cf_ranges))
            for sub in cf_ranges:
                candidates.extend(cidr_to_ips(sub, limit=per))
        elif ip_choice == "3":
            base  = ask("Enter your clean base IP")
            count = ask_int("Surrounding IPs to probe", 200)
            candidates = proximity_ips(base, count)
        elif ip_choice == "4":
            print(f"    {CLR_INFO}👇  Enter IPs (one per line) — type END to finish:{CLR_RESET}")
            while True:
                try:
                    line = input(f"    {CLR_GRAY}│{CLR_RESET} ").strip()
                except (EOFError, KeyboardInterrupt):
                    break
                if line == "END":
                    break
                if line:
                    candidates.append(line)

        if candidates and ip_choice != "5":
            candidates  = list(set(candidates))
            all_results = run_ip_scan(
                candidates, port=443, workers=workers,
                do_ws=ws_probe, ws_host=ws_host, ws_path=ws_path,
            )
            alive_list = display_scan_results(all_results)

            # Persist productive subnets
            golden = list({".".join(r.ip.split(".")[:3]) + ".0/24" for r in alive_list})
            if golden:
                save_intelligence(golden[:5])

            if alive_list:
                limit = ask_int(
                    f"How many clean IPs to inject? (1–{len(alive_list)})",
                    min(5, len(alive_list)), 1, len(alive_list),
                )
                final_ips = [r.ip for r in alive_list[:limit]]

                # Phase 2: xray end-to-end validation
                xray_bin = find_xray_binary()
                if xray_bin and nodes:
                    do_p2 = ask(f"Phase 2: end-to-end xray test for {len(final_ips)} IP(s)? (y/n)", "y")
                    if do_p2.lower() in ("y", "yes"):
                        print(f"\n    {CLR_STEP}🔬  Phase 2 — xray validation…{CLR_RESET}\n")
                        validated: list = []
                        for ip in final_ips:
                            sys.stdout.write(f"    {CLR_CYAN}  Testing {ip}…{CLR_RESET}")
                            sys.stdout.flush()
                            ok, lat, _, err = validate_with_xray(nodes[0], ip, xray_bin)
                            icon  = f"{CLR_SUCCESS}✅" if ok else f"{CLR_ERROR}❌"
                            lat_s = f"{lat:.0f} ms" if lat > 0 else "─"
                            sys.stdout.write(
                                f"\r    {icon}  {ip:<18}  {lat_s:>8}"
                                f"  {err[:35] if err else ''}{CLR_RESET}\n"
                            )
                            sys.stdout.flush()
                            if ok:
                                validated.append(ip)
                                xray_results[ip] = lat
                        if validated:
                            print(f"\n    {CLR_SUCCESS}✅  Phase 2 validated: {len(validated)}/{len(final_ips)} IPs{CLR_RESET}")
                            final_ips = validated
                        else:
                            print(f"    {CLR_WARN}⚠   Phase 2 failed for all — keeping Phase 1 IPs.{CLR_RESET}")
                elif not xray_bin:
                    print(
                        f"    {CLR_GRAY}ℹ   xray not found in PATH — Phase 2 skipped."
                        f" (Install xray for end-to-end validation){CLR_RESET}"
                    )
            else:
                print(f"    {CLR_ERROR}❌  No alive IPs found in this scan.{CLR_RESET}")

    # ── STEP 4: Protocol Optimisation ─────────────────────────────────────────
    print_section("STEP 4 ── PROTOCOL OPTIMISATION")
    print_option("1", "🚀  AI Auto-Pilot  — benchmark TCP/TLS and auto-select best profile")
    print_option("2", "🛠   Manual        — configure Fingerprint, ALPN, TFO by hand")
    tweak_mode = ask("Mode (1/2)", "1")

    enable_tfo  = True
    enable_alpn = True
    fp_choice   = "chrome"

    if tweak_mode == "1" and mode == "1" and final_ips and nodes:
        test_ip = final_ips[0]
        tcp_avg, tcp_min, tcp_jit, tcp_loss = tcp_ping_multi(test_ip, 443)
        tls_lat, tls_ok = tls_handshake_test(test_ip, sni=SCAN_SNI, port=443)
        _, _, _, colo   = probe_http_trace(test_ip, 443)

        logs = [
            f"Reference IP : {test_ip}   Colo: {colo or '─'}",
            f"TCP  avg={tcp_avg:.0f} ms   min={tcp_min:.0f} ms   jitter={tcp_jit:.0f} ms   loss={tcp_loss:.0f}%",
            f"TLS  {f'{tls_lat:.0f} ms ✓' if tls_lat > 0 else 'BLOCKED by local DPI — configs still work via xray'}",
            "Selected profile: fp=chrome (alt: safari)   ALPN=ON   TFO=ON",
        ]
        print_box("AI AUTO-PILOT BENCHMARK", logs)
        fp_choice = "chrome"; enable_alpn = True; enable_tfo = True

        if tls_lat < 0:
            print(
                f"    {CLR_WARN}⚠   Local TLS scan is blocked — this is normal in heavily filtered "
                f"networks.\n    {CLR_WARN}    Your configs use xray internally and bypass this layer.{CLR_RESET}"
            )

    elif tweak_mode == "2":
        if mode == "1":
            enable_tfo  = ask("Enable TCP Fast Open (TFO)? (y/n)", "y").lower() in ("y", "yes")
            enable_alpn = ask("Enable ALPN (http/1.1, h2)? (y/n)",  "y").lower() in ("y", "yes")
            print(f"    {CLR_CYAN}TLS Fingerprint:{CLR_RESET} [1]Chrome  [2]Safari  [3]Firefox  [4]Edge  [5]Random")
            fp_choice = FINGERPRINT_MAP.get(ask("Select (1-5)", "1"), "chrome")
        else:
            enable_tfo = enable_alpn = False

    # ── Build output links ────────────────────────────────────────────────────
    compiled: list = []

    if mode == "1" and len(nodes) == 1 and final_ips:
        compiled = saturation_mode(nodes[0], final_ips, custom_name or nodes[0].remarks)
    else:
        alt_fp = "safari" if fp_choice != "safari" else "chrome"
        for idx, node in enumerate(nodes, 1):
            name = custom_name or node.remarks
            if mode == "1" and final_ips:
                for ip in final_ips:
                    tag = f"_{xray_results[ip]:.0f}ms" if ip in xray_results else ""
                    compiled.append(build_vless_link(node, ip, node.port, fp_choice, enable_alpn, enable_tfo, f"{name}_{idx}⚡{tag}"))
                    compiled.append(build_vless_link(node, ip, node.port, alt_fp,    False,       enable_tfo, f"{name}_{idx}🛡️{tag}"))
            else:
                compiled.append(build_vless_link(node, node.address, node.port, fp_choice, enable_alpn, enable_tfo, f"{name}_{idx}"))

    if not compiled:
        print(f"    {CLR_ERROR}❌  No links were generated.{CLR_RESET}")
        return

    # ── Write output files ────────────────────────────────────────────────────
    ts         = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    prefix     = custom_name if custom_name else "VLESS"
    plain_file = f"{prefix}_{ts}_configs.txt"
    b64_file   = f"{prefix}_{ts}_sub.txt"

    try:
        with open(plain_file, "w", encoding="utf-8") as f:
            f.write("\n".join(compiled) + "\n")
        with open(b64_file, "w", encoding="utf-8") as f:
            f.write(base64.b64encode("\n".join(compiled).encode()).decode())
    except OSError as e:
        print(f"    {CLR_ERROR}❌  File write error: {e}{CLR_RESET}")
        return

    # ── Success Screen ────────────────────────────────────────────────────────
    w = 72
    print(f"\n{CLR_SUCCESS}{'═'*w}{CLR_RESET}")
    print(f"   {CLR_SUCCESS}✅   Operation completed successfully!{CLR_RESET}")
    print(f"{CLR_GRAY}   {'─'*w}{CLR_RESET}")
    print(f"   {CLR_TEXT}⚡  Total links built   : {CLR_SUCCESS}{len(compiled)}{CLR_RESET}")
    print(f"   {CLR_TEXT}⚡  Clean IPs injected  : {CLR_SUCCESS}{len(final_ips)}{CLR_RESET}")
    if xray_results:
        print(f"   {CLR_TEXT}⚡  xray validated      : {CLR_SUCCESS}{len(xray_results)} IP(s){CLR_RESET}")
    print(f"   {CLR_TEXT}⚡  Plain config file   : {CLR_CYAN}'{plain_file}'{CLR_RESET}")
    print(f"   {CLR_TEXT}⚡  Base64 subscription : {CLR_CYAN}'{b64_file}'{CLR_RESET}")
    print(f"{CLR_SUCCESS}{'═'*w}{CLR_RESET}")
    log.info(f"Done: {len(compiled)} links -> {plain_file}")


# ─── Entry Point ───────────────────────────────────────────────────────────────
if __name__ == "__main__":
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print(f"\n\n    {CLR_WARN}⚠   Session cancelled by user.{CLR_RESET}")
        except Exception as e:
            print(f"\n    {CLR_ERROR}❌  Unexpected error: {e}{CLR_RESET}")
            log.exception("Unhandled exception in main()")

        if not pause_or_restart():
            print(f"\n    {CLR_GRAY}Goodbye. — {AUTHOR} · {TELEGRAM}{CLR_RESET}\n")
            break
        draw_header()
