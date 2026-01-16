# SMML-PSM: Simple Markov Model with Length consideration - Password Strength Meter

**SMML-PSM** is a lightweight, probabilistic password strength estimation tool based on the research: "A Study on Markov-Based Password Strength Meters".

Unlike traditional entropy-based meters that treat all password lengths equally, SMML-PSM learns the probability distribution of character transitions specific to each password length. This approach allows for a more accurate assessment of user-created passwords by capturing length-dependent patterns.

## Features

* **Length-Dependent Modeling:** Learns separate simple Markov models for different password lengths (e.g., patterns in 8-char passwords differ from 12-char ones).
* **Automatic Thresholding:** Automatically calculates `WEAK`, `NORMAL`, and `STRONG` thresholds based on the statistical distribution (Mean + 2/3 StdDev) of the training set.
* **Lightweight & Fast:** Serialized into a single `.pkl` file for quick loading and inference.
* **Flexible Input:** Supports both raw password lists and frequency lists (e.g., RockYou format).

## Requirements

* Python 3.x
* NumPy

```Bash
pip install numpy
```

## Usage

The tool consists of two main components: trainer.py (to build the model) and meter.py (to evaluate passwords).

1. Training the Model

To train a new model from a password dataset:

```Bash
python3 trainer.py -i PATH_TO_DATASET -o MODEL_NAME.pkl
```
-i: Path to the training dataset (UTF-8). Can be a list of passwords or count password format.

-o: Output path for the trained model file. e.g., my_model.pkl

2. Evaluating Passwords

* Interactive Mode: Simply run the meter with the trained model to enter interactive mode:

```Bash
python3 meter.py -m MODEL_NAME.pkl
```

Output example:

>> Enter password: password123

   Score: 14.520 | Label: 0 (WEAK)

* File Processing Mode: To evaluate a large list of passwords:

```Bash
python3 meter.py -m MODEL_NAME -i INPUT_FILE -o OUTPUT_FILE
```

-i: Input file containing passwords.

-o: Output file (Format: password label_id). Labels: 0 (Weak), 1 (Normal), 2 (Strong).

## Tool Structure
lib_SMML.py: Core library containing the SMMLEstimator class and logic.

trainer.py: Script to train the model and calculate thresholds.

meter.py: Script to evaluate password strength.

## Citation
If you use this tool in your research, please cite our paper:

@article{thai2024study,
  title={A study on markov-based password strength meters},
  author={Thai, Binh Le Thanh and Tanaka, Hidema},
  journal={IEEE Access},
  volume={12},
  pages={69066--69075},
  year={2024},
  publisher={IEEE}
}
