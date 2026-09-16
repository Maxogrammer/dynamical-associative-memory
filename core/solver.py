import numpy as np
from .networks.base import DynamicNetwork

class RKSolver:
    """
    Runge-Kutta 4 solver with precision clamping.
    """

    MODE_TIME = "time"
    MODE_ACCURACY = "accuracy"

    # Решает систему дифференциальных уравнений методом Рунге-Кутты 4
    # Вход: model (объект сети), initial_state (вектор), mode (режим), param (лимит), dt (шаг), target_pattern_idx (индекс цели)
    # Выход: Словарь с историей времени, состояний, перекрытий и статусом успеха
    @staticmethod
    def solve(
        model: DynamicNetwork,
        initial_state: np.ndarray,
        mode: str,
        param: float,
        dt: float = 0.01,
        target_pattern_idx: int = 0
    ) -> dict:
        
        t = 0.0
        state = initial_state.copy()
        
        times = [t]
        states = [state.copy()]
        
        current_overlaps = [model.get_overlap(state, i) for i in range(len(model.patterns))]
        overlaps = [current_overlaps]

        max_steps = 100000
        step = 0
        success = False

        while step < max_steps:
            current_dt = dt

            if mode == RKSolver.MODE_TIME:
                if t >= param:
                    success = True
                    break
                if t + dt > param:
                    current_dt = param - t
            else:
                if current_overlaps[target_pattern_idx] >= param:
                    success = True
                    break
                if t > 50.0:
                    success = False
                    break

            k1 = model.dynamics(state)
            k2 = model.dynamics(state + 0.5 * current_dt * k1)
            k3 = model.dynamics(state + 0.5 * current_dt * k2)
            k4 = model.dynamics(state + current_dt * k3)
            
            derivative = (k1 + 2*k2 + 2*k3 + k4) / 6.0
            new_state = state + current_dt * derivative
            new_t = t + current_dt

            if mode == RKSolver.MODE_ACCURACY:
                new_overlaps = [model.get_overlap(new_state, i) for i in range(len(model.patterns))]
                if new_overlaps[target_pattern_idx] >= param:
                    state = new_state
                    t = new_t
                    times.append(t)
                    states.append(state.copy())
                    overlaps.append(new_overlaps)
                    success = True
                    break

            state = new_state
            t = new_t
            step += 1

            times.append(t)
            states.append(state.copy())
            
            current_overlaps = [model.get_overlap(state, i) for i in range(len(model.patterns))]
            overlaps.append(current_overlaps)

        return {
            "times": np.array(times),
            "states": np.array(states), 
            "overlaps": np.array(overlaps), 
            "success": success,
            "final_time": t
        }