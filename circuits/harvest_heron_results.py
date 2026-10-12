#!/usr/bin/env python3
"""
Harvest IBM Heron Hardware Execution Results
Polls and collects the 12 queued circuits executed on IBM Heron via BlueQubit (device="quantum").
Extracts raw bitstring counts, applies Tensor-Product Readout Error Mitigation (TREM),
reconstructs Berry holonomy γ(c), compares against CPU simulation, and generates publication plots.
"""

import time
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import bluequbit

API_TOKEN = "FIysMm29ifkmSQeBZcE2N3kPGBOLcMkj"
client = bluequbit.init(API_TOKEN)

JOBS = [
    {"label": "cal_0", "role": "cal", "target": "00", "job_id": "gG7ks4kRNtKALNQy"},
    {"label": "cal_1", "role": "cal", "target": "11", "job_id": "2mUMacOc6fVJOpNy"},
    {"label": "c_0.10_X", "role": "data", "c": 0.10, "axis": "X", "job_id": "lviidKdoRJ80dVea"},
    {"label": "c_0.10_Y", "role": "data", "c": 0.10, "axis": "Y", "job_id": "3UrLHni6W2spp9EJ"},
    {"label": "c_0.30_X", "role": "data", "c": 0.30, "axis": "X", "job_id": "3wCRxmDEx1xL4PfO"},
    {"label": "c_0.30_Y", "role": "data", "c": 0.30, "axis": "Y", "job_id": "P3VJm7TZzEedRN8f"},
    {"label": "c_0.50_X", "role": "data", "c": 0.50, "axis": "X", "job_id": "GvI7zyWUpi8yTk6L"},
    {"label": "c_0.50_Y", "role": "data", "c": 0.50, "axis": "Y", "job_id": "luVvNEo6IYVM3zTN"},
    {"label": "c_0.70_X", "role": "data", "c": 0.70, "axis": "X", "job_id": "miqbpU29JNKqxGDl"},
    {"label": "c_0.70_Y", "role": "data", "c": 0.70, "axis": "Y", "job_id": "CQ59bDJnGuPx35UN"},
    {"label": "c_0.85_X", "role": "data", "c": 0.85, "axis": "X", "job_id": "vCIfgekbGAjKjXxV"},
    {"label": "c_0.85_Y", "role": "data", "c": 0.85, "axis": "Y", "job_id": "Do4RYVjYQ4LVk0PE"},
]

def check_and_harvest(max_wait_seconds=600, poll_interval=15):
    print("=" * 80)
    print("🔬 DUONEURAL LAB — IBM HERON (156-QUBIT) PHYSICAL QPU HARVESTER")
    print("=" * 80)
    
    start_time = time.time()
    all_done = False
    
    while time.time() - start_time < max_wait_seconds:
        statuses = {}
        for item in JOBS:
            jid = item["job_id"]
            job = client.get(jid)
            statuses[jid] = job.run_status
            item["job_obj"] = job
            
        queued_count = sum(1 for s in statuses.values() if s == "QUEUED")
        running_count = sum(1 for s in statuses.values() if s == "RUNNING")
        completed_count = sum(1 for s in statuses.values() if s == "COMPLETED")
        failed_count = sum(1 for s in statuses.values() if s in ["FAILED", "CANCELLED"])
        
        elapsed = time.time() - start_time
        print(f"[{elapsed:5.1f}s] QPU Status: {completed_count}/12 Completed | {running_count} Running | {queued_count} Queued | {failed_count} Failed")
        
        if failed_count > 0:
            print("❌ At least one job failed!")
            for item in JOBS:
                if statuses[item["job_id"]] in ["FAILED", "CANCELLED"]:
                    print(f"   Failed job: {item['label']} ({item['job_id']}) - Error: {item['job_obj'].error_message}")
            return False
            
        if completed_count == 12:
            all_done = True
            break
            
        time.sleep(poll_interval)
        
    if not all_done:
        print(f"⏳ Polling timeout reached ({max_wait_seconds}s). Jobs still in queue.")
        return False

    print("\n" + "=" * 80)
    print("🎉 ALL 12 PHYSICAL CIRCUITS COMPLETED ON IBM HERON!")
    print("=" * 80)

    # 1. Extract Calibration & Readout Mitigation Parameters
    cal0_job = [j for j in JOBS if j["label"] == "cal_0"][0]["job_obj"]
    cal1_job = [j for j in JOBS if j["label"] == "cal_1"][0]["job_obj"]
    
    cal0_counts = cal0_job.get_counts()
    cal1_counts = cal1_job.get_counts()
    shots = cal0_job.shots
    
    print("\n--- READOUT CALIBRATION TELEMETRY ---")
    print(f"Shots per circuit: {shots}")
    print(f"cal_0 (|00>) raw bitstrings: {cal0_counts}")
    print(f"cal_1 (|11>) raw bitstrings: {cal1_counts}")
    
    # Readout error on ancilla qubit (qubit 0, rightmost bit or leftmost depending on qiskit ordering)
    # In Qiskit, bitstring format is 'c0' or 'q1 q0'. Let's verify bitstring keys.
    # Single classical bit was measured from ancilla qubit 0, so bitstrings are '0' and '1'.
    p_1_given_0 = cal0_counts.get("1", 0) / float(shots)  # false positive eta_0
    p_0_given_1 = cal1_counts.get("0", 0) / float(shots)  # false negative eta_1
    
    eta_0 = p_1_given_0
    eta_1 = p_0_given_1
    denom = max(1e-6, 1.0 - eta_0 - eta_1)
    
    print(f"Measured Readout Error Rates: η₀ = {eta_0:.5f} ({eta_0*100:.2f}%), η₁ = {eta_1:.5f} ({eta_1*100:.2f}%)")
    print(f"Readout Inversion Scale Factor: 1 - η₀ - η₁ = {denom:.5f}")

    # 2. Extract Observables for each curvature point
    c_points = [0.10, 0.30, 0.50, 0.70, 0.85]
    harvest_data = {
        "metadata": {
            "device": "ibm_heron (quantum)",
            "shots": shots,
            "eta_0": eta_0,
            "eta_1": eta_1,
            "cal0_counts": cal0_counts,
            "cal1_counts": cal1_counts,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%SZ", time.gmtime())
        },
        "curvature_sweeps": []
    }

    print("\n--- CURVATURE POINT HOLONOMY RECONSTRUCTION ---")
    for c in c_points:
        job_x = [j for j in JOBS if j.get("c") == c and j.get("axis") == "X"][0]["job_obj"]
        job_y = [j for j in JOBS if j.get("c") == c and j.get("axis") == "Y"][0]["job_obj"]
        
        cx = job_x.get_counts()
        cy = job_y.get_counts()
        
        # Raw probabilities P(0)
        p0_x_raw = cx.get("0", 0) / float(shots)
        p0_y_raw = cy.get("0", 0) / float(shots)
        
        exp_x_raw = 2.0 * p0_x_raw - 1.0
        exp_y_raw = 2.0 * p0_y_raw - 1.0
        
        # Mitigated probabilities P_mit(0)
        p0_x_mit = np.clip((p0_x_raw - eta_1) / denom, 0.0, 1.0)
        p0_y_mit = np.clip((p0_y_raw - eta_1) / denom, 0.0, 1.0)
        
        exp_x_mit = 2.0 * p0_x_mit - 1.0
        exp_y_mit = 2.0 * p0_y_mit - 1.0
        
        # Holonomy angle gamma and visibility
        gamma_raw = float(np.arctan2(exp_y_raw, exp_x_raw))
        gamma_mit = float(np.arctan2(exp_y_mit, exp_x_mit))
        vis_raw = float(np.sqrt(exp_x_raw**2 + exp_y_raw**2))
        vis_mit = float(np.sqrt(exp_x_mit**2 + exp_y_mit**2))
        
        # Theoretical holonomy gamma_theory(c) = -2 * arctan(sqrt(1 - c^2) / c) or phase accumulation
        # In our circuit: U_geom = RZ(2 * theta_geo), where theta_geo is set by the state parameter
        rec = {
            "c": c,
            "job_x_id": job_x.job_id,
            "job_y_id": job_y.job_id,
            "counts_x": cx,
            "counts_y": cy,
            "p0_x_raw": p0_x_raw,
            "p0_y_raw": p0_y_raw,
            "exp_x_raw": exp_x_raw,
            "exp_y_raw": exp_y_raw,
            "gamma_raw": gamma_raw,
            "vis_raw": vis_raw,
            "p0_x_mit": p0_x_mit,
            "p0_y_mit": p0_y_mit,
            "exp_x_mit": exp_x_mit,
            "exp_y_mit": exp_y_mit,
            "gamma_mit": gamma_mit,
            "vis_mit": vis_mit,
        }
        harvest_data["curvature_sweeps"].append(rec)
        print(f"c={c:.2f} | Raw: <X>={exp_x_raw:+.4f}, <Y>={exp_y_raw:+.4f}, γ={gamma_raw:+.4f} rad, V={vis_raw:.4f}")
        print(f"       Mit: <X>={exp_x_mit:+.4f}, <Y>={exp_y_mit:+.4f}, γ={gamma_mit:+.4f} rad, V={vis_mit:.4f}")

    # Save to file
    out_json = "/home/ai/duoneural/quantum/ramsey_hardware_results.json"
    with open(out_json, "w") as f:
        json.dump(harvest_data, f, indent=2)
    print(f"\n💾 Physical QPU results saved to: {out_json}")

    # 3. Load dryrun (CPU simulator) for comparison
    dryrun_json = "/home/ai/duoneural/quantum/ramsey_dryrun_results.json"
    with open(dryrun_json, "r") as f:
        dryrun_data = json.load(f)

    # Plot Comparison
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('#0d1117')
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_facecolor('#161b22')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
        ax.grid(True, linestyle='--', alpha=0.3, color='#8b949e')

    sim_c = [pt["c"] for pt in dryrun_data["curvature_sweeps"]]
    sim_gamma = [pt["gamma_measured_rad"] for pt in dryrun_data["curvature_sweeps"]]
    sim_vis = [pt["visibility"] for pt in dryrun_data["curvature_sweeps"]]
    sim_exp_x = [pt["exp_x_mit"] for pt in dryrun_data["curvature_sweeps"]]
    sim_exp_y = [pt["exp_y_mit"] for pt in dryrun_data["curvature_sweeps"]]

    qpu_c = [pt["c"] for pt in harvest_data["curvature_sweeps"]]
    qpu_gamma_raw = [pt["gamma_raw"] for pt in harvest_data["curvature_sweeps"]]
    qpu_gamma_mit = [pt["gamma_mit"] for pt in harvest_data["curvature_sweeps"]]
    qpu_vis_raw = [pt["vis_raw"] for pt in harvest_data["curvature_sweeps"]]
    qpu_vis_mit = [pt["vis_mit"] for pt in harvest_data["curvature_sweeps"]]
    qpu_exp_x_mit = [pt["exp_x_mit"] for pt in harvest_data["curvature_sweeps"]]
    qpu_exp_y_mit = [pt["exp_y_mit"] for pt in harvest_data["curvature_sweeps"]]

    # Panel 1: Holonomy Angle γ(c)
    ax1.plot(sim_c, sim_gamma, 'o--', color='#58a6ff', label='CPU Simulator (Exact)', linewidth=2)
    ax1.plot(qpu_c, qpu_gamma_raw, 's:', color='#f0883e', label='IBM Heron Raw', markersize=7)
    ax1.plot(qpu_c, qpu_gamma_mit, 'D-', color='#3fb950', label='IBM Heron Mitigated (TREM)', markersize=8, linewidth=2.5)
    ax1.set_title("Berry Holonomy γ(c) Reconstruction", color='white', fontsize=13, fontweight='bold')
    ax1.set_xlabel("Curvature / Velocity c", color='white')
    ax1.set_ylabel("Holonomy Angle γ (rad)", color='white')
    ax1.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white')

    # Panel 2: Visibility V(c)
    ax2.plot(sim_c, sim_vis, 'o--', color='#58a6ff', label='CPU Simulator (V ≈ 1)', linewidth=2)
    ax2.plot(qpu_c, qpu_vis_raw, 's:', color='#f0883e', label='IBM Heron Raw Visibility', markersize=7)
    ax2.plot(qpu_c, qpu_vis_mit, 'D-', color='#3fb950', label='IBM Heron TREM-Mitigated V', markersize=8, linewidth=2.5)
    ax2.set_title("Ramsey Fringe Visibility V(c) = √(<X>² + <Y>²)", color='white', fontsize=13, fontweight='bold')
    ax2.set_xlabel("Curvature / Velocity c", color='white')
    ax2.set_ylabel("Interference Visibility V", color='white')
    ax2.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white')

    # Panel 3: Tomographic Expectation Values <X> and <Y>
    ax3.plot(sim_c, sim_exp_x, 'o--', color='#79c0ff', label='Sim <X>', alpha=0.7)
    ax3.plot(sim_c, sim_exp_y, '^--', color='#d2a8ff', label='Sim <Y>', alpha=0.7)
    ax3.plot(qpu_c, qpu_exp_x_mit, 's-', color='#58a6ff', label='IBM Heron <X>_mit', markersize=7, linewidth=2)
    ax3.plot(qpu_c, qpu_exp_y_mit, 'd-', color='#bc8cff', label='IBM Heron <Y>_mit', markersize=7, linewidth=2)
    ax3.set_title("Tomographic Projections <X> and <Y>", color='white', fontsize=13, fontweight='bold')
    ax3.set_xlabel("Curvature / Velocity c", color='white')
    ax3.set_ylabel("Expectation Value", color='white')
    ax3.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white')

    # Panel 4: Discrepancy & Fidelity on Physical Hardware
    # Residual |gamma_mit - gamma_sim|
    interp_sim_gamma = np.interp(qpu_c, sim_c, sim_gamma)
    delta_gamma = np.abs(np.array(qpu_gamma_mit) - interp_sim_gamma)
    ax4.bar(qpu_c, delta_gamma, width=0.04, color='#f778ba', alpha=0.8, edgecolor='white', label='|γ_QPU - γ_Sim| Error')
    ax4.axhline(0.05, color='#e3b341', linestyle='--', label='High-Fidelity Threshold (50 mrad)')
    ax4.set_title("Holonomy Absolute Error |Δγ| (Physical vs Theory)", color='white', fontsize=13, fontweight='bold')
    ax4.set_xlabel("Curvature / Velocity c", color='white')
    ax4.set_ylabel("Angular Error (rad)", color='white')
    ax4.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white')

    plt.suptitle("IBM Heron (156-Qubit) Hardware Validation — Ancilla Ramsey Holonomy Protocol\nDuoNeural Lab (Jesse Caldwell, Aura ✨, Archon)", color='white', fontsize=15, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    out_plot = "/home/ai/duoneural/quantum/ramsey_hardware_comparison.png"
    plt.savefig(out_plot, dpi=300)
    print(f"📊 Publication plot saved to: {out_plot}")
    return True

if __name__ == "__main__":
    check_and_harvest(max_wait_seconds=14400, poll_interval=30)
