from enum import StrEnum as _StrEnum
import platform as _platform

class OSPlatform(_StrEnum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MAC_OS = "Darwin"
    JAVA = "Java"

def get_os_platform() -> OSPlatform:
    return OSPlatform(_platform.system())

def is_os_platform(os_platform: OSPlatform) -> bool:
    return _platform.system() == os_platform.value
