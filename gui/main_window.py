from PyQt6.QtWidgets import QMainWindow, QTabWidget, QMessageBox
from .config_tab import ConfigTab
from .results_tab import ResultsTab
import numpy as np

from core.patterns import PatternGenerator
from core.networks.hopfield import HopfieldNetwork
from core.networks.synergetic import SynergeticComputer
from core.solver import RKSolver

class MainWindow(QMainWindow):
    """
    Main Application Window.
    Implementing strict mathematical synchronization: lambda = beta - 1.
    """

    # Инициализирует главное окно приложения и вкладки
    # Вход: Нет
    # Выход: Новый экземпляр окна
    def __init__(self):
        super().__init__()
        
        self.setWindowTitle("Comparative Analysis: Hopfield vs Haken Dynamics")
        self.resize(1400, 900)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.tab_config = ConfigTab()
        self.tab_results = ResultsTab()

        self.tabs.addTab(self.tab_config, "Configuration")
        self.tabs.addTab(self.tab_results, "Simulation Results")
        
        self.tabs.setTabEnabled(1, False)
        self.tab_config.start_simulation_signal.connect(self.run_simulation)

    # Выполняет основной цикл симуляции: подготовка данных, создание моделей, запуск решателя
    # Вход: pattern_key (имя буквы), noise (уровень шума), mode (режим), param (параметр остановки)
    # Выход: Нет (обновляет GUI)
    def run_simulation(self, pattern_key, noise, mode, param):
        try:
            patterns_dict = PatternGenerator.get_all_patterns()
            keys = ["T", "L", "X"] 
            patterns_list = [patterns_dict[k] for k in keys]
            target_idx = keys.index(pattern_key)
            target_pattern = patterns_list[target_idx]

            noisy_input = PatternGenerator.apply_noise(target_pattern, noise)
            
            size = 32 * 32
            
            # --- MATHEMATICAL PARAMETERS ---
            beta_val = 10.0
            
            # growth_hopfield = beta - 1
            # growth_haken = lambda
            # lambda = beta - 1
            lambda_val = beta_val - 1.0 # 9.0
            
            # 1 = sqrt(lambda / (B + C))  =>  B + C = lambda
            B_val = 0.1 * lambda_val  # 0.9
            C_val = 0.9 * lambda_val  # 8.1
            
            hopfield = HopfieldNetwork(size, decay=1.0, beta=beta_val) 
            hopfield.train(patterns_list)
            
            norm = np.linalg.norm(noisy_input)
            haken_input = noisy_input / norm if norm > 0 else noisy_input
            
            haken = SynergeticComputer(size, lambda_val=lambda_val, B=B_val, C=C_val)
            haken.train(patterns_list)

            common_dt = 0.01

            res_hop = RKSolver.solve(
                hopfield, noisy_input, mode, param, 
                dt=common_dt, target_pattern_idx=target_idx
            )
            
            res_syn = RKSolver.solve(
                haken, haken_input, mode, param, 
                dt=common_dt, target_pattern_idx=target_idx 
            )

            input_summary = {
                'target': target_pattern,
                'noisy': noisy_input,
                'name': pattern_key,
                'noise_lvl': noise
            }
            
            self.tab_results.render_results(input_summary, res_hop, res_syn, keys)

            self.tabs.setTabEnabled(1, True)
            self.tabs.setCurrentIndex(1)

        except Exception as e:
            QMessageBox.critical(self, "Simulation Error", f"An error occurred:\n{str(e)}")
            raise e