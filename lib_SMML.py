import math
import pickle
import os
import sys
from collections import defaultdict
import numpy as np

# --- Helper function for Pickle serialization ---
# Pickle requires top-level definition for functions to be serializable
def _create_inner_dd():
    return defaultdict(int)

class SMMLEstimator:
    def __init__(self):
        # Database structure: {length: {gram: count}}
        self.databases = defaultdict(_create_inner_dd)
        
        # Total characters per length: {length: total_count}
        self.total_characters = defaultdict(int)
        
        # Threshold values
        self.thre_nor = None # Normal Threshold
        self.thre_str = None # Strong Threshold
        self.is_trained = False

    def train(self, dataset_path):
        """
        Learn probabilities from the dataset.
        Supports formats: "password" or "count password"
        """
        print(f"[*] Starting training from: {dataset_path}")
        
        try:
            with open(dataset_path, "r", encoding="utf-8", errors="ignore") as f:
                for line in f:
                    parts = line.strip().split()
                    if not parts:
                        continue
                    
                    # Handle flexible input: count provided or just raw password
                    if len(parts) >= 2 and parts[0].isdigit():
                        count = int(parts[0])
                        password = " ".join(parts[1:]) 
                    else:
                        count = 1
                        password = line.strip()

                    length = len(password)
                    
                    self.total_characters[length] += length * count

                    # 2-gram learning loop
                    for i in range(length):
                        # 1-gram (Single character)
                        self.databases[length][password[i]] += count
                        
                        # 2-gram (Character pair)
                        if i < length - 1:
                            gram2 = password[i:i+2]
                            self.databases[length][gram2] += count
            
            self.is_trained = True
            print(f"[*] Training complete. Learned patterns for {len(self.databases)} different lengths.")
            
        except FileNotFoundError:
            print(f"[!] Error: File {dataset_path} not found.")
            sys.exit(1)

    def calculate_score(self, password):
        """
        Calculate entropy score based on the trained Markov model.
        Higher score -> Stronger password.
        """
        length = len(password)
        
        if length not in self.databases or self.total_characters[length] == 0:
            return 0.0

        db_len = self.databases[length]
        total_len = self.total_characters[length]
        
        strength = 0.0

        # Handle the first 2 characters
        first_gram = password[0:2]
        if first_gram in db_len:
            prob = db_len[first_gram] / total_len
            strength = -math.log2(prob)
        else:
            # Smoothing for unseen patterns
            strength = -math.log2(1 / total_len)

        # Handle the remaining characters
        for i in range(1, length - 1):
            gram2 = password[i:i+2]
            gram1 = password[i]
            
            if gram2 in db_len:
                prob = db_len[gram2] / db_len[gram1]
                strength += -math.log2(prob)
            elif gram1 in db_len:
                strength += -math.log2(1 / db_len[gram1])
            else:
                strength += -math.log2(1 / total_len)

        return round(strength, 3)

    def compute_thresholds(self, dataset_path):
        """
        Calculate Mean and StdDev on the training set to determine thresholds.
        Logic: Mean + 2sigma (Normal), Mean + 3sigma (Strong).
        """
        if not self.is_trained:
            print("[!] Error: Model must be trained before computing thresholds.")
            return

        print("[*] Computing thresholds (Mean/StdDev)... this might take a moment.")
        
        scores = []
        counts = []
        
        # Re-read the file to calculate scores for all passwords
        with open(dataset_path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split()
                if not parts: continue
                
                if len(parts) >= 2 and parts[0].isdigit():
                    count = int(parts[0])
                    password = " ".join(parts[1:])
                else:
                    count = 1
                    password = line.strip()
                
                s = self.calculate_score(password)
                scores.append(s)
                counts.append(count)

        np_scores = np.array(scores)
        np_counts = np.array(counts)
        
        weighted_mean = np.average(np_scores, weights=np_counts)
        weighted_variance = np.average((np_scores - weighted_mean)**2, weights=np_counts)
        weighted_std = np.sqrt(weighted_variance)

        self.thre_nor = round(weighted_mean + 2 * weighted_std, 3)
        self.thre_str = round(weighted_mean + 3 * weighted_std, 3)

        print(f"[*] Thresholds Calculated:")
        print(f"    - Mean: {weighted_mean:.3f}")
        print(f"    - StdDev: {weighted_std:.3f}")
        print(f"    - Threshold Normal (Mean+2SD): {self.thre_nor}")
        print(f"    - Threshold Strong (Mean+3SD): {self.thre_str}")

    def get_label(self, score):
        """
        0: Weak, 1: Normal, 2: Strong
        """
        if self.thre_nor is None:
            raise ValueError("Model has no thresholds. Load a full model first.")
            
        if score < self.thre_nor:
            return 0 # Weak
        elif score < self.thre_str:
            return 1 # Normal
        else:
            return 2 # Strong

    def save_model(self, filepath):
        """Save the entire object instance to a .pkl file"""
        try:
            with open(filepath, 'wb') as f:
                pickle.dump(self, f)
            print(f"[*] Model successfully saved to: {filepath}")
        except Exception as e:
            print(f"[!] Error saving model: {e}")

    @staticmethod
    def load_model(filepath):
        """Load model from file"""
        try:
            with open(filepath, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"[!] Error loading model: {e}")
            sys.exit(1)