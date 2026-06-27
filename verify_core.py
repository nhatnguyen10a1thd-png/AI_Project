# verify_core.py
import sys
import os

# Add project root to sys.path to allow imports to work
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from core.level import LevelManager
from core.rules import BoardRules
from ai.solver_interface import ALGORITHMS, solve

def run_tests():
    print("==================================================")
    print("SQUIRRELS GO NUTS AI SOLVER - CORE LOGIC VERIFICATION")
    print("==================================================")
    
    # 1. Load Level Manager
    try:
        level_mgr = LevelManager()
        print("Level Manager loaded successfully.")
    except Exception as e:
        print(f"FAILED to load Level Manager: {e}")
        return

    # 2. Load Starter 01
    try:
        lvl, state = level_mgr.load_level("starter", "starter_01")
        print(f"Loaded level: {lvl['name']} ({lvl['difficulty']})")
        print(f"Holes: {state.holes}")
        print(f"Pieces: {list(state.pieces.keys())}")
    except Exception as e:
        print(f"FAILED to load level: {e}")
        return

    rules = BoardRules()
    
    # 3. Test Legal Actions
    actions = rules.legal_actions(state)
    print(f"Initial legal actions: {actions}")
    
    # 4. Test state transitions
    if actions:
        test_act = actions[0]
        next_state = rules.apply_action(state, test_act)
        print(f"Applied action {test_act}. New anchor of {test_act[0]}: {next_state.pieces[test_act[0]].anchor}")
    
    # 5. Run every registered algorithm and print search results
    print("\n==================================================")
    print(f"RUNNING ALL {len(ALGORITHMS)} REGISTERED ALGORITHMS ON STARTER 01")
    print("==================================================")
    
    for algo_name in ALGORITHMS.keys():
        print(f"\nRunning {algo_name}...")
        try:
            res = solve(algo_name, state, rules)
            print(f"Result: Solved={res.solved}, Length={len(res.path)}, Visited={res.visited_count}, Generated={res.generated_count}, Time={res.elapsed_time:.4f}s")
            if res.solved:
                print(f"Path: {res.path}")
        except Exception as e:
            print(f"ERROR running {algo_name}: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    run_tests()
