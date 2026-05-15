import json
import numpy as np
import os

def analyze_irt_file(filepath, label):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return

    with open(filepath, 'r') as f:
        data = json.load(f)
    
    # Extract the lists from your specific JSON structure
    abilities = data.get("ability", [])
    difficulties = data.get("diff", [])
    
    if not difficulties:
        print(f"❌ No difficulty data found in {label}")
        return

    avg_b = np.mean(difficulties)
    min_b = np.min(difficulties)
    max_b = np.max(difficulties)
    theta = abilities[0] if abilities else "N/A"

    print(f"--- {label} Results ---")
    print(f"Probe Strength (Theta): {theta}")
    print(f"Average Difficulty (b): {avg_b:.4f}")
    print(f"Range: [{min_b:.2f} to {max_b:.2f}]")
    print(f"Number of items: {len(difficulties)}")
    print("-" * 30)

# Run the analysis
print("=======================================")
print("   IRT BASELINE DIFFICULTY ANALYSIS    ")
print("=======================================")

analyze_irt_file('./irt_results_lying/best_parameters.json', 'LYING')
analyze_irt_file('./irt_results_deception/best_parameters.json', 'DECEPTION')

print("=======================================")