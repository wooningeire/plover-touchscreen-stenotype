from plover.machine.base import ThreadedStenotypeBase

from typing import Any

class NoneMachine(ThreadedStenotypeBase):
    """Machine that does nothing"""

    KEYS_LAYOUT: str = ""

    def __init__(self, params: dict[str, Any]):
        super().__init__()
    
    def run(self):
        self._ready()

    def start_capture(self):
        super().start_capture()

    def stop_capture(self):
        super().stop_capture()

    @classmethod
    def get_option_info(cls):
        return {}