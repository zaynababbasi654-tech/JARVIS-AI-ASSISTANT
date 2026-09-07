import platform
import psutil
from datetime import datetime


def get_system_info():

    # CPU
    processor = platform.processor()

    if not processor:
        processor = platform.machine()

    # RAM
    total_ram = psutil.virtual_memory().total
    available_ram = psutil.virtual_memory().available

    total_ram_gb = total_ram / (1024 ** 3)
    available_ram_gb = available_ram / (1024 ** 3)

    # Storage
    disk = psutil.disk_usage("/")

    total_storage_gb = disk.total / (1024 ** 3)
    free_storage_gb = disk.free / (1024 ** 3)

    # Operating system
    operating_system = platform.system()
    version = platform.version()

    # CPU usage
    cpu_usage = psutil.cpu_percent(interval=1)

    # RAM usage
    ram_usage = psutil.virtual_memory().percent

    return {
        "operating_system": operating_system,
        "version": version,
        "processor": processor,
        "total_ram_gb": round(total_ram_gb, 2),
        "available_ram_gb": round(available_ram_gb, 2),
        "ram_usage_percent": ram_usage,
        "total_storage_gb": round(total_storage_gb, 2),
        "free_storage_gb": round(free_storage_gb, 2),
        "cpu_usage_percent": cpu_usage,
    }


def format_system_info():

    info = get_system_info()

    return f"""
System Information:

Operating System: {info["operating_system"]}
System Version: {info["version"]}

Processor: {info["processor"]}

Total RAM: {info["total_ram_gb"]} GB
Available RAM: {info["available_ram_gb"]} GB
RAM Usage: {info["ram_usage_percent"]}%

Total Storage: {info["total_storage_gb"]} GB
Free Storage: {info["free_storage_gb"]} GB

CPU Usage: {info["cpu_usage_percent"]}%
""".strip()


if __name__ == "__main__":

    print("=" * 55)
    print("JARVIS SYSTEM INFORMATION")
    print("=" * 55)

    print(format_system_info())