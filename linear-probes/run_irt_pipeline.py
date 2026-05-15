import subprocess
import json
import numpy as np
import os

def run_py_irt(input_file, output_dir):
    """Uses subprocess to run the py-irt CLI command from within Python."""
    print(f"🚀 Training IRT Model on {input_file}...")
    
    # Create the output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # This simulates typing the exact command into your terminal
    subprocess.run([
        "py-irt", "train", "1pl", 
        input_file, 
        output_dir
    ], check=True)
    
    print(f"✅ Training complete. Results saved to {output_dir}\n")

def get_average_difficulty(results_path):
    """Opens the py-irt output and calculates the average item difficulty (b)."""
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    item_params = data.get('item_params', {})
    difficulties = []
    
    for item_id, params in item_params.items():
        # py-irt 1PL models store difficulty under 'diff' or 'b'
        diff_score = params.get('diff', params.get('b', [0]))[0]
        difficulties.append(diff_score)
        
    if not difficulties:
        return "No scores found."
        
    return np.mean(difficulties)

if __name__ == "__main__":
    # Define your paths
    lying_data = "results/AmongUsDataset_qwen_2_5_1_5b/baseline_irt_lying.jsonlines"
    deception_data = "results/AmongUsDataset_qwen_2_5_1_5b/baseline_irt_deception.jsonlines"
    
    lying_out = "./irt_results_lying/"
    deception_out = "./irt_results_deception/"

    # 1. Run the Training
    run_py_irt(lying_data, lying_out)
    run_py_irt(deception_data, deception_out)

    # 2. Extract and Average the Results
    lying_b = get_average_difficulty(os.path.join(lying_out, "best_parameters.json"))
    deception_b = get_average_difficulty(os.path.join(deception_out, "best_parameters.json"))

    # 3. Print the Final Report
    print("=======================================")
    print("  BASELINE AVERAGE ITEM DIFFICULTY (b) ")
    print("=======================================")
    print(f"Lying (Fact Contradiction):   {lying_b:.3f}")
    print(f"Deception (Imposter Persona): {deception_b:.3f}")
    print("=======================================")