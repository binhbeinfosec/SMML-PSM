#!/usr/bin/env python3
import argparse
import sys
import os
from lib_SMML import SMMLEstimator

BANNER = r'''
   _____ __  __ __  __ __        __  __      _            
  / ____|  \/  |  \/  | |       |  \/  |    | |           
 | (___ | \  / | \  / | |    ___| \  / | ___| |_ ___ _ __ 
  \___ \| |\/| | |\/| | |    ___| |\/| |/ _ \ __/ _ \ '__|
  ____) | |  | | |  | | |___    | |  | |  __/ ||  __/ |   
 |_____/|_|  |_|_|  |_|____/    |_|  |_|\___|\__\___|_|   
                                                          
      SMML-PSM Meter
      Interactive Password Strength Evaluator
      Version 1.0
'''

LABELS = {0: "WEAK", 1: "NORMAL", 2: "STRONG"}

def interactive_mode(estimator):
    """Interactive mode for manual password entry"""
    print("\n[+] Entering Interactive Mode.")
    print("[+] Type 'exit' or 'quit' to stop.\n")
    
    while True:
        try:
            pwd = input(">> Enter password: ").strip()
            if pwd.lower() in ['exit', 'quit']:
                break
            if not pwd:
                continue
            
            score = estimator.calculate_score(pwd)
            label_id = estimator.get_label(score)
            label_str = LABELS[label_id]
            
            print(f"   Score: {score:.3f} | Label: {label_id} ({label_str})")
            
        except KeyboardInterrupt:
            print("\nExiting...")
            break

def file_mode(estimator, input_path, output_path):
    """File processing mode"""
    print(f"[*] Processing file: {input_path}")
    
    if not os.path.exists(input_path):
        print(f"[!] Error: Input file not found.")
        return

    count = 0
    try:
        with open(input_path, 'r', encoding='utf-8', errors='ignore') as f_in, \
             open(output_path, 'w', encoding='utf-8') as f_out:
            
            # Write Header
            f_out.write("password strength_label\n")
            
            for line in f_in:
                parts = line.strip().split()
                if not parts: continue
                
                # Assume password is the last element in the line
                password = parts[-1] 
                
                score = estimator.calculate_score(password)
                label = estimator.get_label(score)
                
                f_out.write(f"{password} {label}\n")
                count += 1
                
                if count % 10000 == 0:
                    print(f"    Processed {count} passwords...", end='\r')
                    
        print(f"\n[+] Done. Processed {count} passwords.")
        print(f"[+] Results saved to: {output_path}")
        
    except Exception as e:
        print(f"\n[!] Error during processing: {e}")

def main():
    print(BANNER)
    parser = argparse.ArgumentParser(description="Evaluate password strength using trained SMML model")
    
    parser.add_argument("-m", "--model", required=True, help="Path to trained model file (.pkl)")
    parser.add_argument("-i", "--input", help="Path to input file containing passwords to evaluate")
    parser.add_argument("-o", "--output", default="evaluated_passwords.txt", help="Output file path (only for file mode)")
    
    args = parser.parse_args()

    # Load Model
    print(f"[*] Loading model from: {args.model} ...")
    estimator = SMMLEstimator.load_model(args.model)
    print(f"[*] Model loaded successfully.")
    print(f"    (Thresholds -> Normal: {estimator.thre_nor}, Strong: {estimator.thre_str})")

    if args.input:
        file_mode(estimator, args.input, args.output)
    else:
        interactive_mode(estimator)

if __name__ == "__main__":
    main()