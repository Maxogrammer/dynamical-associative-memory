import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
    QSlider, QPushButton, QGroupBox, QStyle
)
from PyQt6.QtCore import Qt, QTimer

from .canvas import MplCanvas
from utils.image_processing import vector_to_image
from utils.analytics import SimulationAnalyzer

class ResultsTab(QWidget):
    """
    Visualization Tab.
    """

    # Инициализирует вкладку результатов
    # Вход: Нет
    # Выход: Новый экземпляр виджета
    def __init__(self):
        super().__init__()
        
        self.data_hop = None
        self.data_syn = None
        self.input_info = None
        
        self.is_playing = False
        self.current_time_ratio = 0.0
        self.max_duration = 0.0
        self.timer_interval = 30
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._on_timer_tick)

        self._init_ui()

    # Создает сетку лейаута, графики matplotlib и элементы управления плеером
    # Вход: Нет
    # Выход: Нет
    def _init_ui(self):
        layout = QHBoxLayout()

        col1 = QVBoxLayout()
        col1.setContentsMargins(0, 0, 10, 0)
        
        group_input = QGroupBox("Input Data")
        layout_input = QVBoxLayout()
        
        self.lbl_target_info = QLabel("Target: ?")
        self.lbl_target_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_noise_info = QLabel("Noise: ?")
        self.lbl_noise_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.canvas_target = MplCanvas(width=3, height=3, dpi=80)
        self.canvas_noisy = MplCanvas(width=3, height=3, dpi=80)
        
        layout_input.addWidget(self.lbl_target_info)
        layout_input.addWidget(self.canvas_target)
        layout_input.addSpacing(10)
        layout_input.addWidget(self.lbl_noise_info)
        layout_input.addWidget(self.canvas_noisy)
        layout_input.addStretch()
        
        group_input.setLayout(layout_input)
        col1.addWidget(group_input)

        col2 = QVBoxLayout()
        
        self.group_hop = QGroupBox("Hopfield Network Dynamics")
        layout_hop = QHBoxLayout()
        
        self.canvas_hop_img = MplCanvas(width=3, height=3, dpi=90)
        self.canvas_hop_plot = MplCanvas(width=5, height=3, dpi=90)
        
        layout_hop.addWidget(self.canvas_hop_img, 1)
        layout_hop.addWidget(self.canvas_hop_plot, 2)
        self.group_hop.setLayout(layout_hop)
        
        self.group_syn = QGroupBox("Synergetic Computer Dynamics")
        layout_syn = QHBoxLayout()
        
        self.canvas_syn_img = MplCanvas(width=3, height=3, dpi=90)
        self.canvas_syn_plot = MplCanvas(width=5, height=3, dpi=90)
        
        layout_syn.addWidget(self.canvas_syn_img, 1)
        layout_syn.addWidget(self.canvas_syn_plot, 2)
        self.group_syn.setLayout(layout_syn)
        
        controls = QHBoxLayout()
        
        self.btn_play = QPushButton()
        self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.btn_play.clicked.connect(self._toggle_play)
        
        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(0, 1000)
        self.slider.sliderMoved.connect(self._on_slider_move)
        self.slider.sliderPressed.connect(self._on_slider_press)
        
        self.lbl_time = QLabel("0.00s")
        self.lbl_time.setFixedWidth(60)

        controls.addWidget(self.btn_play)
        controls.addWidget(self.slider)
        controls.addWidget(self.lbl_time)

        col2.addWidget(self.group_hop, 4)
        col2.addWidget(self.group_syn, 4)
        col2.addLayout(controls, 1)

        col3 = QVBoxLayout()
        col3.setContentsMargins(10, 0, 0, 0)
        
        group_stats = QGroupBox("Simulation Results")
        layout_stats = QVBoxLayout()
        
        style_sheet = "border: 1px solid #555; padding: 10px; background: #2b2b2b; color: #eee; font-size: 11px;"
        
        self.text_hop_stats = QLabel("No Data")
        self.text_hop_stats.setWordWrap(True)
        self.text_hop_stats.setStyleSheet(style_sheet)
        
        self.text_syn_stats = QLabel("No Data")
        self.text_syn_stats.setWordWrap(True)
        self.text_syn_stats.setStyleSheet(style_sheet)

        layout_stats.addWidget(QLabel("<b>Hopfield Summary:</b>"))
        layout_stats.addWidget(self.text_hop_stats)
        layout_stats.addSpacing(20)
        layout_stats.addWidget(QLabel("<b>Haken Summary:</b>"))
        layout_stats.addWidget(self.text_syn_stats)
        layout_stats.addStretch()
        
        group_stats.setLayout(layout_stats)
        col3.addWidget(group_stats)

        layout.addLayout(col1, 2)
        layout.addLayout(col2, 7)
        layout.addLayout(col3, 2)
        
        self.setLayout(layout)

    # Загружает данные симуляции, обновляет графики и статистику
    # Вход: input_data (словарь), hop_data (результат), syn_data (результат), pattern_keys (список)
    # Выход: Нет
    def render_results(self, input_data: dict, hop_data: dict, syn_data: dict, pattern_keys: list):
        self.data_hop = hop_data
        self.data_syn = syn_data
        self.input_info = input_data
        self.pattern_keys = pattern_keys
        
        t_h = hop_data['times'][-1]
        t_s = syn_data['times'][-1]
        self.max_duration = max(t_h, t_s)
        
        self._plot_static_image(self.canvas_target, input_data['target'], "Target Pattern")
        self._plot_static_image(self.canvas_noisy, input_data['noisy'], "Initial Input")
        self.lbl_target_info.setText(f"Target: <b>{input_data['name']}</b>")
        self.lbl_noise_info.setText(f"Noise: <b>{input_data['noise_lvl']*100:.0f}%</b>")

        report_h = SimulationAnalyzer.generate_short_report("Hopfield", hop_data, input_data['name'], pattern_keys)
        self.text_hop_stats.setText(report_h)
        
        report_s = SimulationAnalyzer.generate_short_report("Haken", syn_data, input_data['name'], pattern_keys)
        self.text_syn_stats.setText(report_s)

        self._setup_stacked_chart(self.canvas_hop_plot, hop_data, "Hopfield")
        self._setup_stacked_chart(self.canvas_syn_plot, syn_data, "Haken")
        
        self.current_time_ratio = 0.0
        self.slider.setValue(0)
        self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        self.is_playing = False
        self.timer.stop()
        
        self._update_frame()

    # Отрисовывает статичное черно-белое изображение на канвасе
    # Вход: canvas (виджет), vector (данные), title (заголовок)
    # Выход: Нет
    def _plot_static_image(self, canvas, vector, title):
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        
        from utils.image_processing import vector_to_image
        img = vector_to_image(vector)
        ax.imshow(img, cmap='gray', vmin=-1, vmax=1)
        ax.set_title(title, fontsize=9)
        ax.axis('off')
        canvas.draw()

    # Настраивает и рисует график Stacked Area Chart
    # Вход: canvas (виджет), data (результаты), title (заголовок)
    # Выход: Нет
    def _setup_stacked_chart(self, canvas, data, title):
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        
        times = data['times']
        overlaps = data['overlaps']
        
        stack_data = SimulationAnalyzer.prepare_stacked_data(overlaps).T 
        
        labels = self.pattern_keys
        colors = ['#ff9999', '#66b3ff', '#99ff99'] 
        
        ax.stackplot(times, *stack_data, labels=labels, colors=colors, alpha=0.8)
        
        ax.set_xlim(0, self.max_duration)
        ax.set_ylim(0, 1.0)
        ax.set_yticks([]) 
        ax.set_title(f"{title} Dynamics (Similarity Share)", fontsize=10)
        if title == "Haken":
            ax.set_xlabel("Time (s)")
            ax.legend(loc='lower right', fontsize='x-small', framealpha=0.5)
        
        self.vlines = getattr(self, 'vlines', {})
        self.vlines[title] = ax.axvline(x=0, color='black', linestyle='--', linewidth=1.5)
        
        canvas.draw()

    # Переключает состояние воспроизведения
    # Вход: Нет
    # Выход: Нет
    def _toggle_play(self):
        if self.is_playing:
            self.is_playing = False
            self.timer.stop()
            self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        else:
            if self.current_time_ratio >= 1.0:
                self.current_time_ratio = 0.0
                
            self.is_playing = True
            self.timer.start(self.timer_interval)
            self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPause))

    # Обрабатывает нажатие на слайдер
    # Вход: Нет
    # Выход: Нет
    def _on_slider_press(self):
        if self.is_playing:
            self.timer.stop()

    # Обрабатывает движение слайдера
    # Вход: val
    # Выход: Нет
    def _on_slider_move(self, val):
        self.current_time_ratio = val / 1000.0
        self._update_frame()

    # Обрабатывает тик таймера анимации
    # Вход: Нет
    # Выход: Нет
    def _on_timer_tick(self):
        step = (self.timer_interval / 1000.0) / self.max_duration 
        if self.max_duration > 20: step *= 5 
        
        self.current_time_ratio += step
        
        if self.current_time_ratio >= 1.0:
            self.current_time_ratio = 1.0
            self.is_playing = False
            self.timer.stop()
            self.btn_play.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_MediaPlay))
        
        self.slider.blockSignals(True)
        self.slider.setValue(int(self.current_time_ratio * 1000))
        self.slider.blockSignals(False)
        
        self._update_frame()

    # Обновляет кадр визуализации
    # Вход: Нет
    # Выход: Нет
    def _update_frame(self):
        if not self.data_hop: return

        current_time = self.current_time_ratio * self.max_duration
        self.lbl_time.setText(f"{current_time:.2f}s")

        self._update_single_image(self.canvas_hop_img, self.data_hop, current_time, auto_contrast=False)
        self._update_single_image(self.canvas_syn_img, self.data_syn, current_time, auto_contrast=True)

        if 'Hopfield' in self.vlines:
            self.vlines['Hopfield'].set_xdata([current_time])
            self.canvas_hop_plot.draw_idle() 
            
        if 'Haken' in self.vlines:
            self.vlines['Haken'].set_xdata([current_time])
            self.canvas_syn_plot.draw_idle()

    # Обновляет отдельное изображение
    # Вход: canvas, data, t_target, auto_contrast
    # Выход: Нет
    def _update_single_image(self, canvas, data, t_target, auto_contrast=False):
        times = data['times']
        idx = np.searchsorted(times, t_target)
        if idx >= len(times): idx = len(times) - 1
        
        state = data['states'][idx]
        from utils.image_processing import vector_to_image
        img = vector_to_image(state)
        
        canvas.fig.clear()
        ax = canvas.fig.add_subplot(111)
        
        if auto_contrast:
            vmin = np.min(img)
            vmax = np.max(img)
            if vmax - vmin < 1e-6: 
                vmin, vmax = -1, 1
            ax.imshow(img, cmap='gray', vmin=vmin, vmax=vmax)
        else:
            ax.imshow(img, cmap='gray', vmin=-1, vmax=1)
            
        ax.axis('off')
        canvas.draw()