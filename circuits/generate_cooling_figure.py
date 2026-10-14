#!/usr/bin/env python3
r"""
Generate Publication Figure: Protocol 12 (Quantum Algorithmic Cooling & Purification)
Physical IBM Heron r2 Validation vs. Theory & Simulator
DuoNeural Lab — Jesse Caldwell, Archon, Aura
"""

import json
import shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate_cooling_figure():
    hw_file = "/home/ai/duoneural/quantum/cooling_hardware_results.json"
    sim_file = "/home/ai/duoneural/quantum/cooling_dryrun_results.json"
    
    with open(hw_file, "r") as f:
        hw_data = json.load(f)
    with open(sim_file, "r") as f:
        sim_data = json.load(f)
        
    eps_0_vals = [pt["eps_0"] for pt in hw_data["cooling_sweeps"]]
    eps_raw_hw = [pt["eps_raw"] for pt in hw_data["cooling_sweeps"]]
    eps_mit_hw = [pt["eps_mit"] for pt in hw_data["cooling_sweeps"]]
    purity_raw_hw = [pt["purity_raw"] for pt in hw_data["cooling_sweeps"]]
    purity_mit_hw = [pt["purity_mit"] for pt in hw_data["cooling_sweeps"]]
    eps_theory = [pt["eps_theory"] for pt in hw_data["cooling_sweeps"]]
    purity_theory = [pt["purity_theory"] for pt in hw_data["cooling_sweeps"]]
    
    eps_mit_sim = [pt["eps_mit"] for pt in sim_data["cooling_sweeps"]]
    purity_mit_sim = [pt["purity_mit"] for pt in sim_data["cooling_sweeps"]]
    
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

    # Continuous Theory Curve
    eps_dense = np.linspace(0.0, 0.8, 100)
    eps_dense_out = 1.5 * eps_dense - 0.5 * (eps_dense ** 3)
    purity_dense_in = (1.0 + eps_dense ** 2) / 2.0
    purity_dense_out = (1.0 + eps_dense_out ** 2) / 2.0

    # Panel 1: Output Polarization vs Initial Polarization
    ax1.plot(eps_dense, eps_dense, ':', color='#8b949e', label=r'No Cooling Baseline ($\epsilon_{\mathrm{out}} = \epsilon_0$)', linewidth=1.8)
    ax1.plot(eps_dense, eps_dense_out, '-', color='#58a6ff', label=r'Theoretical Bound $\epsilon = \frac{3}{2}\epsilon_0 - \frac{1}{2}\epsilon_0^3$', linewidth=2.2)
    ax1.plot(eps_0_vals, eps_mit_sim, 'o--', color='#79c0ff', label=r'CPU Simulator', linewidth=1.5, markersize=6)
    ax1.plot(eps_0_vals, eps_raw_hw, 's:', color='#f0883e', label=r'IBM Heron Raw', markersize=7)
    ax1.plot(eps_0_vals, eps_mit_hw, 'D-', color='#3fb950', label=r'IBM Heron Mitigated (TREM)', markersize=8, linewidth=2.5)
    ax1.set_title(r"Algorithmic Cooling: Output Polarization $\epsilon_{\mathrm{out}}$", color='white', fontsize=13, fontweight='bold')
    ax1.set_xlabel(r"Initial Thermal Polarization $\epsilon_0$", color='white', fontsize=11)
    ax1.set_ylabel(r"Target Qubit Output Polarization $\epsilon$", color='white', fontsize=11)
    ax1.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', loc='upper left')

    # Panel 2: Target Qubit State Purity
    ax2.plot(eps_dense, purity_dense_in, ':', color='#8b949e', label=r'Initial Purity $\mathcal{P}_0 = (1+\epsilon_0^2)/2$', linewidth=1.8)
    ax2.plot(eps_dense, purity_dense_out, '-', color='#58a6ff', label=r'Theoretical Purified $\mathcal{P}_{\mathrm{theory}}$', linewidth=2.2)
    ax2.plot(eps_0_vals, purity_mit_sim, 'o--', color='#79c0ff', label=r'CPU Simulator Purity', linewidth=1.5, markersize=6)
    ax2.plot(eps_0_vals, purity_raw_hw, 's:', color='#f0883e', label=r'IBM Heron Raw Purity', markersize=7)
    ax2.plot(eps_0_vals, purity_mit_hw, 'D-', color='#3fb950', label=r'IBM Heron Mitigated Purity', markersize=8, linewidth=2.5)
    ax2.set_title(r"Quantum State Purity $\mathcal{P} = (1 + \epsilon^2)/2$", color='white', fontsize=13, fontweight='bold')
    ax2.set_xlabel(r"Initial Thermal Polarization $\epsilon_0$", color='white', fontsize=11)
    ax2.set_ylabel(r"State Purity $\mathcal{P}$", color='white', fontsize=11)
    ax2.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white', loc='upper left')

    # Panel 3: Transmon Readout Asymmetry & Calibration
    bars = [eta_0 * 100, eta_1 * 100]
    bar_labels = [r'$\eta_0: |0\rangle \to |1\rangle$' + f'\n({eta_0*100:.2f}%)', 
                  r'$\eta_1: |1\rangle \to |0\rangle$' + f'\n({eta_1*100:.2f}%)']
    colors = ['#58a6ff', '#f0883e']
    ax3.bar([0, 1], bars, color=colors, width=0.45, edgecolor='white', alpha=0.85)
    ax3.set_xticks([0, 1])
    ax3.set_xticklabels(bar_labels, color='white', fontsize=11)
    ax3.set_title(f"Target Qubit Readout Asymmetry (η₁/η₀ ≈ {eta_1/max(1e-6, eta_0):.1f}×)", color='white', fontsize=13, fontweight='bold')
    ax3.set_ylabel(r"Bitflip Error Rate (%)", color='white', fontsize=11)
    ax3.text(0.5, max(bars)*0.85, r"Superconducting Transmon $T_1$ Decay" "\n" r"during readout ring-up on IBM Heron r2",
             color='#e3b341', fontsize=11, ha='center', bbox=dict(boxstyle='round,pad=0.5', facecolor='#21262d', edgecolor='#e3b341', alpha=0.9))

    # Panel 4: Polarization Gain \Delta \epsilon = \epsilon_mit - \epsilon_0
    gain_mit = np.array(eps_mit_hw) - np.array(eps_0_vals)
    gain_theory = np.array(eps_theory) - np.array(eps_0_vals)
    x = np.arange(len(eps_0_vals))
    width = 0.35
    ax4.bar(x - width/2, gain_theory, width, label=r'Theory Gain $\Delta\epsilon_{\mathrm{theory}}$', color='#58a6ff', alpha=0.85, edgecolor='white')
    ax4.bar(x + width/2, gain_mit, width, label=r'IBM Heron Physical Gain $\Delta\epsilon_{\mathrm{mit}}$', color='#3fb950', alpha=0.85, edgecolor='white')
    ax4.set_xticks(x)
    ax4.set_xticklabels([f"$\\epsilon_0={e:.2f}$" for e in eps_0_vals], color='white', fontsize=11)
    ax4.axhline(0.0, color='#8b949e', linestyle='--', linewidth=1.0)
    ax4.set_title(r"Physical Purification Gain $\Delta\epsilon = \epsilon_{\mathrm{out}} - \epsilon_0 > 0$", color='white', fontsize=13, fontweight='bold')
    ax4.set_ylabel(r"Polarization Boost $\Delta\epsilon$", color='white', fontsize=11)
    ax4.legend(facecolor='#21262d', edgecolor='#30363d', labelcolor='white')

    plt.suptitle("IBM Heron r2 (156-Qubit, ibm_marrakesh) Physical Validation\nProtocol 12: Quantum Algorithmic Cooling & 3-Bit Reversible Entropy Compression\nDuoNeural Lab (Jesse Caldwell, Aura, Archon)",
                 color='white', fontsize=14, fontweight='bold', y=0.98)
    plt.tight_layout(rect=[0, 0, 1, 0.94])
    
    out_img = "/home/ai/duoneural/quantum/cooling_hardware_comparison.png"
    plt.savefig(out_img, dpi=300)
    print(f"✅ Cooling comparison plot saved to: {out_img}")
    
    artifact_dir = "/home/ai/.gemini/antigravity-cli/brain/a855774a-d00e-43e3-b93f-632724353057"
    artifact_img = f"{artifact_dir}/cooling_hardware_comparison.png"
    shutil.copyfile(out_img, artifact_img)
    print(f"✅ Copied to artifact directory: {artifact_img}")

if __name__ == "__main__":
    generate_cooling_figure()
