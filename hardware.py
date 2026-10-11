"""Diagnostico do PC: CPU, RAM, GPUs, Windows, e amostragem de uso de CPU (sem instalar nada)."""
import json, os, platform, time
from .proc import run

SYS32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")


def _ps(script, timeout=12):
    if os.name != "nt":
        return None
    code, out = run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script], timeout)
    try:
        return json.loads(out.strip())
    except ValueError:
        return None


def cpu_info():
    d = _ps("Get-CimInstance Win32_Processor | Select-Object -First 1 Name,NumberOfCores,NumberOfLogicalProcessors,MaxClockSpeed | ConvertTo-Json -Compress")
    if isinstance(d, dict):
        return {"name": str(d.get("Name", "?")).strip(), "cores": d.get("NumberOfCores"), "threads": d.get("NumberOfLogicalProcessors"), "mhz": d.get("MaxClockSpeed")}
    return {"name": platform.processor() or "CPU", "cores": None, "threads": os.cpu_count(), "mhz": None}


def ram_info():
    d = _ps("$o=Get-CimInstance Win32_OperatingSystem; [PSCustomObject]@{T=[math]::Round($o.TotalVisibleMemorySize/1MB,1);F=[math]::Round($o.FreePhysicalMemory/1MB,1)} | ConvertTo-Json -Compress")
    return {"total_gb": d.get("T"), "free_gb": d.get("F")} if isinstance(d, dict) else {"total_gb": None, "free_gb": None}


def gpu_list():
    d = _ps("Get-CimInstance Win32_VideoController | Select-Object Name,DriverVersion,AdapterRAM | ConvertTo-Json -Compress")
    if d is None:
        return []
    out = []
    for g in ([d] if isinstance(d, dict) else d):
        ram = g.get("AdapterRAM")
        out.append({"name": g.get("Name", "?"), "driver": g.get("DriverVersion", "?"), "vram_mb": int(ram) // 1048576 if isinstance(ram, int) and ram > 0 else None})
    return out


def graphics_libs():
    """So diz se a BIBLIOTECA existe. NAO significa que ajude a codificar video (isso so o teste real de encoder diz)."""
    if os.name != "nt":
        return {}
    return {n: os.path.exists(os.path.join(SYS32, f)) for n, f in (("DirectX 12 (d3d12.dll)", "d3d12.dll"), ("OpenGL", "opengl32.dll"),
                                                                  ("Vulkan", "vulkan-1.dll"), ("OpenCL", "OpenCL.dll"))}


def windows_name():
    return "%s %s" % (platform.system(), platform.version()) if os.name != "nt" else "Windows %s (build %s)" % (platform.release(), platform.version())


class CpuSampler:
    """Uso total de CPU (%) entre duas chamadas. Windows: GetSystemTimes. Linux: /proc/stat (so para testes)."""

    def __init__(self):
        self.prev = self._read()

    @staticmethod
    def _read():
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes
            i, k, u = wintypes.FILETIME(), wintypes.FILETIME(), wintypes.FILETIME()
            ctypes.windll.kernel32.GetSystemTimes(ctypes.byref(i), ctypes.byref(k), ctypes.byref(u))
            ft = lambda f: (f.dwHighDateTime << 32) | f.dwLowDateTime
            return ft(i), ft(k) + ft(u)                      # (ocioso, total)  (kernel inclui o ocioso)
        try:
            with open("/proc/stat") as f:
                v = [int(x) for x in f.readline().split()[1:]]
            return v[3] + (v[4] if len(v) > 4 else 0), sum(v)
        except OSError:
            return 0, 1

    def percent(self):
        idle, total = self._read(); pi, pt = self.prev; self.prev = (idle, total)
        dt = total - pt
        return max(0.0, min(100.0, 100.0 * (1 - (idle - pi) / dt))) if dt > 0 else 0.0
