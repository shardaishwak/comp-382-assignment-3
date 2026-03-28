"""Hint system with BFS-based solution simulation."""

from typing import List, Optional, Tuple, Dict, Set
from collections import deque
from state import Hint, HintType
from config import MIN_MOVES

def find_all_solutions(dominos, work_seq, max_depth=12, max_solutions=10):
    """
    BFS to find all solutions from current state.
    Increased max_depth for Hard/Expert difficulties.
    """
    top_so = ''.join(dominos[i]['top'] for i in work_seq)
    bot_so = ''.join(dominos[i]['bot'] for i in work_seq)
    
    solutions = []
    start_state = (top_so, bot_so, tuple(work_seq))
    queue = deque([(start_state, 0)])
    visited = {}
    
    while queue and len(solutions) < max_solutions:
        state, depth = queue.popleft()
        top, bot, path = state
        
        # Check if we have a solution
        if top == bot and depth >= MIN_MOVES:
            solutions.append((path, depth))
            continue
        
        # Stop if too deep - increased for Hard/Expert
        if depth >= max_depth:
            continue
        
        # Try each domino
        for i, d in enumerate(dominos):
            new_top = top + d['top']
            new_bot = bot + d['bot']
            new_path = path + (i,)
            
            # Early pruning: if prefixes don't match, skip
            min_len = min(len(new_top), len(new_bot))
            if new_top[:min_len] != new_bot[:min_len]:
                continue
            
            new_state = (new_top, new_bot, new_path)
            
            # Check if we've seen this state with a shorter path
            if new_state not in visited or visited[new_state] > depth + 1:
                visited[new_state] = depth + 1
                queue.append((new_state, depth + 1))
    
    return solutions, len(solutions) > 0

def score_with_bfs(d_idx, top_so, bot_so, seq_len, solutions, has_solution, dominos):
    """
    Score a domino based on BFS solution analysis.
    """
    # Get the actual domino data
    d = dominos[d_idx]
    nt = top_so + d['top']
    nb = bot_so + d['bot']
    
    # Check if this domino creates a solution immediately
    if nt == nb:
        nl = seq_len + 1
        if nl >= MIN_MOVES:
            return 100.0, HintType.PERFECT_MATCH, f"Completes the match with {nl} dominos — you win!"
        return 95.0, HintType.PERFECT_MATCH, f"Strings match but need {MIN_MOVES - nl} more domino(s) first."
    
    # Check if this domino appears in any solution path
    solutions_with_this = []
    min_solution_len = float('inf')
    
    for sol_path, sol_len in solutions:
        if len(sol_path) > seq_len and sol_path[seq_len] == d_idx:
            solutions_with_this.append((sol_path, sol_len))
            if sol_len < min_solution_len:
                min_solution_len = sol_len
    
    if solutions_with_this:
        # This domino is part of at least one solution
        num_solutions = len(solutions_with_this)
        shortest_solution = min_solution_len
        
        # Calculate score based on solution length and frequency
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
    
    # Check prefix matches (might lead to solutions)
    if nt.startswith(nb):
        r = len(nt) - len(nb)
        if r <= 3:
            return 65.0, HintType.EXACT_PREFIX, \
                   f"Top leads by {r} — good prefix, likely leads to solution"
        return 55.0, HintType.EXACT_PREFIX, \
               f"Top leads by {r} — add dominos that grow the bottom"
    
    if nb.startswith(nt):
        r = len(nb) - len(nt)
        if r <= 3:
            return 65.0, HintType.EXACT_PREFIX, \
                   f"Bottom leads by {r} — good prefix, likely leads to solution"
        return 55.0, HintType.EXACT_PREFIX, \
               f"Bottom leads by {r} — add dominos that grow the top"
    
    # Check balance improvement (might help reach solutions)
    orig_gap = abs(len(top_so) - len(bot_so))
    new_gap = abs(len(nt) - len(nb))
    
    if new_gap < orig_gap:
        reduction = orig_gap - new_gap
        if reduction >= 2:
            return 60.0, HintType.BALANCING, \
                   f"Reduces gap by {reduction} — helps work toward solutions"
        return 50.0, HintType.BALANCING, \
               "Reduces the length gap — step in the right direction"
    
    # No strong signal
    if not has_solution:
        return 0.0, HintType.EXPLORATORY, "No solution possible from current state — try clearing or restarting"
    return 0.0, HintType.EXPLORATORY, ""

def compute_hints(dominos, work_seq):
    """
    Compute hints using BFS to find actual solutions.
    """
    # Dynamically adjust search depth based on difficulty
    # Estimate required depth: current length + min_solution_moves + buffer
    current_len = len(work_seq)
    
    # Determine search depth based on current progress
    # For Hard/Expert, we need deeper search
    if current_len < 3:
        # Early game - search deeper to find possible paths
        search_depth = 14
    elif current_len < 6:
        # Mid game
        search_depth = 12
    else:
        # Late game - closer to solution
        search_depth = 10
    
    # Find all solutions from current state
    solutions, has_solution = find_all_solutions(
        dominos, work_seq, 
        max_depth=search_depth, 
        max_solutions=10
    )
    
    top_so = ''.join(dominos[i]['top'] for i in work_seq)
    bot_so = ''.join(dominos[i]['bot'] for i in work_seq)
    
    hints = []
    for i, d in enumerate(dominos):
        # Pass the index and dominos list
        score, hint_type, explanation = score_with_bfs(
            i, top_so, bot_so, len(work_seq), solutions, has_solution, dominos
        )
        
        # Show hints based on solution availability
        if has_solution:
            # Solutions exist - show verified hints (75+)
            if score >= 75.0:
                hints.append(Hint(i, score, explanation, hint_type))
            # Also show good prefix/balance hints if no verified ones found
            elif not hints and score >= 50.0:
                hints.append(Hint(i, score, explanation, hint_type))
        else:
            # No solutions found - show best available guidance
            if score >= 50.0:
                hints.append(Hint(i, score, explanation, hint_type))
    
    # If no solutions found, provide clear feedback
    if not has_solution:
        if not hints:
            # Create a special hint with clear message
            hints.append(Hint(-1, 0.0, 
                            "No solution possible from current position within search depth. Try clearing and restarting, or choose a different first domino.", 
                            HintType.EXPLORATORY))
        else:
            # Add a warning that solutions might not exist
            hints.append(Hint(-2, 0.0,
                            "Warning: No guaranteed solutions found within search depth. Consider resetting if stuck.",
                            HintType.EXPLORATORY))
    
    # Sort by score (highest first)
    hints.sort(key=lambda h: h.score, reverse=True)
    
    return hints, (hints[0] if hints else None)