#!/usr/bin/env python3
import argparse
import time
from lib_SMML import SMMLEstimator

# Using raw string (r) to handle escape sequences in ASCII art
BANNER = r'''
   _____ __  __ __  __ __         _______   __
  / ____|  \/  |  \/  | |        |  __ \ \ / /
 | (___ | \  / | \  / | |    ___ | |__) \ V / 
  \___ \| |\/| | |\/| | |    ___ |  ___/ > <  
  ____) | |  | | |  | | |___     | |    / . \ 
 |_____/|_|  |_|_|  |_|____/     |_|   /_/ \_\ 
                                             
      SMML-PSM Trainer
      Probabilistic Password Strength Meter
      Based on Markov Model with Length Consideration
      Version 1.0
'''

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Train SMML Model and Calculate Thresholds")
    parser.add_argument("-i", "--input", required=True, help="Path to training dataset (passwords)")
    parser.add_argument("-o", "--output", default="SMML_model.pkl", help="Output path for the trained model file")
    
    args = parser.parse_args()

    start_time = time.time()

    # 1. Initialize Estimator
    estimator = SMMLEstimator()

    # 2. Train (Learn N-grams)
    estimator.train(args.input)

    # 3. Compute Thresholds (Mean + StdDev logic)
    estimator.compute_thresholds(args.input)

    # 4. Save Model
    estimator.save_model(args.output)

    elapsed = time.time() - start_time
    print(f"\n[+] Process finished in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()