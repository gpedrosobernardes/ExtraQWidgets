import sys

from PySide6.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QLabel

from qextrawidgets.icons import QThemeResponsiveIcon
from qextrawidgets.widgets.color_button import QColorButton


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(300, 300)

        self.setWindowTitle("QColorButton Demo")
        self.setWindowIcon(QThemeResponsiveIcon.fromAwesome("fa6b.python"))

        widget = QWidget()

        layout = QVBoxLayout()

        # 1. Standard Buttons
        layout.addWidget(QLabel("Standard Buttons:"))
        color_button_1 = QColorButton("Color Button 1 (Blue)", "#0077B6")
        color_button_2 = QColorButton("Color Button 2 (Red)", "#CC2936")
        color_button_3 = QColorButton("Color Button 3 (Custom Text)", "#C5D86D", "#000000")
        
        layout.addWidget(color_button_1)
        layout.addWidget(color_button_2)
        layout.addWidget(color_button_3)

        layout.addSpacing(20)

        # 2. Toggle Button (Checked Color)
        layout.addWidget(QLabel("Toggle Button (Blue <-> Red):"))
        
        # Create a checkable button with distinct colors for Normal and Checked states
        self.toggle_btn = QColorButton(
            text="Click to Toggle (Blue)", 
            color="#0077B6",           # Normal Color (Blue)
            checked_color="#CC2936"    # Checked Color (Red)
        )
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.toggled.connect(self.on_toggle)
        
        layout.addWidget(self.toggle_btn)

        widget.setLayout(layout)
        self.setCentralWidget(widget)

    def on_toggle(self, checked: bool):
        if checked:
            self.toggle_btn.setText("Checked (Red)")
        else:
            self.toggle_btn.setText("Unchecked (Blue)")


if __name__ == '__main__':
    app = QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
