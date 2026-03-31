"""Hint system with BFS-based solution simulation for PCPGameState."""

from collections import deque
from typing import List, Tuple, Optional
from .pcp_game_state import PCPGameState, Domino


class HintType:
    """Types of hints with priority levels."""
    PERFECT_MATCH = 5
    EXACT_PREFIX = 4
    PARTIAL_PREFIX = 3
    BALANCING = 2
    EXPLORATORY = 1


class Hint:
    """A hint for a specific domino."""
    def __init__(self, idx: int, score: float, explanation: str, htype: int):
        self.idx = idx
        self.score = score
        self.explanation = explanation
        self.htype = htype


def find_all_solutions(
    game_state: PCPGameState,
    max_depth: int = 12,
    max_solutions: int = 10
) -> Tuple[List[Tuple[List[int], int]], bool]:
    """
    BFS to find all solutions from current state.
    Uses PCPGameState's instance and current sequence.
    """
    top_so = game_state._top_str
    bot_so = game_state._bottom_str
    work_seq = [pd.domino.id for pd in game_state.sequence]
    
    solutions = []
    start_state = (top_so, bot_so, tuple(work_seq))
    queue = deque([(start_state, 0)])
    visited = {}
    
    while queue and len(solutions) < max_solutions:
        state, depth = queue.popleft()
        top, bot, path = state
        
        if top == bot and depth >= 1:
            solutions.append((list(path), depth))
            continue
        
        if depth >= max_depth:
            continue
        
        for domino in game_state.instance:
            new_top = top + domino.top_str
            new_bot = bot + domino.bottom_str
            new_path = path + (domino.id,)
            
            min_len = min(len(new_top), len(new_bot))
            if new_top[:min_len] != new_bot[:min_len]:
                continue
            
            new_state = (new_top, new_bot, new_path)
            
            if new_state not in visited or visited[new_state] > depth + 1:
                visited[new_state] = depth + 1
                queue.append((new_state, depth + 1))
    
    return solutions, len(solutions) > 0


def score_with_bfs(
    domino: Domino,
    game_state: PCPGameState,
    solutions: List[Tuple[List[int], int]],
    has_solution: bool
) -> Tuple[float, int, str]:
    """
    Score a domino based on BFS solution analysis.
    """
    top_so = game_state._top_str
    bot_so = game_state._bottom_str
    seq_len = len(game_state.sequence)
    
    nt = top_so + domino.top_str
    nb = bot_so + domino.bottom_str
    
    if nt == nb:
        nl = seq_len + 1
        return 100.0, HintType.PERFECT_MATCH, f"Completes the match with {nl} dominoes — you win!"
    
    solutions_with_this = []
    min_solution_len = float('inf')
    
    for sol_path, sol_len in solutions:
        if len(sol_path) > seq_len and sol_path[seq_len] == domino.id:
            solutions_with_this.append((sol_path, sol_len))
            if sol_len < min_solution_len:
                min_solution_len = sol_len
    
    if solutions_with_this:
        num_solutions = len(solutions_with_this)
        shortest_solution = min_solution_len
        
        if shortest_solution == seq_len + 1:
            return 98.0, HintType.PERFECT_MATCH, \
                   f"Leads to a solution in {shortest_solution} moves — take it!"
        elif shortest_solution <= seq_len + 3:
            return 90.0, HintType.EXACT_PREFIX, \
                   f"Part of solution in {shortest_solution} total moves ({shortest_solution - seq_len - 1} more)"
        elif num_solutions >= 3:
            return 85.0, HintType.EXACT_PREFIX, \
                   f"Appears in {num_solutions} different solutions — very promising!"
        else:
            return 75.0, HintType.EXACT_PREFIX, \
                   f"Part of a solution in {shortest_solution} total moves"
    
    if nt.startswith(nb):
        r = len(nt) - len(nb)
        if r <= 3:
            return 65.0, HintType.PARTIAL_PREFIX, \
                   f"Top leads by {r} — good prefix, likely leads to solution"
        return 55.0, HintType.PARTIAL_PREFIX, \
               f"Top leads by {r} — add dominoes that grow the bottom"
    
    if nb.startswith(nt):
        r = len(nb) - len(nt)
        if r <= 3:
            return 65.0, HintType.PARTIAL_PREFIX, \
                   f"Bottom leads by {r} — good prefix, likely leads to solution"
        return 55.0, HintType.PARTIAL_PREFIX, \
               f"Bottom leads by {r} — add dominoes that grow the top"
    
    orig_gap = abs(len(top_so) - len(bot_so))
    new_gap = abs(len(nt) - len(nb))
    
    if new_gap < orig_gap:
        reduction = orig_gap - new_gap
        if reduction >= 2:
            return 60.0, HintType.BALANCING, \
                   f"Reduces gap by {reduction} — helps work toward solutions"
        return 50.0, HintType.BALANCING, \
               "Reduces the length gap — step in the right direction"
    
    if not has_solution:
        return 0.0, HintType.EXPLORATORY, "No solution possible from current state — try clearing or restarting"
    return 0.0, HintType.EXPLORATORY, ""


def compute_hints(game_state: PCPGameState) -> Tuple[List[Hint], Optional[Hint]]:
    """
    Compute hints using BFS to find actual solutions.
    """
    current_len = len(game_state.sequence)
    
    if current_len < 3:
        search_depth = 14
    elif current_len < 6:
        search_depth = 12
    else:
        search_depth = 10
    
    solutions, has_solution = find_all_solutions(
        game_state,
        max_depth=search_depth,
        max_solutions=10
    )
    
    hints = []
    for domino in game_state.instance:
        score, hint_type, explanation = score_with_bfs(
            domino, game_state, solutions, has_solution
        )
        
        if has_solution:
            if score >= 75.0:
                hints.append(Hint(domino.id, score, explanation, hint_type))
            elif not hints and score >= 50.0:
                hints.append(Hint(domino.id, score, explanation, hint_type))
        else:
            if score >= 50.0:
                hints.append(Hint(domino.id, score, explanation, hint_type))
    
    if not has_solution:
        if not hints:
            hints.append(Hint(-1, 0.0, 
                            "No solution possible from current position within search depth. Try clearing and restarting, or choose a different first domino.", 
                            HintType.EXPLORATORY))
        else:
            hints.append(Hint(-2, 0.0,
                            "Warning: No guaranteed solutions found within search depth. Consider resetting if stuck.",
                            HintType.EXPLORATORY))
    
    hints.sort(key=lambda h: h.score, reverse=True)
    
    return hints, (hints[0] if hints else None)