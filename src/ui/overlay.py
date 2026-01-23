from PyQt6.QtWidgets import QWidget, QRubberBand, QApplication, QSizeGrip, QVBoxLayout, QLabel, QPushButton, QHBoxLayout
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QColor, QPalette, QPen, QPainter

class OverlaySelector(QWidget):
    """
    Uma janela semitransparente que o usuário pode mover e redimensionar
    para selecionar a área de captura.
    """
    area_selected = pyqtSignal(int, int, int, int) # x, y, w, h

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Estilo visual
        self.setStyleSheet("background-color: rgba(255, 0, 0, 50); border: 2px solid red;")

        # Grip para redimensionar
        self.grip_layout = QVBoxLayout(self)
        self.grip_layout.setContentsMargins(0, 0, 0, 0)
        self.grip_layout.addStretch()

        # Label de instrução
        self.info_label = QLabel("Arraste e Redimensione.\n[ENTER] confirmar.\n[ESC] cancelar.", self)
        self.info_label.setStyleSheet("color: white; background-color: red; border: none; font-weight: bold;")
        self.grip_layout.addWidget(self.info_label, alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Botão de Confirmar
        h_layout = QHBoxLayout()
        h_layout.addStretch()
        
        self.btn_confirm = QPushButton("Confirmar Seleção", self)
        self.btn_confirm.setStyleSheet("background-color: rgba(255,255,255,200); color: black; font-weight: bold; border: 2px solid white;")
        self.btn_confirm.clicked.connect(self.confirm_selection)
        h_layout.addWidget(self.btn_confirm)

        # Adiciona SizeGrip no canto inferior direito
        self.size_grip = QSizeGrip(self)
        self.size_grip.setStyleSheet("background-color: transparent;")
        h_layout.addWidget(self.size_grip)
        self.grip_layout.addLayout(h_layout)

        # Variáveis para mover a janela
        self.old_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        self.old_pos = None

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.confirm_selection()
        elif event.key() == Qt.Key.Key_Escape:
            self.close()

    def confirm_selection(self):
        # Emite coordenadas relativas à tela
        # Cuidado com DPI scaling, mas mss geralmente lida bem com pixels físicos se configurado.
        # PyQt geometry() retorna coordenadas lógicas.
        # Para mss, precisamos garantir que bate.
        # Em muitos casos PyQt coordinates == Pixels se escala for 100%.
        # Se houver scaling, pode haver offset. Vamos assumir 1:1 por enquanto.
        g = self.geometry()
        self.area_selected.emit(g.x(), g.y(), g.width(), g.height())
        self.hide()

    def paintEvent(self, event):
        # Garante a borda vermelha desenhada customizada se o stylesheet falhar em frameless
        painter = QPainter(self)
        pen = QPen(Qt.GlobalColor.red)
        pen.setWidth(4)
        painter.setPen(pen)
        painter.drawRect(0, 0, self.width(), self.height())
