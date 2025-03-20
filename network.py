from PyQt6.QtCore import QObject, pyqtSignal


class Network(QObject):
    signal = pyqtSignal()

    def emit_signal(self):
        self.signal.emit()