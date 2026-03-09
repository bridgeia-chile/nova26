"""
Hardware Utility
Detection of GPU and other hardware features.
"""
import logging

def is_gpu_available() -> bool:
    """Detects if an NVIDIA GPU is available using pynvml."""
    try:
        import pynvml
        pynvml.nvmlInit()
        device_count = pynvml.nvmlDeviceGetCount()
        pynvml.nvmlShutdown()
        return device_count > 0
    except Exception:
        return False
