from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QComboBox, 
    QDoubleSpinBox, QGroupBox, QRadioButton, QPushButton, QLabel
)
from PyQt6.QtCore import pyqtSignal

class ConfigTab(QWidget):
    """
    Configuration Tab UI.
    """
    
    start_simulation_signal = pyqtSignal(str, float, str, float)

    # Инициализирует вкладку конфигурации
    # Вход: Нет
    # Выход: Новый экземпляр виджета
    def __init__(self):
        super().__init__()
        self._init_ui()

    # Создает и размещает элементы управления (слайдеры, кнопки)
    # Вход: Нет
    # Выход: Нет
    def _init_ui(self):
        layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.combo_pattern = QComboBox()
        self.combo_pattern.addItems(["T", "L", "X"])
        form_layout.addRow("Select Pattern:", self.combo_pattern)

        self.spin_noise = QDoubleSpinBox()
        self.spin_noise.setRange(0.0, 0.50)
        self.spin_noise.setSingleStep(0.01)
        self.spin_noise.setDecimals(2)
        self.spin_noise.setValue(0.45)
        form_layout.addRow("Noise Level (0.00 - 0.50):", self.spin_noise)

        layout.addLayout(form_layout)

        self.group_mode = QGroupBox("Solver Stopping Criteria")
        mode_layout = QVBoxLayout()

        self.radio_time = QRadioButton("Fixed Time Duration")
        self.radio_time.setChecked(True)
        self.radio_accuracy = QRadioButton("Target Accuracy (Overlap %)")

        self.spin_param = QDoubleSpinBox()
        self.spin_param.setRange(0.1, 100.0)
        self.spin_param.setValue(3.0)
        self.label_param = QLabel("Duration (simulated seconds):")

        self.radio_time.toggled.connect(self._update_param_label)
        self.radio_accuracy.toggled.connect(self._update_param_label)

        mode_layout.addWidget(self.radio_time)
        mode_layout.addWidget(self.radio_accuracy)
        mode_layout.addWidget(self.label_param)
        mode_layout.addWidget(self.spin_param)
        
        self.group_mode.setLayout(mode_layout)
        layout.addWidget(self.group_mode)

        self.btn_start = QPushButton("INITIALIZE & RUN SIMULATION")
        self.btn_start.setStyleSheet("""
            QPushButton {
                font-weight: bold; 
                padding: 12px; 
                background-color: #2ecc71; 
                color: white;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_start.clicked.connect(self._on_start_clicked)
        layout.addWidget(self.btn_start)

        layout.addStretch()
        self.setLayout(layout)

    # Обновляет подписи и пределы спинбокса при смене режима (Время/Точность)
    # Вход: Нет
    # Выход: Нет
    def _update_param_label(self):
        if self.radio_time.isChecked():
            self.label_param.setText("Duration (simulated seconds):")
            self.spin_param.setDecimals(2)
            self.spin_param.setSingleStep(1.0)
            self.spin_param.setValue(3.0)
            self.spin_param.setMaximum(100.0)
        else:
            self.label_param.setText("Target Overlap (0.0 - 1.0):")
            self.spin_param.setDecimals(3)
            self.spin_param.setSingleStep(0.005)
            self.spin_param.setValue(0.950)
            self.spin_param.setMaximum(1.0)

    # Собирает данные из полей и отправляет сигнал запуска симуляции
    # Вход: Нет
    # Выход: Нет
    def _on_start_clicked(self):
        pattern = self.combo_pattern.currentText()
        noise = self.spin_noise.value()
        
        if self.radio_time.isChecked():
            mode = "time"
        else:
            mode = "accuracy"
            
        param = self.spin_param.value()
        
        self.start_simulation_signal.emit(pattern, noise, mode, param)