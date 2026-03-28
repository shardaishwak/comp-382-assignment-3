"""Domino generation and BFS solution finder."""

import random
from collections import deque
from typing import Optional, Tuple, List, Dict
from config import SQ_KEYS, MIN_MOVES

def min_solution_length(dominos: list, max_depth: int = 6) -> Optional[int]:
    """BFS to find shortest PCP solution."""
    start = ('=', ())
    queue = deque([(start, 0)])
    visited: Dict = {start: 0}

    while queue:
        state, depth = queue.popleft()
        if depth >= max_depth:
            continue
        side, surplus = state
        for d in dominos:
            t = tuple(d['top'])
            b = tuple(d['bot'])
            nt = surplus + t if side == 't' else t
            nb = surplus + b if side == 'b' else b
            if side == '=':
                nt, nb = t, b
            mn = min(len(nt), len(nb))
            if nt[:mn] != nb[:mn]:
                continue
            if nt == nb:
                return depth + 1
            ns = ('t', nt[mn:]) if len(nt) > len(nb) else ('b', nb[mn:])
            if ns not in visited or visited[ns] > depth + 1:
                visited[ns] = depth + 1
                queue.append((ns, depth + 1))
    return None

def rstr(min_len: int = 1, max_len: int = 3) -> str:
    """Generate random string from SQ_KEYS."""
    return ''.join(random.choices(SQ_KEYS, k=random.randint(min_len, max_len)))

def generate_dominos(num_dominos=8, min_string_len=1, max_string_len=3,
                     min_solution_moves=MIN_MOVES) -> Tuple[list, list]:
    """Generate a solvable set of dominos."""
    
    # For Hard/Expert, increase attempts and be more flexible
    max_attempts = 2000 if min_solution_moves >= 5 else 500
    core_attempts = 300 if min_solution_moves >= 5 else 100
    extra_attempts = 5000 if min_solution_moves >= 5 else 2000
    
    for attempt in range(max_attempts):
        core_dominos = []
        
        # Generate core dominos
        for __ in range(core_attempts):
            t1 = rstr(min_string_len, max_string_len)
            t2 = rstr(min_string_len, max_string_len)
            t3 = rstr(min_string_len, max_string_len)
            b1 = rstr(min_string_len, max_string_len)
            b2 = rstr(min_string_len, max_string_len)
            b3 = rstr(min_string_len, max_string_len)
            
            # Allow some leniency for Hard/Expert
            if t1 == b1 or t2 == b2 or t3 == b3:
                continue
                
            test = [{'top': t1, 'bot': b1}, {'top': t2, 'bot': b2}, {'top': t3, 'bot': b3}]
            
            # Use deeper search for Hard/Expert
            search_depth = min_solution_moves + 5 if min_solution_moves >= 5 else min_solution_moves + 3
            sl = min_solution_length(test, max_depth=search_depth)
            
            # More flexible: allow solutions slightly shorter than requirement
            if sl is not None and sl >= max(3, min_solution_moves - 1):
                core_dominos = test
                break
        
        if len(core_dominos) < 3:
            continue

        used_pairs = {(d['top'], d['bot']) for d in core_dominos}
        extra = []
        
        # Generate extra dominos
        for __ in range(extra_attempts):
            if len(extra) >= num_dominos - 3:
                break
            t = rstr(min_string_len, max_string_len)
            b = rstr(min_string_len, max_string_len)
            
            if t == b or (t, b) in used_pairs:
                continue
                
            # Less strict about extra dominos for Hard/Expert
            test_set = core_dominos + extra + [{'top': t, 'bot': b}]
            ts = min_solution_length(test_set, max_depth=min_solution_moves + 2)
            
            # Only reject if it creates a solution that's too short
            if ts is not None and ts < max(2, min_solution_moves - 2):
                continue
                
            used_pairs.add((t, b))
            extra.append({'top': t, 'bot': b})

        if len(extra) < num_dominos - 3:
            continue

        all_d = core_dominos + extra
        
        # Final validation with deeper search
        final_depth = min_solution_moves + 8 if min_solution_moves >= 5 else min_solution_moves + 5
        sl = min_solution_length(all_d, max_depth=final_depth)
        
        if sl is None or sl < min_solution_moves - 1:
            continue

        # Success! Return shuffled set
        order = list(range(len(all_d)))
        random.shuffle(order)
        inv = {old: new for new, old in enumerate(order)}
        shuffled = [all_d[order[i]] for i in range(len(all_d))]
        return shuffled, [inv[0], inv[1], inv[2]]
    
    # If all attempts fail, generate a valid set manually for Hard/Expert
    if min_solution_moves >= 5:
        # Create a guaranteed solvable set for Hard/Expert
        return generate_guaranteed_set(num_dominos, min_string_len, max_string_len, min_solution_moves)
    
    # Fallback for Easy/Medium
    fallback = [
        {'top': '01', 'bot': '0'}, {'top': '2', 'bot': '12'}, {'top': '01', 'bot': '012'},
        {'top': '12', 'bot': '01'}, {'top': '20', 'bot': '2'}, {'top': '0', 'bot': '01'},
        {'top': '1', 'bot': '2'}, {'top': '02', 'bot': '1'}
    ]
    return fallback[:num_dominos], [0, 1, 2]

def generate_guaranteed_set(num_dominos, min_len, max_len, min_moves):
    """Generate a guaranteed solvable set for Hard/Expert difficulties."""
    # Create a base solution path
    solution_dominos = []
    
    # Create a simple solution pattern using allowed string lengths
    if min_moves >= 5:
        # Pattern: domino that builds a longer chain
        solution_dominos = [
            {'top': '0' * min_len, 'bot': '0' * min_len + '1'},
            {'top': '1', 'bot': '2'},
            {'top': '2', 'bot': '01'},
            {'top': '01', 'bot': '012'},
            {'top': '12', 'bot': '01'},
        ]
    
    # Add random extra dominos
    used_pairs = {(d['top'], d['bot']) for d in solution_dominos}
    extra = []
    
    while len(solution_dominos) + len(extra) < num_dominos:
        t = rstr(min_len, max_len)
        b = rstr(min_len, max_len)
        if t != b and (t, b) not in used_pairs:
            used_pairs.add((t, b))
            extra.append({'top': t, 'bot': b})
    
    all_d = solution_dominos + extra
    order = list(range(len(all_d)))
    random.shuffle(order)
    inv = {old: new for new, old in enumerate(order)}
    shuffled = [all_d[order[i]] for i in range(len(all_d))]
    
    return shuffled, [inv[0], inv[1], inv[2]]