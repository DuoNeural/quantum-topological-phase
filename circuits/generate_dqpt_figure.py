#!/usr/bin/env python3
r"""
Generate Publication Figure: Protocol 4 (DQPT Loschmidt Echo Cusps)
Physical IBM Heron r2 Validation vs. CPU Simulation
DuoNeural Lab — Jesse Caldwell, Archon, Aura ✨
"""

import json
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_figure():
    hw_file = "/home/ai/duoneural/quantum/dqpt_hardware_results.json"
    sim_file = "/home/ai/duoneural/quantum/dqpt_dryrun_results.json"
    
    with open(hw_file, "r") as f:
        hw_data = json.load(f)
    with open(sim_file, "r") as f:
        sim_data = json.load(f)
        
    t_hw = [pt["t"] for pt in hw_data["time_series"]]
    p_raw_hw = [pt["p_raw_0000"] for pt in hw_data["time_series"]]
    p_mit_hw = [pt["p_mit_0000"] for pt in hw_data["time_series"]]
    rate_raw_hw = [pt["rate_raw"] for pt in hw_data["time_series"]]
    rate_mit_hw = [pt["rate_mit"] for pt in hw_data["time_series"]]
    
    t_sim = [pt["t"] for pt in sim_data["time_series"]]
    p_sim = [pt["p_mit_0000"] for pt in sim_data["time_series"]]
    rate_sim = [pt["rate_mit"] for pt in sim_data["time_series"]]
    
    eta_0 = hw_data["metadata"]["eta_0"]
    eta_1 = hw_data["metadata"]["eta_1"]

    # Publication Dark-Mode Style
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(14, 10))
    fig.patch.set_facecolor('#0d1117')
    
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_facecolor('#161b22')
        ax.tick_params(colors='white')
        for spine in ax.spines.values():
            spine.set_color('#30363d')
        ax.grid(True, linestyle='--', alpha=0.3, color='#8b949e')

    # Panel 1: Loschmidt Return Probability L(t)
    ax1.plot(t_sim, p_sim, 'o--', color='#58a6ff', label=r'CPU Simulator (Exact)', linewidth=2, markersize=6)
    ax1.plot(t_hw, p_raw_hw, 's:', color='#f0883e', label=r'IBM Heron Raw ($N=4$)', markersize=7)
    ax1.plot(t_hw, p_mit_hw, 'D-', color='#3fb950', label=r'IBM Heron TREM-Mitigated', markersize=8, linewidth=2.5)
    ax1.axvline(2.31, color='#f778ba', linestyle=':', linewidth=1.8, label=r'Critical Cusp $t^* = 2.31\,\mathrm{s}$')
    ax1.set_title(r"Loschmidt Return Probability $\mathcal{L}(t) = P(|0000\rangle)$", color='white', fontsize=13, fontweight='bold')
    ax1.set_xlabel(r"Evolution Time $t$ (seconds)", color='white', fontsize=11)
    ax1.set_ylabel(r"Return Probability $\mathcal{L}(t)$", color='white', fontsize=11)
    ax1.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', loc='upper left')

    # Panel 2: Dynamical Rate Function g(t)
    ax2.plot(t_sim, rate_sim, 'o--', color='#58a6ff', label=r'CPU Simulator $g(t)$', linewidth=2, markersize=6)
    ax2.plot(t_hw, rate_raw_hw, 's:', color='#f0883e', label=r'IBM Heron Raw $g_{\mathrm{raw}}(t)$', markersize=7)
    ax2.plot(t_hw, rate_mit_hw, 'D-', color='#3fb950', label=r'IBM Heron Mitigated $g_{\mathrm{mit}}(t)$', markersize=8, linewidth=2.5)
    ax2.axvline(2.31, color='#f778ba', linestyle=':', linewidth=1.8, label=r'Critical Singular Cusp $t^*$')
    ax2.set_title(r"Dynamical Rate Function $g(t) = -\frac{1}{N}\ln \mathcal{L}(t)$", color='white', fontsize=13, fontweight='bold')
    ax2.set_xlabel(r"Evolution Time $t$ (seconds)", color='white', fontsize=11)
    ax2.set_ylabel(r"Rate Function $g(t)$", color='white', fontsize=11)
    ax2.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', loc='upper right')

    # Panel 3: Transmon Readout Asymmetry & Calibration Error
    bars = [eta_0 * 100, eta_1 * 100]
    bar_labels = [r'$\eta_0: |0\rangle \to |1\rangle$' + f'\n({eta_0*100:.2f}%)', 
                  r'$\eta_1: |1\rangle \to |0\rangle$' + f'\n({eta_1*100:.2f}%)']
    colors = ['#58a6ff', '#f0883e']
    ax3.bar([0, 1], bars, color=colors, width=0.45, edgecolor='white', alpha=0.85)
    ax3.set_xticks([0, 1])
    ax3.set_xticklabels(bar_labels, color='white', fontsize=11)
    ax3.set_title(r"Physical Readout Error Asymmetry ($\eta_1/\eta_0 \approx 3.98$)", color='white', fontsize=13, fontweight='bold')
    ax3.set_ylabel(r"Bitflip Error Rate (%)", color='white', fontsize=11)
    ax3.text(0.5, max(bars)*0.85, r"Physical Transmon $T_1$ Relaxation" "\n" r"dominates readout ring-up ($\eta_1 \gg \eta_0$)",
             color='#e3b341', fontsize=11, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#21262d', edgecolor='#e3b341', alpha=0.9))

    # Panel 4: Discrepancy & Fidelity on Physical Hardware
    delta_rate = np.abs(np.array(rate_mit_hw) - np.array(rate_sim))
    ax4.bar(t_hw, delta_rate, width=0.08, color='#bc8cff', alpha=0.85, edgecolor='white', label=r'$|g_{\mathrm{QPU}} - g_{\mathrm{Sim}}|$ Residual')
    ax4.axhline(0.05, color='#e3b341', linestyle='--', linewidth=1.5, label=r'Precision Bound ($\Delta g = 0.05$)')
    ax4.set_title(r"Physical QPU Rate Residual $|g_{\mathrm{mit}} - g_{\mathrm{sim}}|$", color='white', fontsize=13, fontweight='bold')
    ax4.set_xlabel(r"Evolution Time $t$ (seconds)", color='white', fontsize=11)
    ax4.set_ylabel(r"Rate Discrepancy", color='white', fontsize=11)
    ax4.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white')

    plt.suptitle("IBM Heron r2 (156-Qubit, ibm_marrakesh) Physical Validation\nProtocol 4: Dynamical Quantum Phase Transition (DQPT) Loschmidt Echo Cusps\nDuoNeural Lab (Jesse Caldwell, Aura, Archon)",
                 color='white', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    
    out_img = "/home/ai/duoneural/quantum/dqpt_hardware_comparison.png"
    plt.savefig(out_img, dpi=300)
    print(f"✅ DQPT comparison plot saved to: {out_img}")
    
    # Copy to artifact directory
    artifact_dir = "/home/ai/.gemini/antigravity-cli/brain/a855774a-d00e-43e3-b93f-632724353057"
    artifact_img = f"{artifact_dir}/dqpt_hardware_comparison.png"
    shutil.copyfile(out_img, artifact_img)
    print(f"✅ Copied to artifact directory: {artifact_img}")

if __name__ == "__main__":
    generate_figure()
