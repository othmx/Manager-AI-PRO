"""setup_env.py —— 一键准备运行环境（Python + frida + adb + 模拟器连接）

做四件事：
  1. 检查 Python 版本
  2. 安装 frida 16.5.9（脚本注入必需；17.x 移除了 Java bridge，不能用）
  3. 找 adb：环境变量 → PATH → MuMu 自带 → 都没有就自动下载 platform-tools
  4. 连接模拟器并跑 ultra0.py --check 自检

用法：双击 一键安装环境.bat，或 python setup_env.py
"""
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import urllib.request
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
ADB_CANDIDATES = [
    os.environ.get("ADB_PATH", ""),
    r"C:\Program Files\Netease\MuMuPlayer-12.0\shell\adb.exe",
    r"C:\Program Files\Netease\MuMuPlayerGlobal-12.0\shell\adb.exe",
    r"C:\Program Files (x86)\Netease\MuMuPlayer-12.0\shell\adb.exe",
    r"D:\Program Files\Netease\MuMu\nx_main\adb.exe",
    r"D:\Program Files\Netease\MuMu\nx_device\12.0\shell\adb.exe",
    r"C:\Program Files\Netease\MuMu\nx_main\adb.exe",
    os.path.expandvars(r"%LOCALAPPDATA%\Android\Sdk\platform-tools\adb.exe"),
    os.path.expandvars(r"%USERPROFILE%\AppData\Local\Android\Sdk\platform-tools\adb.exe"),
]
PLATFORM_TOOLS_URL = "https://dl.google.com/android/repository/platform-tools-latest-windows.zip"


def step(msg):
    print(f"\n▶ {msg}", flush=True)


def ok(msg):
    print(f"   ✅ {msg}", flush=True)


def warn(msg):
    print(f"   ⚠️  {msg}", flush=True)


def die(msg):
    print(f"\n❌ {msg}", flush=True)
    sys.exit(1)


def check_python():
    step("检查 Python")
    v = sys.version_info
    print(f"   {platform.python_version()}  ({platform.architecture()[0]})")
    if v < (3, 9):
        die("Python 版本太低，请安装 3.10 或更高：https://www.python.org/downloads/")
    ok("Python 可用")


def install_frida():
    step("安装 frida 16.5.9（注入必需）")
    try:
        import frida
        if frida.__version__.startswith("16."):
            ok(f"已安装 frida {frida.__version__}")
            return
        warn(f"当前是 frida {frida.__version__}，17.x 不能用，正在降级…")
    except Exception:
        pass

    cmds = [
        [sys.executable, "-m", "pip", "install", "--no-cache-dir", "frida==16.5.9"],
        [sys.executable, "-m", "pip", "install", "--no-cache-dir",
         "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", "frida==16.5.9"],
    ]
    for c in cmds:
        print("   " + " ".join(c[2:]))
        r = subprocess.run(c, capture_output=True, text=True, errors="ignore")
        if r.returncode == 0:
            break
        print("   " + (r.stderr or r.stdout).strip().splitlines()[-1][:160])
    try:
        import importlib
        import frida
        importlib.reload(frida)
        ok(f"frida {frida.__version__} 安装完成")
    except Exception as e:
        die(f"frida 安装失败：{e}\n   手动执行：pip install frida==16.5.9")


def download_platform_tools():
    dest = BASE / "platform-tools"
    print(f"   下载 platform-tools 到 {dest}")
    tmp = Path(tempfile.gettempdir()) / "platform-tools.zip"
    with urllib.request.urlopen(PLATFORM_TOOLS_URL, timeout=180) as r, open(tmp, "wb") as f:
        f.write(r.read())
    with zipfile.ZipFile(tmp) as z:
        z.extractall(BASE)
    tmp.unlink(missing_ok=True)
    adb = dest / "adb.exe"
    if adb.exists():
        ok(f"platform-tools 就绪：{adb}")
        return str(adb)
    die("platform-tools 解压后没找到 adb.exe")


def find_adb():
    step("查找 adb")
    for c in ADB_CANDIDATES:
        if not c:
            continue
        if c in ("adb", "adb.exe"):
            continue
        if Path(c).exists():
            ok(f"使用 {c}")
            return c
    w = shutil.which("adb")
    if w:
        ok(f"使用 PATH 里的 {w}")
        return w
    warn("没找到 adb，开始自动下载")
    return download_platform_tools()


def connect_emulator(adb):
    step("连接模拟器")
    ports = ["16384", "7555", "16416", "21503", "62001"]
    for p in ports:
        subprocess.run([adb, "connect", f"127.0.0.1:{p}"], capture_output=True, text=True, errors="ignore")
    out = subprocess.run([adb, "devices"], capture_output=True, text=True, errors="ignore").stdout
    devices = [l.split("\t")[0] for l in out.splitlines()[1:] if "\tdevice" in l]
    if not devices:
        warn("没有连上设备。请确认 MuMu 已启动，并在设置里开启 ADB 调试")
        print("   " + out.strip().replace("\n", "\n   "))
        return None
    ok(f"已连接：{', '.join(devices)}")
    return devices[0]


def run_check(adb, serial):
    step("运行环境自检（ultra0.py --check）")
    env = dict(os.environ)
    env["ADB_PATH"] = adb
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, "ultra0.py", "--check"], cwd=str(BASE),
                       env=env, capture_output=True, encoding="utf-8", errors="ignore")
    print(r.stdout.strip() or r.stderr.strip())
    return r.returncode == 0


def main():
    print("=" * 60)
    print("  Google Ultra / Pro 一键下单 · 环境安装")
    print("=" * 60)
    check_python()
    install_frida()
    adb = find_adb()
    serial = connect_emulator(adb)

    if serial:
        good = run_check(adb, serial)
        print("\n" + "=" * 60)
        if good:
            print("  ✅ 环境就绪，可以双击「2_Pro_12个月_第1步.bat」开始下单")
        else:
            print("  ⚠️  自检未全绿，看上面的提示处理（多半是 Play 商店没起来）")
        print("=" * 60)
    else:
        print("\n装好 MuMu 并开启 ADB 调试后，再运行一次本脚本。")


if __name__ == "__main__":
    main()
