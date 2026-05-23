# Deception in LLM Agents: Effects of Text Decomposition in Social Deduction Games

This repository contains the code and simulation environment for our senior research project on detecting deception in LLM agents. We use a text-based simulation of the game *Among Us* to study how AI agents learn to express lying and deception, and specifically investigate whether **text decomposition** improves the detectability of these signals within a model's internal activations.

## Overview

> **Attribution Notice:** This repository is a cloned and modified version of the original [*AmongUs* sandbox by 7vik](https://github.com/7vik/AmongUs). We have adapted their foundational simulation and probing architecture to run locally via Ollama and specifically tailored it to test our text decomposition hypotheses.

Large language model (LLM) agents are increasingly deployed in real-world environments that require reasoning and decision-making under incomplete or misleading information. This project simulates an *Among Us* environment—featuring hidden roles, cooperation, and strategic communication—to compare how well linear probes can detect factual lying versus general deception from an LLM's hidden states.

<img src="https://static.wikia.nocookie.net/among-us-wiki/images/f/f5/Among_Us_space_key_art_redesign.png" alt="Among Us" width="400"/>

## Prerequisites: Ollama

Unlike other implementations that rely on paid APIs (like OpenRouter or OpenAI), this project is designed to run entirely locally using [Ollama](https://ollama.com/). 

Before running the simulation or evaluations, ensure Ollama is installed and the required models are pulled to your machine:

```bash
# Pull the agent model used for gameplay
ollama pull qwen2.5:1.5b-instruct

# Pull the evaluator model used for labeling deception
ollama pull llama3.1:8b
```

## Setup

1. Clone the repository:
   ```bash
   git clone XXXX
   cd AmongUs
   ```

2. Set up the environment:
   ```bash
   conda create -n amongus python=3.10
   conda activate amongus
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install numpy pandas networkx streamlit dotenv requests aiohttp
   ```

4. Configure your environment file:
Create a .env file in the root directory of the project to redirect the code's API calls to your local Ollama instance:
   ```bash
   OPENROUTER_API_BASE="http://localhost:11434/v1"
   OPENROUTER_API_KEY="ollama"
   ```

## Run Games

To run the sandbox and simulate games using Qwen-2.5-1.5B-Instruct locally via Ollama, run:

```
main.py
```

## Caching Activations

Once the (full) game logs are in place, use the following command to cache the activations of the LLMs:

```
python linear-probes/cache_activations.py --dataset <dataset_name>
```

This loads up the HuggingFace models and caches the activations of the specified layers for each game action step. This step is computationally expensive, so it is recommended to run this using GPUs.

Use `configs.py` to specify the model and layer to cache, and other configuration options.

## LLM-based Evaluation (for Lying, Awareness, Deception, and Planning)

Once the game logs are generated, we use our secondary local model (llama3.1:8b) to act as an evaluator. The evaluator reads the game steps and scores them on a 1-to-10 scale for awareness, lying, deception, and planning.

To run the evaluations and generate ground-truth labels, run:

```
bash evaluations/run_evals.sh
```


## Training Linear Probes

Once the activations are cached, training linear probes is easy. Just run:

```
python linear-probes/train_probes.py
```
You can choose which datasets to train probes on - by default, it will train on all datasets.

## Evaluating Linear Probes

To evaluate the linear probes, run:

```
python linear-probes/evaluate_probes.py
```
You can choose which datasets to evaluate probes on - by default, it will evaluate on all datasets.

It will store the results in `linear-probes/results/`, which are used to generate the plots in the paper.

## Project Structure

```plaintext
.
├── CONTRIBUTING.md         # Contribution guidelines
├── Dockerfile               # Docker setup for project environment
├── LICENSE                  # License information
├── README.md                # Project documentation (this file)
├── among-agents             # Main code for the Among Us agents
│   ├── README.md            # Documentation for agent implementation
│   ├── amongagents          # Core agent and environment modules
│   ├── envs                 # Game environment and configurations
│   ├── evaluation           # Evaluation scripts for agent performance
│   ├── notebooks            # Jupyter notebooks for running experiments
│   ├── requirements.txt     # Python dependencies for agents
│   └── setup.py             # Setup script for agent package
├── expt-logs                # Experiment logs
├── k8s                      # Kubernetes configurations for deployment
├── main.py                  # Main entry point for running the game
├── notebooks                # Additional notebooks (not part of the main project)
├── reports                  # Experiment reports
├── requirements.txt         # Python dependencies for main project
├── tests                    # Unit tests for project functionality
└── utils.py                 # Utility functions
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute to this project.

## License

This project is licensed under CC0 1.0 Universal - see [LICENSE](LICENSE).

## Acknowledgments

- Our game logic uses a bunch of code from [AmongAgents](https://github.com/cyzus/among-agents).

If you face any bugs or issues with this codebase, please contact Satvik Golechha (7vik) at zsatvik@gmail.com.