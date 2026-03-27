# FMCW Radar — Baseband Signal Conditioning & Digital Backend

A personal engineering portfolio project redesigning the baseband signal conditioning path for a 5.8 GHz FMCW radar system. Originally built as a senior capstone project at Texas Tech University (Spring 2020), now being redesigned from scratch with professional engineering discipline informed by 4+ years of hardware validation experience at Texas Instruments.

## Project Overview

This project demonstrates mixed-signal PCB design, digital hardware design, hardware verification, and system-level engineering through the complete redesign of an FMCW radar baseband — from schematic capture through layout, with first-principles documentation explaining every design decision.

### The System

An FMCW (Frequency-Modulated Continuous Wave) radar transmits a frequency chirp, receives the reflection from a target, and mixes it with the current transmit frequency to produce a low-frequency beat signal whose frequency is proportional to target range. The **baseband** conditions this beat signal for digitization:

```
RF Mixer → SMA Input → ESD Protection → PGA (1–200×) → Anti-Alias Filter → FDA → 18-bit ADC → SPI → FPGA/MCU
           └─────────── Sheet B ──────┘  └── Sheet C ──┘                   └──── Sheet D ────┘
                                         └──────────────── Sheet A (Power + References) ──────────────────┘
```

### Rev A → Rev B: What Changed and Why

| Aspect | Rev A (2020) | Rev B (2025–26) |
|--------|-------------|-----------------|
| Scope | 3 RX channels, 182 components | 1 RX channel (building block), 90 components |
| EDA | Eagle 9.5, flat single sheet | KiCad 9, 4-sheet hierarchy |
| VGA | LT6230 + MCP4017 I²C digital pot | PGA113 (SPI, internal gain resistors) |
| ADC | ADS1174 (16-bit, 64-pin QFP — solder bridges) | ADS8881 (18-bit, 10-pin VSSOP) |
| SE→Diff | LTC6242 (improvised, no VOCM) | THS4531A (true FDA with VOCM pin) |
| Power | Single 3.3V rail | 3V3A/3V3D split via ferrite bead |
| Reference | Resistor divider | REF5025 (2.500V, 0.05%, 3 µVpp) |
| DFT | None | J_DFT header, 17 TPs, 5 MMCX, 6 isolation resistors |
| ERC | Never run | 0 errors, 0 warnings |

## Repository Structure

```
├── hardware/
│   ├── baseband-revB/          # Current design (KiCad 9)
│   │   ├── kicad/              # Schematic and PCB files
│   │   └── docs/               # Rev B specific documentation
│   └── baseband-revA/          # Original design (Eagle 9.5) for reference
│       └── eagle/              # Original schematic and board files
│
├── digital/
│   └── spi-controller/         # SystemVerilog SPI master for ADS8881/PGA113
│       ├── rtl/                # RTL source
│       ├── tb/                 # Testbenches
│       └── sim/                # Simulation scripts and results
│
└── docs/
    ├── system-design/          # System design document (the "why" for every decision)
    ├── block-diagrams/         # System and sheet-level block diagrams
    ├── analysis/               # Filter analysis, schematic review
    ├── specifications/         # Sheet specifications, IC pin wiring guides
    └── images/                 # Photos, screenshots
```

### Related Repositories

This project is one track of a broader engineering portfolio spanning processor architecture, modular instrumentation, and mixed-signal hardware design. Related repositories:

| Repository | Description | Status |
|-----------|-------------|--------|
| [32-bit RISC Pipelined Processor](https://github.com/Pike1950/BradW_ECE4375_RISC_Pipeline) | 4-stage pipelined CPU refactored from Verilog to SystemVerilog. Data forwarding, hazard detection, 25 opcodes, signed multiply program. Tang Primer 25K (Gowin GW5A) is in hand; FPGA synthesis phase requires clock edge standardization, BSRAM memory fitting, and PLL clock generation. | SV conversion complete (14/14 CRs done), synthesis next |
| *scpi-instrument-platform* (planned) | Modular SCPI-compliant test instrument platform. Pi 5 orchestration, Pico 2 W measurement modules (DIO, voltage, SMU-lite), FPGA modules on Tang Primer 25K (logic analyzer, protocol exerciser, frequency counter). PyVISA + USB-TMC automation. | Architecture defined |

## Key Documents

| Document | Description |
|----------|-------------|
| [System Design Document](https://pike1950.github.io/fmcw-radar-portfolio/docs/system-design/System_Design_Document.html) | First-principles system design document covering all four sheets. FMCW operating principles (§1) with three-band beat frequency comparison, adaptive chirp modes, FCC regulatory landscape, and ISM band upgrade path. System overview (§2). Sheet A power (§3): LDO, ferrite bead, voltage reference, VCM buffer. Sheet B input (§4): ESD protection, AC coupling, DC bias. Sheet C gain+filter (§5): PGA113 variable gain, 4th-order Sallen-Key Butterworth with Q derivation. Sheet D digitization (§6): FDA SE→Diff, ADS8881 18-bit SAR, J_DFT header with isolation. |
| [Block Diagrams](https://pike1950.github.io/fmcw-radar-portfolio/docs/block-diagrams/RevB_Block_Diagrams.html) | Pin tables, signal maps, DFT reference, inter-sheet signal summary, hierarchical label directions. The "what" companion to the Design Rationale's "why." |
| [Schematic Review](https://pike1950.github.io/fmcw-radar-portfolio/docs/analysis/SchematicReview.html) | Systematic review of all four schematic sheets. |
| [Filter Analysis](https://pike1950.github.io/fmcw-radar-portfolio/docs/analysis/SheetC_Filter_Analysis.html) | Sheet C anti-alias filter analysis with transfer function derivation. |

## Technical Highlights

### Analog Design
- **Supply splitting via ferrite bead** — BLM18PG221SN1D (220Ω @ 100MHz) isolates analog from digital supply noise. Single ground plane with partitioned routing (no ground splits). First-principles impedance analysis in the design rationale.
- **Paired decoupling capacitors** — Every supply and reference node uses matched cap pairs (e.g., 10µF + 100nF) with different self-resonant frequencies to provide low impedance across a wide frequency range.
- **DFT-first methodology** — 17 test points, 5 MMCX probe connectors (DNP), 6× 10kΩ isolation resistors, and a 2×10 DFT header were designed before the signal chain, not as an afterthought.

### System-Level Analysis
- **Chirp rate correction** — Identified a fundamental parameter mismatch in Rev A: the 10 kHz chirp rate yielded only 5 ADC samples per ramp at 100 kSPS — insufficient for FFT-based range extraction. Rev B specifies ~100 Hz chirp rate (500 samples/ramp, 512-point FFT). Derived from first principles with sample-count-per-ramp analysis.
- **ISM band upgrade path** — Documented a firmware-only upgrade from 30 MHz / 75 mW (FCC §15.245) to 125 MHz / 1W (FCC §15.247 ISM), improving range resolution from 5.0 m to 1.2 m with zero baseband hardware changes. Full system impact assessment showing every subsystem's change status.
- **FCC regulatory landscape** — Comparative analysis of five unlicensed radar bands (§15.245, §15.247 ISM, UWB 3.1–10.6 GHz, 60 GHz, 76–81 GHz automotive) with bandwidth, power limits, resolution, and hardware implications for each.
- **Adaptive chirp modes** — Multi-scale radar operation via time-division sweep bandwidth switching (narrow/medium/wide), analogous to the British Chain Home / Chain Home Low / Chain Home Extra Low layered defense concept from WWII. Includes multi-channel staggered filter bandwidth analysis (academic concept for 3-RX architecture).

### Digital Design (In Progress)
- **FPGA digital backend** (planned) — SystemVerilog modules for the radar's digital subsystem, targeting Gowin GW5A (Tang Primer 25K, ~$35, in hand, 23K LUT4, 1008Kb BSRAM):
  - SPI master controllers for ADS8881 (ADC readout) and PGA113 (gain control)
  - DDS chirp waveform generator for VCO sweep control
  - Configurable FIR digital filter (supplements the analog anti-alias filter)
  - Timing controller for deterministic CONVST generation and adaptive gain scheduling
  - UART/USB data streaming to host PC
- All modules verified with self-checking testbenches using Verilator. See [`digital/spi-controller/`](digital/spi-controller/).

## Tools & Technologies

- **EDA:** KiCad 9 (schematic, PCB layout), Eagle 9.5 (Rev A reference)
- **Simulation:** LTspice (analog), Verilator (digital), GTKWave (waveforms)
- **HDL:** SystemVerilog (digital backend, verification)
- **FPGA Targets:**
  - *Phase 1:* Gowin GW5A (Sipeed Tang Primer 25K, ~$35, in hand) — 23K LUT4, 1008Kb BSRAM, 3 PMOD ports. Radar digital backend, RISC processor synthesis, SCPI diagnostic modules. Gowin EDA + open-source Yosys/Apicula.
  - *Phase 2:* Gowin GW5AST-138 (Sipeed Tang Mega 138K Pro, ~$200) — 138K LUT4, PCIe 3.0 x4, dual SFP+, SerDes transceivers. High-speed interface validation and multi-gigabit protocol work.
- **Documentation:** HTML with first-principles analysis, SVG block diagrams
- **Test Automation:** PyVISA (planned integration with SCPI instrument platform)

## Background

This project is part of a broader engineering portfolio spanning four interconnected tracks:

1. **FMCW Radar PCB** (this repo) — Mixed-signal PCB design with first-principles documentation, DFT-first methodology, and system-level analysis including adaptive chirp modes and ISM band upgrade path.

2. **Hardware Validation** — 4+ years at Texas Instruments (HVP-DB, Drivers & Bias) doing bench-level validation and characterization of high-power gate driver ICs, automated test systems (LabVIEW/TestStand/PXI), and DUT board design in Altium.

3. **Digital Design** — Pipelined RISC processor in SystemVerilog (see [RISC Pipeline repo](https://github.com/Pike1950/BradW_ECE4375_RISC_Pipeline)), refactored from university coursework with data forwarding, hazard detection, and FPGA synthesis targeting Tang Primer 25K.

4. **Test Infrastructure** — Modular SCPI instrument platform using Raspberry Pi 5 orchestration with Pico 2 W and FPGA measurement modules, PyVISA automation.

The radar project connects all four tracks: it's a mixed-signal PCB (track 1) designed with validation-engineer discipline (track 2), with an FPGA digital backend (track 3) that can be characterized by the SCPI instrument platform (track 4).

## Status

- [x] Rev B schematic complete (90 components, 4 sheets, 0 ERC errors)
- [x] Design rationale: FMCW principles, system overview, Sheet A (power)
- [x] Design rationale: Sheet B (IF input, protection, bias)
- [x] Design rationale: Sheet C (PGA, anti-alias filter, Sallen-Key topology)
- [x] Design rationale: Sheet D (FDA, ADC, SPI interface, J_DFT)
- [ ] Schematic updates (FPGA connector evaluation, ISM band provisions)
- [ ] PCB layout
- [ ] FPGA digital backend: SPI controller RTL and verification
- [ ] FPGA digital backend: DDS chirp generator
- [ ] FPGA digital backend: Digital FIR filter
- [ ] FPGA synthesis and bench validation
- [ ] Integration with SCPI instrument platform for automated characterization

## License

This is a personal engineering portfolio project. The FMCW radar design originated as a senior capstone project at Texas Tech University (HOTRODS, Spring 2020). The Rev B redesign, documentation, and all new digital design work are by Bradley Ward.

## Contact

Bradley Ward — [bradw858@gmail.com](mailto:bradw858@gmail.com) — [LinkedIn](https://linkedin.com/in/bradley-ward-49087766/)
