"""
Script to generate realistic VLA bimanual action chunk sequences,
including baseline divergence patterns documented in Hugging Face LeRobot Issue #3154.
"""

import json
import numpy as np

def generate_fixtures():
    np.random.seed(42)
    chunks = []
    
    # Base nominal joint velocities for a synchronized table-setting motion
    # Arm 1: [pan, shoulder, elbow, wrist_p, wrist_r, grip]
    # Arm 2: [pan, shoulder, elbow, wrist_p, wrist_r, grip]
    base_v = np.array([0.05, 0.08, -0.04, 0.02, 0.0, 0.0,
                      -0.05, 0.08, -0.04, 0.02, 0.0, 0.0])
    
    for i in range(150):
        # Add random neural approximation jitter (Tier C condition)
        noise = np.random.normal(0, 0.01, 12)
        v = base_v + noise
        
        # Inject asymmetric drift after step 30 (simulating LeRobot #3154 failure mode)
        if i >= 30:
            # Arm 1 pulls right (+x), Arm 2 stays or lags
            v[0] += 0.09 * np.sin((i - 30) / 10.0)
            v[1] += 0.06 * np.cos((i - 30) / 8.0)
            v[6] -= 0.07 * np.sin((i - 30) / 10.0)
            
        chunks.append({
            "chunk_id": i + 1,
            "q_dot": v.tolist(),
            "confidence": float(np.clip(0.95 - 0.001 * i, 0.80, 0.99))
        })
        
    with open(r"C:\Users\HP LAPTOP\.gemini\antigravity\scratch\kinlock\fixtures\sample_vla_chunks.json", "w") as f:
        json.dump(chunks, f, indent=2)
    print("Generated 150 VLA action chunks.")

if __name__ == "__main__":
    generate_fixtures()
