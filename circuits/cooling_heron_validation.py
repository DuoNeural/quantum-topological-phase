#!/usr/bin/env python3
r"""
Protocol 12: Quantum Algorithmic Cooling & 3-Bit Entropy Compression
Physical Execution & Validation on IBM Heron r2 (156 Qubits, ibm_marrakesh)
DuoNeural Lab — Jesse Caldwell, Archon, Aura ✨

Physical Mechanism:
Implements reversible Schulman-Vazirani entropy compression on a 3-qubit register.
Target qubit q0 is initialized with tunable thermal polarization \epsilon_0 along with ancillae q1, q2.
Compression unitary: CNOT(q0, q1) -> CNOT(q1, q2) -> CCX(q1, q2, q0).
Theoretical output polarization: \epsilon_out = 1.5 * \epsilon_0 - 0.5 * \epsilon_0^3.
State purity: P = (1 + \epsilon_out^2) / 2.
"""

import sys
import time
import json
import argparse
import numpy as np
import bluequbit
from qiskit import QuantumCircuit

API_TOKEN = "FIysMm29ifkmSQeBZcE2N3kPGBOLcMkj"
client = bluequbit.init(API_TOKEN)

def build_cooling_circuit(eps_0: float, n_qubits: int = 3) -> QuantumCircuit:
    """Constructs 3-bit Schulman-Vazirani cooling circuit for initial polarization eps_0."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    # theta = 2 * arcsin(sqrt((1 - eps_0) / 2)) sets P(0) = (1 + eps_0)/2, P(1) = (1 - eps_0)/2
    theta = 2.0 * np.arcsin(np.sqrt((1.0 - eps_0) / 2.0))
    
    # 1. State preparation: prepare thermal mixed ensemble polarization
    for q in range(n_qubits):
        qc.ry(theta, q)
        
    # 2. Reversible Entropy Compression (SV 3-bit sort)
    qc.cx(0, 1)
    qc.cx(0, 2)  # Fixed: must compare qubit 2 against target qubit 0
    qc.ccx(1, 2, 0)
    
    # 3. Measurement
    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def build_cooling_calibration_circuits(n_qubits: int = 3):
    """Builds 3-qubit readout calibration circuits |000> and |111>."""
    qc0 = QuantumCircuit(n_qubits, n_qubits)
    qc0.measure(range(n_qubits), range(n_qubits))
    
    qc1 = QuantumCircuit(n_qubits, n_qubits)
    for q in range(n_qubits):
        qc1.x(q)
    qc1.measure(range(n_qubits), range(n_qubits))
    
    return qc0, qc1

def run_cooling_suite(mode: str = "dryrun", shots: int = 2048, budget_cap: float = 12.00):
    print("=" * 80)
    print(f"🔬 DUONEURAL PROTOCOL 12: ALGORITHMIC COOLING & PURIFICATION (Mode: {mode.upper()})")
    print(f"Target Hardware: IBM Heron r2 (156 Qubits) | Shots: {shots} | Cap: ${budget_cap:.2f}")
    print("=" * 80)
    
    device_target = "quantum" if mode == "hardware" else "cpu"
    n_qubits = 3
    eps_grid = [0.15, 0.30, 0.45, 0.60]
    
    qc_cal0, qc_cal1 = build_cooling_calibration_circuits(n_qubits=n_qubits)
    circuits_to_run = [
        ("cal_000", 0.0, qc_cal0),
        ("cal_111", 0.0, qc_cal1),
    ]
    for eps in eps_grid:
        qc_eps = build_cooling_circuit(eps_0=eps, n_qubits=n_qubits)
        circuits_to_run.append((f"cool_eps_{eps:.2f}", eps, qc_eps))
        
    total_circuits = len(circuits_to_run)
    print(f"Total Circuits to Execute: {total_circuits} (2 Readout Calibrations + {len(eps_grid)} Polarization Levels)")
    
    # Pre-Flight Cost Verification Gate
    if mode == "hardware":
        print("\n🔒 PRE-FLIGHT COST GATE VERIFICATION:")
        sample_est = client.estimate(circuits_to_run[2][2], device="quantum")
        est_cost_per_circuit = getattr(sample_est, 'estimated_cost', getattr(sample_est, 'cost', 1.35))
        est_total = est_cost_per_circuit * total_circuits
        print(f"   Est. Cost Per Circuit: ${est_cost_per_circuit:.2f}")
        print(f"   Est. Total Run Cost:   ${est_total:.2f}")
        print(f"   Authorized Budget Cap: ${budget_cap:.2f}")
        
        if est_total > budget_cap:
            print(f"❌ FATAL: Estimated total ${est_total:.2f} breaches budget cap ${budget_cap:.2f}. Aborting.")
            sys.exit(1)
        else:
            print(f"   ✅ Cost Gate Cleared: ${est_total:.2f} <= ${budget_cap:.2f} (Reserve: ${budget_cap - est_total:.2f})")

    # Execution Loop
    print(f"\n🚀 Dispatching {total_circuits} circuits to BlueQubit ({device_target})...")
    dispatched_jobs = []
    
    for tag, eps, qc in circuits_to_run:
        if mode == "hardware":
            job = client.run(qc, device="quantum", shots=shots, asynchronous=True)
            print(f"   Submitted [IBM Heron]: {tag} (ε₀={eps:.2f}) | Job ID: {job.job_id}")
        else:
            job = client.run(qc, device="cpu", shots=shots)
            print(f"   Completed [Simulator]: {tag} (ε₀={eps:.2f}) | Job ID: {job.job_id}")
        dispatched_jobs.append((tag, eps, job))

    # Await Completion if Hardware Mode
    if mode == "hardware":
        print("\n⏳ Polling physical IBM Heron QPU jobs until all 6 complete...")
        start_poll = time.time()
        completed = [False] * total_circuits
        final_jobs = [None] * total_circuits
        
        while not all(completed):
            time.sleep(15)
            for idx, (tag, eps, job) in enumerate(dispatched_jobs):
                if not completed[idx]:
                    updated = client.get(job.job_id)
                    st = updated.run_status
                    if st == "COMPLETED":
                        completed[idx] = True
                        final_jobs[idx] = updated
                        elapsed = time.time() - start_poll
                        print(f"   [{elapsed:.1f}s] Completed: {tag} (ε₀={eps:.2f}) | Job ID: {job.job_id}")
                    elif st in ["FAILED", "CANCELLED"]:
                        completed[idx] = True
                        final_jobs[idx] = updated
                        print(f"   ❌ FAILED: {tag} | Status: {st}")
    else:
        final_jobs = [j[2] for j in dispatched_jobs]

    # Process Raw Counts & Extract Observables
    print("\n" + "-" * 80)
    print("📊 DATA PROCESSING & ALGORITHMIC COOLING OBSERVABLE EXTRACTION")
    print("-" * 80)
    
    cal0_counts = final_jobs[0].get_counts()
    cal1_counts = final_jobs[1].get_counts()
    
    # Target qubit q0 marginal calibration:
    # In Qiskit bitstring 'q2 q1 q0', target qubit q0 is the rightmost bit (-1)
    zeros_q0_cal0 = sum(count for b, count in cal0_counts.items() if b[-1] == '0')
    ones_q0_cal0 = sum(count for b, count in cal0_counts.items() if b[-1] == '1')
    eta_0 = ones_q0_cal0 / float(zeros_q0_cal0 + ones_q0_cal0)
    
    zeros_q0_cal1 = sum(count for b, count in cal1_counts.items() if b[-1] == '0')
    ones_q0_cal1 = sum(count for b, count in cal1_counts.items() if b[-1] == '1')
    eta_1 = zeros_q0_cal1 / float(zeros_q0_cal1 + ones_q0_cal1)
    
    print(f"Target Qubit q₀ Readout Calibration: η₀ = {eta_0:.5f} ({eta_0*100:.2f}%), η₁ = {eta_1:.5f} ({eta_1*100:.2f}%)")
    cal_denom = max(1e-6, 1.0 - eta_0 - eta_1)

    results_data = {
        "metadata": {
            "protocol": "Protocol 12 (Algorithmic Cooling)",
            "mode": mode,
            "device": device_target,
            "shots": shots,
            "n_qubits": n_qubits,
            "eta_0": float(eta_0),
            "eta_1": float(eta_1),
            "cal0_counts": cal0_counts,
            "cal1_counts": cal1_counts,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        },
        "cooling_sweeps": []
    }

    for i, eps in enumerate(eps_grid):
        job_eps = final_jobs[2 + i]
        counts_eps = job_eps.get_counts()
        
        # Marginal probability of target qubit q0 being in |0>
        zeros_q0 = sum(count for b, count in counts_eps.items() if b[-1] == '0')
        p0_raw = zeros_q0 / float(shots)
        p0_mit = np.clip((p0_raw - eta_1) / cal_denom, 0.0, 1.0)
        
        eps_raw = 2.0 * p0_raw - 1.0
        eps_mit = 2.0 * p0_mit - 1.0
        
        # Purity P = (1 + eps^2) / 2
        purity_raw = (1.0 + eps_raw**2) / 2.0
        purity_mit = (1.0 + eps_mit**2) / 2.0
        
        eps_theory = 1.5 * eps - 0.5 * (eps ** 3)
        purity_theory = (1.0 + eps_theory**2) / 2.0
        
        record = {
            "eps_0": eps,
            "job_id": job_eps.job_id,
            "counts": counts_eps,
            "p0_raw": float(p0_raw),
            "p0_mit": float(p0_mit),
            "eps_raw": float(eps_raw),
            "eps_mit": float(eps_mit),
            "purity_raw": float(purity_raw),
            "purity_mit": float(purity_mit),
            "eps_theory": float(eps_theory),
            "purity_theory": float(purity_theory)
        }
        results_data["cooling_sweeps"].append(record)
        print(f"[{i+1}/{len(eps_grid)}] Initial ε₀ = {eps:.2f} | ε_mit = {eps_mit:.4f} (Theory: {eps_theory:.4f}) | Purity = {purity_mit:.4f} (Theory: {purity_theory:.4f})")

    out_file = f"/home/ai/duoneural/quantum/cooling_{mode}_results.json"
    with open(out_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\n💾 Results persisted to: {out_file}")
    return results_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dryrun", "hardware"], default="dryrun")
    parser.add_argument("--shots", type=int, default=2048)
    parser.add_argument("--cap", type=float, default=12.00)
    args = parser.parse_args()
    run_cooling_suite(mode=args.mode, shots=args.shots, budget_cap=args.cap)
