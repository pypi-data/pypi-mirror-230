# 아키텍처별로 사용할 모듈을 가져옵니다.
import platform

# 현재 아키텍처를 확인합니다.
architecture = platform.machine()

if architecture == 'x86_64':
    from .x86_64 import nnfw_api_pybind
elif architecture == 'armv7l':
    from .armv7l import nnfw_api_pybind
elif architecture == 'aarch64':
    from .aarch64 import nnfw_api_pybind
else:
    raise ImportError(f"Unsupported architecture: {architecture}")
