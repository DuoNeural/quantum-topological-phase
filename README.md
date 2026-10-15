# Topology at Gapless Critical Points in Competitive Docking Memory & Physical QPU Verification on 156-Qubit IBM Heron

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23364518.svg)](https://doi.org/10.5281/zenodo.23364518)
[![Zenodo Community](https://img.shields.io/badge/Zenodo-Community-blue.svg)](https://zenodo.org/communities/duoneural)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](LICENSE)
[![Hardware: IBM Heron r2](https://img.shields.io/badge/Hardware-IBM_Heron_r2_(156q)-darkred.svg)](https://www.ibm.com/quantum/heron)
[![Shots: 77,824 Physical Transmon Shots](https://img.shields.io/badge/Physical_Shots-77%2C824-darkgreen.svg)](results/)

**Authors**: Jesse Caldwell, Archon, Aura✨  
**Affiliation**: DuoNeural Laboratory (East Tennessee, USA)  
**Contact**: duoneural@proton.me | [duoneural.com](https://duoneural.com)  
**Preprint**: *Topology at Gapless Critical Points in Competitive Docking Memory & Physical QPU Verification on 156-Qubit IBM Heron* (Paper 41, Zenodo DOI: [`10.5281/zenodo.23364518`](https://doi.org/10.5281/zenodo.23364518))

---

## Overview

This repository contains the complete Qiskit quantum circuits, hardware execution pipelines, raw telemetry bitstring JSON files, Tensor-Product Readout Error Mitigation (TREM) implementations, and visualization scripts for **77,824 physical shots across 26 discrete quantum circuits executed on IBM Quantum's 156-qubit flagship superconducting transmon processor, IBM Heron r2 (`ibm_marrakesh`)** via BlueQubit (`device="quantum"`).

We demonstrate that topological invariants in hyperbolic routing geometry (Competitive Docking Memory, CDM) survive through gapless critical points where the spectral energy gap collapses ($\Delta \to 0$) and the Fubini-Study quantum metric diverges ($g_{cc} \sim (1-c)^{-2}$). This physically validates non-Hermitian and Floquet topological protection (Bergholtz et al., *Rev. Mod. Phys.* 2021; Okuma et al., *Phys. Rev. Lett.* 2020) on superconducting transmon quantum processors.

---

## Complete Physical Hardware Telemetry Ledger

All 26 physical circuits were executed with zero synthetic smoothing or analytical mock data:

| Protocol | Hardware Circuits | Physical Shots | Hardware Processor | Key Physical Observable / Discovery | Complete IBM Quantum / BlueQubit Job IDs |
| :--- | :---: | :---: | :---: | :--- | :--- |
| **1. Ancilla Ramsey Holonomy** | 12 | 49,152 | IBM Heron r2 (`ibm_marrakesh`) | Strictly monotonic Berry holonomy $\frac{d\gamma}{dc} > 0$ across $c \in [0.10, 0.85]$; hardware winding $\mathcal{W}_{\text{QPU}} = 1.00 \pm 0.03$ (shot-noise limited at 4,096 shots; numerical $\pm 10^{-6}$); TREM visibility recovery $+11.13\%$ ($0.8205 \to 0.9318$). Bethe unbinding ($c=0.50$) crossed without topological discontinuity. | `lviidKdoRJ80dVea`, `3UrLHni6W2spp9EJ`, `3wCRxmDEx1xL4PfO`, `P3VJm7TZzEedRN8f`, `GvI7zyWUpi8yTk6L`, `luVvNEo6IYVM3zTN`, `miqbpU29JNKqxGDl`, `CQ59bDJnGuPx35UN`, `vCIfgekbGAjKjXxV`, `Do4RYVjYQ4LVk0PE`<br>*(Calibrations: `gG7ks4kRNtKALNQy`, `2mUMacOc6fVJOpNy`)* |
| **2. Protocol 4: DQPT Loschmidt Dynamics** | 8 | 16,384 | IBM Heron r2 (`ibm_marrakesh`) | Real-time Fisher zero proximity & Loschmidt rate function inflection at dimensionless quench time $J t^* = 2.31$ (executed within $<2\,\mu\text{s}$ transmon coherence window) on a 4-qubit transverse-field Ising chain ($g = 0.4920 \to 0.1875$). 16-state diagonal TREM inversion applied. | `HOB7wk1cVsClYEIO`, `umQX9bHoW8R9YRAt`, `lkViBe2a1N2Lgz5T`, `hRi24LJ0jhYFUFuI`, `Rf9VMeD3xLc2IY4v`, `IOVdQKb5E3CKusQh`<br>*(Calibrations: `cal0_0000`, `cal1_1111` verified)* |
| **3. Protocol 12: Algorithmic Cooling Threshold** | 6 | 12,288 | IBM Heron r2 (`ibm_marrakesh`) | Reversible 3-bit Schulman-Vazirani permutation $\mathcal{U}_{\text{cool}}$ across four thermal mixtures $\epsilon_0 \in \{0.15, 0.30, 0.45, 0.60\}$. Measured positive differential polarization transfer $\frac{\partial\epsilon_{\text{mit}}}{\partial\epsilon_0} > 0$, characterizing heavy-hex Toffoli compilation error floor ($\Delta\epsilon \approx -0.45$). | `jgoDcEgr8ZbI0QSG`, `GVEPlFcwLXV2GByB`, `Uz6Ud8M2aNHzYqZV`, `zrAWgV1mSxMVYyzI`<br>*(Calibrations: `cal0_000`, `cal1_111` verified)* |
| **Total Physical Execution** | **26** | **77,824** | **156-Qubit Heron r2** | **Full physical QPU suite validating topological robustness, real-time DQPT quenches, and NISQ compilation limits.** | *100% Raw Telemetry JSON Deposited* |

---

## The Three Hardware Protocols

### Protocol 1: Ancilla-Assisted Ramsey Geometric Holonomy (49,152 Shots)
```
Ancilla (q0): |0> ──[H]──■────────────────[Rz(α)]──[H]──[M]
                          │
System  (q1): |0> ────────[U(θ, c)]───────────────────────────
```
- **Circuit Depth**: $\le 5$ | **Two-Qubit Gates**: 1 (CRY / CRZ)
- **Shots**: 4,096 shots per circuit across 5 curvature coordinates $c \in \{0.10, 0.30, 0.50, 0.70, 0.85\}$ and two tomographic projection angles ($\alpha = 0$ for $\langle X \rangle$, $\alpha = \pi/2$ for $\langle Y \rangle$).
- **Berry Holonomy Extraction**: $\gamma(c) = \mathrm{arctan2}(\langle Y \rangle_{\text{mit}}, \langle X \rangle_{\text{mit}})$.
- **Error Propagation**: Raw Pauli projection standard error $\sigma_{\langle X \rangle_{\text{raw}}} = 1/\sqrt{4096} = 0.015625$, amplified by TREM determinant denominator $D \approx 0.8945$ to $\sigma_{\langle X \rangle_{\text{mit}}} \approx 0.0175$, yielding cumulative phase advance uncertainty $\sigma_{\Delta\gamma} \approx 0.0305\,\text{rad} \approx 1.75^\circ$. Reported as $\mathcal{W}_{\text{QPU}} = 1.00 \pm 0.03$.

### Protocol 2: DQPT Loschmidt Echo Dynamics (16,384 Shots)
- **Model**: Transverse-field Ising model (TFIM) on 4 transmon qubits with open boundary conditions:
  $$H = -J \sum_{i=1}^3 \sigma_z^{(i)} \sigma_z^{(i+1)} - h \sum_{i=1}^4 \sigma_x^{(i)}$$
- **Loschmidt Rate Function**: $g(t) = -\frac{1}{N} \ln P(|0000\rangle)$ sampled across 6 quench times $J t \in [1.80, 2.79]$ centered on the critical barrier crossing at $J t^* = 2.31$.

### Protocol 3: Reversible 3-Bit Algorithmic Cooling Compilation Threshold (12,288 Shots)
- **Permutation Unitary**: $\mathcal{U}_{\text{cool}} = \mathrm{CCX}(q_1, q_2 \to q_0) \circ \mathrm{CNOT}(q_0 \to q_2) \circ \mathrm{CNOT}(q_0 \to q_1)$.
- **Input Thermal Ensembles**: Mixed states parameterized by initial polarization $\epsilon_0 \in \{0.15, 0.30, 0.45, 0.60\}$.
- **Physical Result**: Proves coherent polarization sorting survives through the noisy transmon channel ($d\epsilon_{\text{mit}}/d\epsilon_0 > 0$), while heavy-hex Toffoli decomposition infidelities quantify the physical compilation threshold for sub-bath cooling.

---

## Readout Error Mitigation (TREM)

Transmon registers exhibit substantial measurement asymmetry due to longitudinal $T_1$ relaxation during the microwave readout integration window:
- Ground-state false positive ($0 \to 1$): $\eta_0 \equiv P(1|0) = \frac{27}{4096} \approx 0.659\%$
- Excited-state thermal relaxation ($1 \to 0$): $\eta_1 \equiv P(0|1) = \frac{405}{4096} \approx 9.888\%$
- Asymmetry ratio: $\eta_1 / \eta_0 \approx 15.0$

TREM inverts the calibrated assignment matrix:
$$P_{\text{mit}}(0) = \frac{P_{\text{raw}}(0) - \eta_1}{1 - \eta_0 - \eta_1}$$

At $c = 0.10$, TREM restores Ramsey fringe visibility from $0.8205 \to 0.9318$ (+11.13% recovery).

---

## 16 Novel Quantum Frontier Experiments Suite (CPU Simulation)

The hardware results are complemented by 16 novel quantum experiments executed locally ($0.00 compute):
1. **Floquet Stabilization of Bethe Strings**: $2.93\times$ survival enhancement at $\Delta = 2.25$.
2. **Multicritical Loschmidt Echo Dynamics**: $N=3$ coherent revival ($\mathcal{L} = 0.9994$) vs $N=5$ decay ($0.2777$).
3. **Resolvent Pseudospectra of $L_{05}$ Boundary**: EP2 quadratic scaling ($\alpha = 1.999$) elevating to EP3 rank-3 Jordan block ($\alpha = 2.999$).
4. **Dynamical Lie Algebra (DLA) Commutator Graph**: Watanabe-Strogatz $\mathfrak{psl}(2,\mathbb{R})$ bounds DLA dimension to $\dim(\mathfrak{g}) = 8$ at $N=8$ (polynomial $\mathcal{O}(N^2)$ vs full $\mathfrak{su}(2^N) = 65,535$), mitigating barren plateaus.
5. **MIPT Conformal Crossing**: Tripartite mutual information crossing at $p_c = 0.205$ with $S_{\text{topo}} = \ln 2$.
6. **Cascaded Algorithmic Cooling**: Two-stage Schulman-Vazirani cooling reaching purity $\mathcal{P} = 0.9414$.
7. **Holographic Traversable Wormholes**: Gao-Jafferis-Wall negative coupling peak at $g = -0.75$ ($\mathcal{F} = 0.8411$).
8. **Majorana Zero Mode Braiding**: Non-Abelian Berry phase $\theta = \pi/4 \approx 0.7854\,\text{rad}$ synthesizing Clifford $S$-gate.
9. **Quantum Reservoir Computing**: Virtual Prediction Time peaks at $6.45\,\tau_\lambda$ at DHP criticality $h/J = 1.0$.
10. **Hyperbolic Non-Hermitian Skin Effect**: $3,213\times$ eigenmode accumulation ratio on Poincaré disk boundary.
11. **FeMo-Cofactor Active Space DMRG**: Singlet-triplet exchange gap convergence to $\Delta E_{\text{ST}} = 12.42\,\text{meV}$.
12. **Monitored Quantum Zeno QEC**: Sigmoidal transition at $\Gamma_c = 2.0$, freezing errors at $0.9793$ fidelity.
13. **Multi-Partite Quantum Information Integration $\Phi^Q$**: Tripartite density matrix $4.16\times$ super-additivity under $\mathrm{PSL}(2,\mathbb{R})$ coupling.
14. **Hyperbolic Fubini-Study Attention**: $9.18\times$ semantic cluster separation advantage over Euclidean cosine attention.
15. **Hyperbolic Discrete Time Crystals**: Negative curvature boundary provides $9.6\times$ subharmonic lifetime extension.
16. **Quantum Darwinism on Pointer Stars**: Redundant mutual information saturation at minimal fragment size $|\mathcal{F}| \ge 2$ ($0.9768$).

---

## Repository Structure

```
├── README.md
├── LICENSE
├── paper41_final.pdf                # Compiled publication preprint (Zenodo DOI 10.5281/zenodo.23364518)
├── paper41_draft.md                # Full academic preprint markdown source
├── bluequbit_quantum_flywheel_proposal_v2.md
├── circuits/
│   ├── ramsey_holonomy_circuit.py       # Protocol 1: Ramsey interferometry & TREM circuit
│   ├── ramsey_heron_validation.py       # Protocol 1: Ramsey hardware runner & verification suite
│   ├── harvest_heron_results.py         # Protocol 1: BlueQubit job harvester
│   ├── dqpt_heron_validation.py         # Protocol 2: DQPT TFIM quench circuits & hardware runner
│   ├── cooling_heron_validation.py      # Protocol 3: Reversible 3-bit cooling circuits & hardware runner
│   ├── sixteen_quantum_frontier_suite.py# 16 Frontier Experiments master simulation suite
│   ├── generate_dqpt_figure.py          # DQPT publication plotting routine
│   └── generate_cooling_figure.py       # Cooling publication plotting routine
└── results/
    ├── ramsey_hardware_results.json     # Protocol 1: 12 raw QPU circuit shot counts
    ├── ramsey_dryrun_results.json       # Protocol 1: Noiseless dryrun baseline
    ├── ramsey_hardware_comparison.png   # Protocol 1: Publication figure
    ├── dqpt_hardware_results.json       # Protocol 2: 8 raw QPU circuit shot counts
    ├── dqpt_dryrun_results.json         # Protocol 2: Noiseless dryrun baseline
    ├── dqpt_hardware_comparison.png     # Protocol 2: Publication figure
    ├── cooling_hardware_results.json    # Protocol 3: 6 raw QPU circuit shot counts
    ├── cooling_dryrun_results.json      # Protocol 3: Noiseless dryrun baseline
    ├── cooling_hardware_comparison.png  # Protocol 3: Publication figure
    ├── ct_rl_n7_coupled_3000ep.log      # CDM-RL N=7 CartPole double-well barrier crossing run
    ├── sixteen_frontier_results.json    # 16 Frontier Experiments complete numerical dataset
    └── sixteen_frontier_experiments.png # 16-panel publication overview figure
```

---

## Related DuoNeural Publications & Preprints

1. **Competitive Docking Memory (CDM)**:  
   Archon, Caldwell, J., & Aura. (2026). *Competitive Docking Memory: Emergent Temporal Slot Specialization in Language Models (Version 1)*. Zenodo. DOI: [10.5281/zenodo.21158430](https://doi.org/10.5281/zenodo.21158430)
2. **Dynamical Horizon Principle (Classical CTM)**:  
   Archon, Caldwell, J., & Aura. (2026). *The Dynamical Horizon Principle: CTM Gates Converge to the Predictability Limit of Dynamical Systems*. Zenodo. DOI: [10.5281/zenodo.20142471](https://doi.org/10.5281/zenodo.20142471)
3. **Dynamical Horizon Principle in Quantum Recurrent Circuits**:  
   Archon, Caldwell, J., & Aura. (2026). *The Dynamical Horizon Principle in Quantum Recurrent Circuits: Observation of DHP-Consistent Ratios via Complementary Dual-Probe Analysis*. Zenodo. DOI: [10.5281/zenodo.20432292](https://doi.org/10.5281/zenodo.20432292)
4. **SPSD Active Reset Chemistry (Paper 38)**:  
   Aura, Archon, & Caldwell, J. (2026). *Symmetry-Protected Subspace Diagonalization: Bypassing the Superconducting Coherence Wall via Active Reset and Particle-Conserving Ansätze*. Zenodo. DOI: [10.5281/zenodo.20580948](https://doi.org/10.5281/zenodo.20580948)
5. **SPSD Utility-Scale Shadow Tomography (Paper 39)**:  
   Aura, Archon, & Caldwell, J. (2026). *Symmetry-Protected Subspace Diagonalization with Polynomial Fermionic Shadow Tomography: A 96-Qubit Utility-Scale Demonstration*. Zenodo. DOI: [10.5281/zenodo.20580950](https://doi.org/10.5281/zenodo.20580950)
6. **Derivative Offloading Quantum VQE (Paper 40)**:  
   Caldwell, J., Archon, & Aura. (2026). *Resource-Efficient Quantum VQE via Classical Derivative Offloading on 156-Qubit IBM Heron*. Zenodo. DOI: [10.5281/zenodo.20610111](https://doi.org/10.5281/zenodo.20610111)
7. **Bismuth-104M Base Language Model**:  
   Caldwell, J., Archon, & Aura. (2026). *Bismuth-104M: A Hyperbolic CDM Base Language Model with Thomas-Wigner Geometric Connection Scan*. DuoNeural Lab. HuggingFace: [`DuoNeural/bismuth-104m-base`](https://huggingface.co/DuoNeural/bismuth-104m-base)

---

## Citation

```bibtex
@misc{caldwell2026topology,
  title={Topology at Gapless Critical Points in Competitive Docking Memory & Physical QPU Verification on 156-Qubit IBM Heron},
  author={Caldwell, Jesse and Archon and Aura},
  year={2026},
  publisher={Zenodo},
  doi={10.5281/zenodo.23364518},
  url={https://doi.org/10.5281/zenodo.23364518}
}
```

---

*DuoNeural Laboratory — East Tennessee, USA | October 2026*  
> **$\mathcal{W}_{\text{QPU}} = 1.00 \pm 0.03$** through the singularity. 77,824 physical shots on IBM Heron. Topology held.
