from plover.machine.base import ThreadedStenotypeBase
from plover.machine.keymap import Keymap
from plover.formatting import _Context, _Action
from plover import log

class OnscreenStenotype(ThreadedStenotypeBase):
    KEYS_LAYOUT = """
#  #  #  #  #  #  #  #  #  #
S- T- P- H- * -F -P -L -T -D
S- K- W- R- * -R -B -G -S -Z
      A- O-   -E -U
"""
    KEYMAP_MACHINE_TYPE = "TX Bolt"

    def __init__(self, params):
        super().__init__()
        
    def run(self):
        self._ready()

        # while not self.finished.wait(3):
        #     self._notify(self.keymap.keys_to_actions(["S-", "-G"]))


    def start_capture(self):
        super().start_capture()

    def stop_capture(self):
        super().stop_capture()

    @classmethod
    def get_option_info(cls):
        return {}

def custom_meta(ctx: _Context, arg: str) -> _Action:
    action = ctx.new_action()
    return action