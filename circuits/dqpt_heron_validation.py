#!/usr/bin/env python3
r"""
Protocol 4: Dynamical Quantum Phase Transition (DQPT) Loschmidt Echo Cusps
Physical Execution & Validation on IBM Heron r2 (156 Qubits, ibm_marrakesh)
DuoNeural Lab — Jesse Caldwell, Archon, Aura ✨

Physical Mechanism:
Simulates non-equilibrium quench across the CT RL double-well barrier (c* = 0.128).
Initial state: Paramagnetic ground state |++++> = H^{\otimes 4}|0000> (Basin 1).
Quench Hamiltonian: Ferromagnetic TFIM H_f = -J \sum Z_i Z_{i+1} - h_f \sum X_i (Basin 2, J=1.0, h_f=0.40).
Trotterized evolution: U(t) approx [ e^{-i h_f dt \sum X_i} e^{-i J dt \sum Z_i Z_{i+1}} ]^m.
Readout: Invert state prep by applying H^{\otimes 4} prior to computational basis measurement.
Loschmidt Echo: L(t) = |<++++| U(t) |++++>|^2 = P(|0000>).
Rate function: g(t) = - (1/N) ln L(t).
"""

import os
import sys
import time
import json
import argparse
import numpy as np
import bluequbit
from qiskit import QuantumCircuit

API_TOKEN = "FIysMm29ifkmSQeBZcE2N3kPGBOLcMkj"
client = bluequbit.init(API_TOKEN)

def build_dqpt_circuit(t: float, n_qubits: int = 4, trotter_steps: int = 2, J: float = 1.0, h_f: float = 0.40) -> QuantumCircuit:
    """Constructs the Trotterized Loschmidt return circuit for TFIM quench."""
    qc = QuantumCircuit(n_qubits, n_qubits)
    dt = t / trotter_steps
    
    # 1. State preparation: |++++>
    for q in range(n_qubits):
        qc.h(q)
        
    # 2. Trotterized quench evolution U(t)
    for _ in range(trotter_steps):
        # ZZ interactions: e^{-i J dt Z_i Z_{i+1}}
        for i in range(n_qubits - 1):
            qc.cx(i, i + 1)
            qc.rz(2.0 * J * dt, i + 1)
            qc.cx(i, i + 1)
            
        # Transverse X field: e^{-i h_f dt X_i}
        for i in range(n_qubits):
            qc.rx(2.0 * h_f * dt, i)
            
    # 3. Invert state preparation: apply H^{\otimes 4}
    for q in range(n_qubits):
        qc.h(q)
        
    # 4. Measure all qubits in computational basis
    qc.measure(range(n_qubits), range(n_qubits))
    return qc

def build_calibration_circuits(n_qubits: int = 4):
    """Builds 4-qubit readout calibration circuits |0000> and |1111>."""
    # cal_0: all |0>
    qc0 = QuantumCircuit(n_qubits, n_qubits)
    qc0.measure(range(n_qubits), range(n_qubits))
    
    # cal_1: all |1>
    qc1 = QuantumCircuit(n_qubits, n_qubits)
    for q in range(n_qubits):
        qc1.x(q)
    qc1.measure(range(n_qubits), range(n_qubits))
    
    return qc0, qc1

def run_dqpt_suite(mode: str = "dryrun", shots: int = 2048, budget_cap: float = 15.00):
    print("=" * 80)
    print(f"🔬 DUONEURAL PROTOCOL 4: DQPT LOSCHMIDT CUSP VERIFICATION (Mode: {mode.upper()})")
    print(f"Target Hardware: IBM Heron r2 (156 Qubits) | Shots: {shots} | Cap: ${budget_cap:.2f}")
    print("=" * 80)
    
    device_target = "quantum" if mode == "hardware" else "cpu"
    n_qubits = 4
    # Time points centered across the critical cusps identified in Exp 4 (t* ~ 2.31s and 2.79s)
    t_grid = [1.80, 2.05, 2.25, 2.31, 2.45, 2.79]
    
    # Assemble circuits: 2 calibrations + 6 time points = 8 circuits total
    qc_cal0, qc_cal1 = build_calibration_circuits(n_qubits=n_qubits)
    circuits_to_run = [
        ("cal_0000", 0.0, qc_cal0),
        ("cal_1111", 0.0, qc_cal1),
    ]
    for t_val in t_grid:
        qc_t = build_dqpt_circuit(t=t_val, n_qubits=n_qubits, trotter_steps=2)
        circuits_to_run.append((f"dqpt_t_{t_val:.2f}", t_val, qc_t))
        
    total_circuits = len(circuits_to_run)
    print(f"Total Circuits to Execute: {total_circuits} (2 Readout Calibrations + {len(t_grid)} Time Steps)")
    
    # Pre-Flight Cost Verification Gate
    if mode == "hardware":
        print("\n🔒 PRE-FLIGHT COST GATE VERIFICATION:")
        sample_est = client.estimate(circuits_to_run[2][2], device="quantum")
        est_cost_per_circuit = getattr(sample_est, 'estimated_cost', getattr(sample_est, 'cost', 1.35))
        est_total = est_cost_per_circuit * total_circuits
        print(f"   Sample Circuit: {circuits_to_run[2][0]}")
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
    
    for tag, t_val, qc in circuits_to_run:
        if mode == "hardware":
            job = client.run(qc, device="quantum", shots=shots, asynchronous=True)
            print(f"   Submitted [IBM Heron]: {tag} (t={t_val:.2f}s) | Job ID: {job.job_id}")
        else:
            job = client.run(qc, device="cpu", shots=shots)
            print(f"   Completed [Simulator]: {tag} (t={t_val:.2f}s) | Job ID: {job.job_id}")
        dispatched_jobs.append((tag, t_val, job))

    # Await Completion if Hardware Mode
    if mode == "hardware":
        print("\n⏳ Polling physical IBM Heron QPU jobs until all 8 complete...")
        start_poll = time.time()
        completed = [False] * total_circuits
        final_jobs = [None] * total_circuits
        
        while not all(completed):
            time.sleep(15)
            for idx, (tag, t_val, job) in enumerate(dispatched_jobs):
                if not completed[idx]:
                    updated = client.get(job.job_id)
                    st = updated.run_status
                    if st == "COMPLETED":
                        completed[idx] = True
                        final_jobs[idx] = updated
                        elapsed = time.time() - start_poll
                        print(f"   [{elapsed:.1f}s] Completed: {tag} (t={t_val:.2f}s) | Job ID: {job.job_id}")
                    elif st in ["FAILED", "CANCELLED"]:
                        completed[idx] = True
                        final_jobs[idx] = updated
                        print(f"   ❌ FAILED: {tag} | Status: {st}")
    else:
        final_jobs = [j[2] for j in dispatched_jobs]

    # Process Raw Counts & Extract Observables
    print("\n" + "-" * 80)
    print("📊 DATA PROCESSING & DQPT OBSERVABLE EXTRACTION DIRECTLY FROM MEASUREMENT COUNTS")
    print("-" * 80)
    
    # 1. Readout Error Mitigation (TREM) on 4 qubits
    cal0_counts = final_jobs[0].get_counts()
    cal1_counts = final_jobs[1].get_counts()
    
    # Bitstrings in Qiskit are strings like '0000', '1111'
    # False positive eta_0: fraction of bits that flipped 0 -> 1 when prepared in 0000
    # False negative eta_1: fraction of bits that flipped 1 -> 0 when prepared in 1111
    # Average single-qubit marginal readout error:
    total_zeros_in_cal0 = sum(b.count('0') * count for b, count in cal0_counts.items())
    total_ones_in_cal0 = sum(b.count('1') * count for b, count in cal0_counts.items())
    total_bits_cal0 = total_zeros_in_cal0 + total_ones_in_cal0
    eta_0 = total_ones_in_cal0 / float(total_bits_cal0)
    
    total_zeros_in_cal1 = sum(b.count('0') * count for b, count in cal1_counts.items())
    total_ones_in_cal1 = sum(b.count('1') * count for b, count in cal1_counts.items())
    total_bits_cal1 = total_zeros_in_cal1 + total_ones_in_cal1
    eta_1 = total_zeros_in_cal1 / float(total_bits_cal1)
    
    print(f"Readout Calibration: Marginal η₀ = {eta_0:.5f} ({eta_0*100:.2f}%), Marginal η₁ = {eta_1:.5f} ({eta_1*100:.2f}%)")
    cal_denominator = max(1e-6, (1.0 - eta_0 - eta_1) ** n_qubits)

    results_data = {
        "metadata": {
            "protocol": "Protocol 4 (DQPT Cusps)",
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
        "time_series": []
    }

    # 2. Extract Loschmidt Return Probability L(t) = P(|0000>)
    for i, t_val in enumerate(t_grid):
        job_t = final_jobs[2 + i]
        counts_t = job_t.get_counts()
        
        # Target state is '0000'
        p_raw_0000 = counts_t.get("0000", counts_t.get("0", 0)) / float(shots)
        
        # 4-qubit Exact Tensor-Product Readout Error Mitigation (TREM)
        # M_inv row 0000 has weight (1 - eta_1)**(4 - k) * (-eta_1)**k for bitstring with k ones
        sum_weighted = sum(
            ((1.0 - eta_1) ** (n_qubits - b.count('1'))) * ((-eta_1) ** b.count('1')) * count
            for b, count in counts_t.items()
        )
        p_mit_0000 = np.clip(sum_weighted / (float(shots) * cal_denominator), 1e-6, 1.0)
        
        # Dynamical Rate Function g(t) = - (1/N) ln L(t)
        rate_raw = float(- (1.0 / n_qubits) * np.log(max(1e-6, p_raw_0000)))
        rate_mit = float(- (1.0 / n_qubits) * np.log(p_mit_0000))
        
        record = {
            "t": t_val,
            "job_id": job_t.job_id,
            "counts": counts_t,
            "p_raw_0000": float(p_raw_0000),
            "p_mit_0000": float(p_mit_0000),
            "rate_raw": rate_raw,
            "rate_mit": rate_mit
        }
        results_data["time_series"].append(record)
        print(f"[{i+1}/{len(t_grid)}] t = {t_val:.2f}s | L_raw = {p_raw_0000:.5f} | L_mit = {p_mit_0000:.5f} | Rate g(t) = {rate_mit:.4f}")

    # Serialize JSON
    out_file = f"/home/ai/duoneural/quantum/dqpt_{mode}_results.json"
    with open(out_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\n💾 Results persisted to: {out_file}")
    return results_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dryrun", "hardware"], default="dryrun")
    parser.add_argument("--shots", type=int, default=2048)
    parser.add_argument("--cap", type=float, default=15.00)
    args = parser.parse_args()
    run_dqpt_suite(mode=args.mode, shots=args.shots, budget_cap=args.cap)
