from PIL import ImageGrab
from pynput.keyboard import Listener as kb_Listener
import keyboard as kb
from functions import *
from variables import *
from network import Network
from detection import Detection
from multiprocessing import Manager, Value as mp_Value


def heal_handler(tr_stop_event):
    while not tr_stop_event.is_set():
        if not is_full_hp():
            for _ in range(10):
                kb.send(HEAL_KEY)
                time.sleep(0.206)
        else:
            time.sleep(0.35)

def skills_handler(tr_stop_event):
    while not tr_stop_event.is_set():
        if is_attacking() and pixel_color_at(CRIT_CORD[0], CRIT_CORD[1])[0] >= CRIT_COLOR:
            kb.send(CRIT_KEY)
        if is_attacking() and pixel_color_at(DESTR_CORD[0], DESTR_CORD[1])[0] >= DESTR_COLOR:
            kb.send(DESTR_KEY)
        time.sleep(0.35)


class AttackByDetection:
    def __init__(self):
        self.detection = Detection()
        manager = Manager()
        self.shared_dict = manager.dict()
        self.shared_is_updated = mp_Value('b', 0)

    def get_monsters(self, pr_stop_event, shared_dict, shared_is_updated):
        while not pr_stop_event.is_set():
            tmp = self.detection.process_image(ImageGrab.grab(bbox = None))
            for key in tmp:
                shared_dict[key] = tmp[key]
            shared_is_updated.value = True
            time.sleep(PROCESS_IMAGE_DELAY)

    def mouse_handler(self, tr_stop_event):
        while not tr_stop_event.is_set():
            if self.shared_is_updated.value:
                self.shared_is_updated.value = False
                for key in MOB_TYPES:
                    if tr_stop_event.is_set() or self.shared_is_updated.value:
                        break
                    if len(self.shared_dict[key]) > 0:
                        for mob in self.shared_dict[key]:
                            if tr_stop_event.is_set() or self.shared_is_updated.value:
                                break
                            if key == 'aggressive' and mob['distance'] < MAX_AGGRESSIVE_MOB_DISTANCE:
                                self.mouse_attack(mob['click'])
                            elif key == 'neutral':
                                self.mouse_attack(mob['click'])
            if not self.shared_is_updated.value:
                time.sleep(0.35)
            else:
                time.sleep(0.13)

    @staticmethod
    def mouse_attack(cords):
        mouse.move(int(cords[0]), int(cords[1]), absolute=True, duration=0.13)
        time.sleep(0.06)
        if is_cursor_attack():
            mouse_click()
            while is_attacking():
                time.sleep(0.20)


class StopByKey:

    def __init__(self):
        self.network = Network()

    def listener(self):
        l = kb_Listener(on_release=self.on_release)
        l.start()
        l.join()

    def on_release(self, key):
        if hasattr(key, 'char') and key.char in EXIT_KEYS:
            self.network.emit_signal()
            return False
