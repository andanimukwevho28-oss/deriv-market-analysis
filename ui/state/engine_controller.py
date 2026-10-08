import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FEED_SCRIPT = ROOT / "deriv_public_ws.py"
LOG_PATH = ROOT / "feed.log"
_process = None
_log_handle = None


def is_running():
    return _process is not None and _process.poll() is None


def start():
    global _process, _log_handle
    if is_running():
        return False
    _log_handle = LOG_PATH.open("a", encoding="utf-8")
    _process = subprocess.Popen(
        [sys.executable, "-u", str(FEED_SCRIPT)],
        cwd=ROOT,
        stdout=_log_handle,
        stderr=subprocess.STDOUT,
        env=None,
    )
    return True


def stop():
    global _process, _log_handle
    if not is_running():
        return False
    _process.terminate()
    try:
        _process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        _process.kill()
        _process.wait(timeout=5)
    _process = None
    if _log_handle:
        _log_handle.close()
        _log_handle = None
    return True
