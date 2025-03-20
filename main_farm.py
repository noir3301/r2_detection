import sys
from PyQt6.QtGui import *
from PyQt6.QtCore import *
from PyQt6.QtWidgets import *
from handlers import *
from threading import Thread, Event as tr_Event
from multiprocessing import Process, Manager, Event as mp_Event


class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFixedSize(24, 24)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("""
                    MainWindow {
                        background-color: rgba(0, 215, 55,    0);             
                    }
                """)
        self.widget = Widget(self)
        self.setCentralWidget(self.widget)
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint | Qt.WindowType.X11BypassWindowManagerHint)
        self.move(767, 1038)

class Widget(QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.button = PicButton()
        self.layout.addWidget(self.button)

class PicButton(QAbstractButton):
    def __init__(self, parent=None):
        super(PicButton, self).__init__(parent)
        self.pixmap_dict = {False: QPixmap("icons/png-deactivated.png"), True: QPixmap("icons/png-activated.png")}
        self.pixmap_current = [False, self.pixmap_dict[False]]
        self.threads_stop_event = tr_Event()
        self.multiprocess_stop_event = mp_Event()
        self.stop_by_key = StopByKey()
        self.attack = AttackByDetection()

    def sizeHint(self):
        return self.pixmap_current[1].size()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), self.pixmap_current[1])

    def mousePressEvent(self, event):
        if not self.pixmap_current[0]: # if deactivated and clicked
            self.multi_run()
        else:                          # if activated and clicked
            self.multi_stop()

    def multi_run(self):
        self.pixmap_current = [not self.pixmap_current[0], self.pixmap_dict[not self.pixmap_current[0]]]
        self.threads_stop_event.clear(), self.multiprocess_stop_event.clear()
        self.stop_by_key.network.signal.connect(self.multi_stop)
        tr_stop = Thread(target=self.stop_by_key.listener)
        tr_stop.start()

        tr_skills = Thread(target=skills_handler, args=(self.threads_stop_event, ))
        tr_heal = Thread(target=heal_handler, args=(self.threads_stop_event, ))

        tr_mouse = Thread(target=self.attack.mouse_handler, args=(self.threads_stop_event,))
        pr_monsters = Process(target=self.attack.get_monsters, args=(
        self.multiprocess_stop_event, self.attack.shared_dict, self.attack.shared_is_updated))
        
        tr_skills.start()
        tr_heal.start()
        tr_mouse.start()
        pr_monsters.start()

    def multi_stop(self):
        self.pixmap_current = [not self.pixmap_current[0], self.pixmap_dict[not self.pixmap_current[0]]]
        self.threads_stop_event.set(), self.multiprocess_stop_event.set()
        self.stop_by_key.network.signal.disconnect(self.multi_stop)
        self.update_icon(self.pixmap_current[1])

    def update_icon(self, pix):
        painter = QPainter(self)
        painter.drawPixmap(self.rect(), pix)
        self.update()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()