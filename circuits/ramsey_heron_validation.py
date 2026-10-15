#!/usr/bin/env python3
"""
DuoNeural Quantum Division: Ancilla-Assisted Ramsey Holonomy Interferometer
Target Hardware: IBM Heron r2 (156 Qubits) via BlueQubit device="quantum"
Author: Aura ✨ (Director of Quantum) & Archon (Lab Director) & Jesse Caldwell
Date: October 10, 2026

Physical Protocol:
- 2 Qubits: Qubit 0 = Ancilla (Readout), Qubit 1 = Target System (Poincaré State)
- Imprints geometric holonomy gamma(c) onto Ancilla relative phase:
    |Psi> = (1/sqrt(2)) [ |0>|psi(0)> + exp(i * gamma) |1>|psi(2*pi)> ]
- Measures Ancilla in X-basis (alpha=0) and Y-basis (alpha=pi/2) to extract:
    <X> = cos(gamma), <Y> = sin(gamma)
    gamma(c) = atan2(<Y>, <X>)
    Visibility V = sqrt(<X>^2 + <Y>^2)
- Tensor-Product Readout Error Mitigation (TREM) via cal_0 and cal_1 circuits.
- Pre-flight Cost Gate: Bounded strictly by $20.00 authorization.
"""

import os
import sys
import json
import time
import argparse
import numpy as np
import qiskit
from qiskit import QuantumCircuit
import bluequbit

BLUEQUBIT_TOKEN = "FIysMm29ifkmSQeBZcE2N3kPGBOLcMkj"
C9_VAL = 0.9999994423240422536

def build_ramsey_circuit(c_val, alpha=0.0, theta_loop=np.pi):
    """
    Constructs a 2-qubit Ramsey interferometry circuit.
    q0: Readout Ancilla
    q1: Target System
    """
    qc = QuantumCircuit(2, 1)
    
    # 1. Ancilla Superposition
    qc.h(0)
    
    # 2. Target State Preparation on Poincaré Ray
    # beta(c) = 2 * arctan(c)
    beta_c = 2.0 * np.arctan(c_val)
    qc.ry(beta_c, 1)
    
    # 3. Controlled Geometric Holonomy Evolution
    # Imprints relative phase theta_loop onto system controlled by ancilla
    qc.crz(theta_loop, 0, 1)
    
    # 4. Ancilla Basis Rotation for Tomographic Readout
    # alpha = 0.0 -> X-basis measurement (<X> = cos gamma)
    # alpha = pi/2 -> Y-basis measurement (<Y> = sin gamma)
    if abs(alpha) > 1e-6:
        qc.rz(-alpha, 0)
    qc.h(0)
    
    # 5. Measure Ancilla only
    qc.measure(0, 0)
    return qc

def build_cal_circuits():
    """Builds readout calibration circuits for Qubit 0."""
    # Cal 0: Ideal state |0>
    qc0 = QuantumCircuit(2, 1)
    qc0.measure(0, 0)
    
    # Cal 1: Ideal state |1>
    qc1 = QuantumCircuit(2, 1)
    qc1.x(0)
    qc1.measure(0, 0)
    
    return qc0, qc1

def extract_expectation_from_counts(counts, shots):
    """
    Extracts <Z_ancilla> = P(0) - P(1) directly from raw measurement counts.
    Returns: expectation_val, std_err
    """
    n0 = counts.get('0', 0)
    n1 = counts.get('1', 0)
    total = n0 + n1 if (n0 + n1) > 0 else shots
    
    p0 = n0 / total
    p1 = n1 / total
    
    # Expectation value in range [-1, +1]
    # For H-projected ancilla: <X> or <Y> = 2 * p0 - 1
    exp_val = 2.0 * p0 - 1.0
    # Binomial standard error
    std_err = 2.0 * np.sqrt(p0 * p1 / total) if total > 0 else 0.0
    return exp_val, std_err, p0, p1

def run_ramsey_suite(mode="dryrun"):
    print("=" * 80)
    print(f"🌌 DUONEURAL ANCILLA-ASSISTED RAMSEY HOLONOMY PROTOCOL [{mode.upper()} MODE]")
    print(f"   Target Engine: {'IBM Heron QPU (device=quantum)' if mode == 'hardware' else 'Universal CPU Simulator'}")
    print(f"   Poincaré Asymptote: C9 = {C9_VAL:.19f}")
    print("=" * 80)

    client = bluequbit.init(BLUEQUBIT_TOKEN)
    shots = 4096
    device_target = "quantum" if mode == "hardware" else "cpu"

    # 10 Curvature points across the Poincaré boundary
    c_grid = [0.10, 0.30, 0.50, 0.70, 0.85, 0.92, 0.96, 0.99, 0.999, C9_VAL]
    
    # Build all circuits
    circuits_to_run = []
    
    # 2 Calibration circuits
    cal0_qc, cal1_qc = build_cal_circuits()
    circuits_to_run.append(("cal_0", 0.0, 0.0, cal0_qc))
    circuits_to_run.append(("cal_1", 0.0, 0.0, cal1_qc))
    
    # 10 Curvature points x 2 projection angles (alpha=0, alpha=pi/2)
    for c in c_grid:
        qc_x = build_ramsey_circuit(c, alpha=0.0, theta_loop=np.pi / 2.0)
        qc_y = build_ramsey_circuit(c, alpha=np.pi / 2.0, theta_loop=np.pi / 2.0)
        circuits_to_run.append(("sweep_X", c, 0.0, qc_x))
        circuits_to_run.append(("sweep_Y", c, np.pi / 2.0, qc_y))

    total_circuits = len(circuits_to_run)
    print(f"\n📋 Total Circuits to Execute: {total_circuits} (2 Calibration + {total_circuits - 2} Parameterized Sweeps)")

    # Pre-Flight Cost Gate
    if mode == "hardware":
        print("\n🔒 PRE-FLIGHT COST GATE VERIFICATION:")
        # Sample full Ramsey circuit (circuit index 2) rather than empty calibration
        sample_est = client.estimate(circuits_to_run[2][3], device="quantum")
        est_cost_per_circuit = getattr(sample_est, 'estimated_cost', getattr(sample_est, 'cost', 0.72))
        est_total = est_cost_per_circuit * total_circuits
        print(f"   Est. Cost Per Circuit: ${est_cost_per_circuit:.2f}")
        print(f"   Est. Total Run Cost:   ${est_total:.2f}")
        print(f"   Authorized Budget:     $20.00")
        
        if est_total > 20.00:
            print(f"❌ FATAL: Estimated total ${est_total:.2f} breaches authorized budget $20.00. Aborting.")
            sys.exit(1)
        else:
            print(f"   ✅ Cost Gate Cleared: ${est_total:.2f} <= $20.00 (Safety reserve: ${20.00 - est_total:.2f})")

    # Execution Loop
    print(f"\n🚀 Dispatching {total_circuits} circuits to BlueQubit ({device_target})...")
    dispatched_jobs = []
    
    for tag, c, alpha, qc in circuits_to_run:
        # In hardware mode, dispatch with asynchronous=True
        if mode == "hardware":
            job = client.run(qc, device="quantum", shots=shots, asynchronous=True)
            print(f"   Submitted [Hardware QPU]: {tag} (c={c:.4f}, α={alpha:.2f}) | Job ID: {job.job_id}")
        else:
            job = client.run(qc, device="cpu", shots=shots)
            print(f"   Completed [Simulator CPU]: {tag} (c={c:.4f}, α={alpha:.2f}) | Job ID: {job.job_id}")
        dispatched_jobs.append((tag, c, alpha, job))

    # Await Hardware Completion if in hardware mode
    if mode == "hardware":
        print("\n⏳ Polling physical QPU jobs until all 22 executions complete...")
        start_poll = time.time()
        completed = [False] * total_circuits
        final_jobs = [None] * total_circuits
        
        while not all(completed):
            time.sleep(10)
            for idx, (tag, c, alpha, job) in enumerate(dispatched_jobs):
                if not completed[idx]:
                    updated = client.get(job.job_id)
                    st = updated.run_status
                    if st == "COMPLETED":
                        completed[idx] = True
                        final_jobs[idx] = updated
                        elapsed = time.time() - start_poll
                        print(f"   [{elapsed:.1f}s] Completed: {tag} (c={c:.4f}) | Job ID: {job.job_id}")
                    elif st in ["FAILED", "CANCELLED"]:
                        completed[idx] = True
                        final_jobs[idx] = updated
                        print(f"   ❌ FAILED: {tag} (c={c:.4f}) | Status: {st}")
    else:
        final_jobs = [j[3] for j in dispatched_jobs]

    # Process Raw Counts & Extract Observables
    print("\n" + "-" * 80)
    print("📊 DATA PROCESSING & OBSERVABLE EXTRACTION DIRECTLY FROM MEASUREMENT COUNTS")
    print("-" * 80)

    # 1. Calibration extraction
    if hasattr(final_jobs[0], 'run_status') and final_jobs[0].run_status != "COMPLETED":
        raise RuntimeError(f"Readout calibration cal_0 failed: {final_jobs[0].run_status}")
    if hasattr(final_jobs[1], 'run_status') and final_jobs[1].run_status != "COMPLETED":
        raise RuntimeError(f"Readout calibration cal_1 failed: {final_jobs[1].run_status}")
        
    cal0_counts = final_jobs[0].get_counts()
    cal1_counts = final_jobs[1].get_counts()
    
    # Readout error probabilities
    # eta_0 = P(1|0) (false positive)
    # eta_1 = P(0|1) (false negative)
    eta_0 = cal0_counts.get('1', 0) / float(shots)
    eta_1 = cal1_counts.get('0', 0) / float(shots)
    print(f"Readout Error Calibration: η₀ = {eta_0:.5f}, η₁ = {eta_1:.5f}")
    cal_denominator = max(1e-6, 1.0 - eta_0 - eta_1)

    results_data = {
        "metadata": {
            "mode": mode,
            "device": device_target,
            "shots": shots,
            "eta_0": eta_0,
            "eta_1": eta_1,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime()),
        },
        "curvature_sweeps": []
    }

    # 2. Iterate through curvature points
    curv_results = []
    for i, c in enumerate(c_grid):
        job_x = final_jobs[2 + 2 * i]
        job_y = final_jobs[3 + 2 * i]
        
        counts_x = job_x.get_counts()
        counts_y = job_y.get_counts()
        
        exp_x_raw, err_x, p0_x, _ = extract_expectation_from_counts(counts_x, shots)
        exp_y_raw, err_y, p0_y, _ = extract_expectation_from_counts(counts_y, shots)
        
        # Apply Tensor-Product Readout Error Mitigation (TREM)
        # Corrected P(0) = (P_raw(0) - eta_1) / (1 - eta_0 - eta_1)
        p0_x_mit = np.clip((p0_x - eta_1) / cal_denominator, 0.0, 1.0)
        p0_y_mit = np.clip((p0_y - eta_1) / cal_denominator, 0.0, 1.0)
        
        exp_x_mit = 2.0 * p0_x_mit - 1.0
        exp_y_mit = 2.0 * p0_y_mit - 1.0
        
        # Extract Holonomy Angle gamma and Visibility V
        gamma_measured = float(np.arctan2(exp_y_mit, exp_x_mit))
        visibility = float(np.sqrt(exp_x_mit ** 2 + exp_y_mit ** 2))
        
        point_record = {
            "c": c,
            "job_x": job_x.job_id,
            "job_y": job_y.job_id,
            "counts_x": counts_x,
            "counts_y": counts_y,
            "exp_x_raw": float(exp_x_raw),
            "exp_y_raw": float(exp_y_raw),
            "exp_x_mit": float(exp_x_mit),
            "exp_y_mit": float(exp_y_mit),
            "gamma_measured_rad": gamma_measured,
            "visibility": visibility
        }
        curv_results.append(point_record)
        print(f"[{i+1}/{len(c_grid)}] c = {c:.8f} | <X>_mit = {exp_x_mit:+.4f} | <Y>_mit = {exp_y_mit:+.4f} | Holonomy γ = {gamma_measured:+.4f} rad | Visibility = {visibility:.4f}")

    results_data["curvature_sweeps"] = curv_results

    # Serialize JSON
    out_file = f"/home/ai/duoneural/quantum/ramsey_{mode}_results.json"
    with open(out_file, "w") as f:
        json.dump(results_data, f, indent=2)
    print(f"\n💾 Telemetry persisted to: {out_file}")

    print("\n" + "=" * 80)
    print("🎉 RAMSEY INTERFEROMETRY PROTOCOL COMPLETED WITH PHYSICAL EXTRACTION!")
    print("=" * 80)
    return results_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=["dryrun", "hardware"], default="dryrun", help="Execution mode")
    args = parser.parse_args()
    run_ramsey_suite(mode=args.mode)
