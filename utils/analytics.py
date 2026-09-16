import numpy as np

class SimulationAnalyzer:
    """
    Helper class for statistics and reports.
    """

    # Вычисляет долю энергии (Share) каждого паттерна на основе квадратов амплитуд
    # Вход: overlaps (массив амплитуд)
    # Выход: Массив нормированных долей (сумма = 1.0)
    @staticmethod
    def _compute_energy_shares(overlaps: np.ndarray) -> np.ndarray:
        pos_overlaps = np.maximum(overlaps, 0.0)
        energies = np.square(pos_overlaps)
        
        if energies.ndim == 1:
            total = np.sum(energies)
            if total < 1e-9: return np.ones_like(energies) / len(energies)
            return energies / total
        
        else:
            total = np.sum(energies, axis=1, keepdims=True)
            # Защита от деления на 0
            total[total < 1e-9] = 1.0
            return energies / total

    # Определяет победителя соревнования паттернов
    # Вход: final_overlaps (массив амплитуд), pattern_names (список имен)
    # Выход: Словарь с информацией о победителе, амплитуде и доле
    @staticmethod
    def identify_winner(final_overlaps: np.ndarray, pattern_names: list[str]) -> dict:
        winner_idx = np.argmax(final_overlaps)
        winner_name = pattern_names[winner_idx]
        winner_overlap = final_overlaps[winner_idx]

        # Считаем доли энергии для вывода в отчет
        shares = SimulationAnalyzer._compute_energy_shares(final_overlaps)
        share_pct = shares[winner_idx]

        return {
            "winner_idx": winner_idx,
            "winner_name": winner_name,
            "overlap": winner_overlap,
            "share": share_pct
        }

    # Генерирует краткий HTML отчет для боковой панели интерфейса
    # Вход: model_name (строка), result (словарь решения), target_name (цель), pattern_names (список)
    # Выход: Строка с HTML разметкой
    @staticmethod
    def generate_short_report(model_name: str, result: dict, target_name: str, pattern_names: list[str]) -> str:
        final_overlaps = result["overlaps"][-1]
        winner = SimulationAnalyzer.identify_winner(final_overlaps, pattern_names)
        
        success = result["success"]
        final_time = result["final_time"]
        is_correct = (winner["winner_name"] == target_name)
        
        if is_correct:
            status_html = '<span style="color:lightgreen">SUCCESS</span>'
        else:
            status_html = '<span style="color:#ff6666">FAIL</span>'
        
        return (
            f"<b>{model_name}</b><br>"
            f"Result: {status_html}<br>"
            f"Time: {final_time:.2f}s<br>"
            f"Id: {winner['winner_name']} (Share: {winner['share']*100:.1f}%)<br>"
            f"Ampl: {winner['overlap']:.4f}"
        )
    
    # Подготавливает данные для графика Stackplot (преобразует в доли энергии)
    # Вход: overlaps (2D массив истории амплитуд)
    # Выход: 2D массив долей энергии
    @staticmethod
    def prepare_stacked_data(overlaps: np.ndarray) -> np.ndarray:
        return SimulationAnalyzer._compute_energy_shares(overlaps)