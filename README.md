# 24 GHz FMCW Radar Sensor

A personal engineering portfolio project: a short-range 24 GHz FMCW radar sensor spanning an RF front end, a mixed-signal I/Q baseband, and an FPGA digital backend. It began as a baseband redesign of a Texas Tech senior capstone (HOTRODS, Spring 2020) and has grown into a complete radar sensor design, carried out with the discipline of 4+ years of hardware validation at Texas Instruments.

## Project Overview

This project demonstrates RF integration, mixed-signal PCB design, digital hardware design, hardware verification, and system-level engineering, with first-principles documentation explaining every design decision. The completed work is a corrected, first-principles baseband design and its system design document; the active phase is scaling that foundation into a full 24 GHz radar sensor.

## The System

An FMCW (Frequency-Modulated Continuous Wave) radar transmits a frequency chirp, receives the reflection from a target, and mixes it with the current transmit frequency to produce a low-frequency beat signal. The beat frequency is proportional to range; the chirp-to-chirp phase gives Doppler velocity, and a complex (I/Q) baseband resolves the sign of that velocity (approaching versus receding).

The sensor is built around an integrated 24 GHz transceiver MMIC and is partitioned into two boards plus a downstream digital backend:

```
RF FRONT-END MODULE                       I/Q BASEBAND BOARD                    DIGITAL BACKEND
BGT24MTR11 (24 GHz, 1 TX / 1 RX)          per channel:                          range-Doppler FFT
 on-chip VCO, PA, LNA, I/Q mixers   I,Q   VGA -> anti-alias -> 18-bit SAR ADC    (FPGA / MCU) -> host
 TX/RX antennas, chirp ramp,        --->  I and Q sampled simultaneously
 first gain stage                  (zero  SPI control of the MMIC
                                     IF)
```

The two boards meet at a low-frequency analog I/Q interface, not a 24 GHz one, because the MMIC downconverts on-chip. That seam is what makes the split practical: the costly, iteration-prone 24 GHz RF and antennas stay on a small module, while the baseband stays on inexpensive FR4 and can be brought up and validated on its own.

## Evolution: Rev A to Rev B to Rev C

- **Rev A (2020).** 5.8 GHz, 3 RX channels, 182 components, Eagle, a single flat sheet. Built as the Texas Tech senior capstone; non-functional. The headline defect was a 10 kHz chirp rate that produced only about 5 ADC samples per ramp, far too few for FFT range extraction.
- **Rev B (current).** Began as a scaled, corrected 5.8 GHz baseband (one channel, KiCad 9, a modern signal chain, DFT-first methodology), captured as schematic plus a first-principles system design document. Rather than fabricate that band, Rev B is now redefined as the **24 GHz I/Q radar**: the band moves to 24 GHz, the project adopts the BGT24MTR11 (so it now owns the RF front end, not just the baseband), the baseband goes complex I/Q, and the sensor splits into an RF module and a baseband board. The baseband modernization below carries forward intact.
- **Rev C.** Additional receive channels for angle estimation, the original trilateration goal, on a proven single-channel Rev B.

### Baseband modernization (carried forward from the 5.8 GHz Rev B)

These corrections to the capstone baseband are band-agnostic and carry directly into the 24 GHz I/Q design.

| Aspect | Rev A (2020) | Rev B baseband (carried forward) |
| --- | --- | --- |
| EDA | Eagle 9.5, flat single sheet | KiCad 9, hierarchical |
| VGA | LT6230 + MCP4017 I²C digital pot | PGA113 (SPI, internal gain resistors) |
| ADC | ADS1174 (16-bit, 64-pin QFP, solder bridges) | ADS8881 (18-bit, 10-pin VSSOP) |
| SE to Diff | LTC6242 (improvised, no VOCM) | THS4531A (true FDA with VOCM) |
| Power | Single 3.3 V rail | 3V3A / 3V3D split via ferrite bead |
| Reference | Resistor divider | REF5025 (2.500 V, 0.05%, 3 µVpp) |
| DFT | None | J_DFT header, 17 TPs, 5 MMCX, 6 isolation resistors |

On top of this, the 24 GHz move adds an integrated-MMIC RF front end, a complex I/Q baseband (the chain above duplicated for I and Q with simultaneous sampling), and the two-board partition.

## Key Documents

| Document | Description |
| --- | --- |
| System Design Document | The 24 GHz radar system SDD, restyled to the PMVB module-doc schema with PHYSICS / DECISION / TRADEOFF / RISK reasoning callouts. Covers the two-board architecture, the carry-over analog design (power, references, gain, anti-alias filter, DFT), the FMCW principles, and an open decision register tracking the remaining 24 GHz choices. |
| Block Diagrams | Pin tables, signal maps, DFT reference, inter-sheet signal summary. |
| Schematic Review | Systematic review of the baseband schematic sheets. |
| Filter Analysis | Anti-alias filter transfer-function derivation. |

## Technical Highlights

### Analog and mixed-signal design

- **Supply splitting via ferrite bead.** BLM18PG221SN1D (220 Ω at 100 MHz) isolates analog from digital supply noise on a single continuous ground plane, with first-principles impedance analysis.
- **Paired decoupling capacitors.** Matched cap pairs (for example 10 µF + 100 nF) with different self-resonant frequencies for low impedance across a wide band, placed per a derived trace-inductance budget.
- **DFT-first methodology.** Test points, MMCX probes, and isolation resistors designed before the signal chain, now applied per channel for I and Q.

### System-level analysis

- **Chirp-rate correction.** Identified the Rev A parameter mismatch (about 5 samples per ramp) and derived the corrected chirp plan from first principles (sample-count-per-ramp to FFT resolution). The analysis is carrier-independent and re-derives the 24 GHz filter and ADC plan.
- **Band move to 24 GHz with complex I/Q.** Moving from 5.8 GHz to the 24 GHz ISM band raises range resolution from about 5 m to about 0.6 m and brings the RF front end into scope through an integrated MMIC. Complex I/Q sampling adds sign-of-velocity discrimination.
- **Designed for validation.** The board is designed for standalone bring-up and characterization on a homebrew SCPI instrument platform (see Related Repositories).

### Digital backend (planned)

SystemVerilog modules targeting the Gowin GW5A (Tang Primer 25K): SPI masters for the ADS8881 and the MMIC, a chirp ramp / DDS generator, a configurable FIR, and a deterministic timing controller, all verified with self-checking Verilator testbenches. See `digital/spi-controller/`.

## Related Repositories

| Repository | Description | Status |
| --- | --- | --- |
| [32-bit RISC Pipelined Processor](https://github.com/Pike1950/BradW_ECE4375_RISC_Pipeline) | 4-stage pipelined CPU refactored from Verilog to SystemVerilog. Shares the Verilator-clean SystemVerilog methodology used for this radar's digital backend. | SV conversion complete, synthesis next |
| [Poor Man's Validation Bench](https://github.com/Pike1950/poor-mans-validation-bench) | Modular SCPI + MCP instrument platform: Raspberry Pi 5 orchestration, Pico 2W USB-TMC modules, tiered FPGA. The bring-up and characterization platform for this radar. | Phase 0 complete; Module 1E (AWG) in build |

## Tools and Technologies

- **EDA:** KiCad 9. RF module on a controlled high-frequency stackup; baseband on FR4.
- **Simulation:** LTspice (analog), Verilator (digital), GTKWave (waveforms).
- **HDL:** SystemVerilog (digital backend, verification).
- **FPGA target:** Gowin GW5A (Sipeed Tang Primer 25K) for the digital backend.
- **Documentation:** Markdown rendered to HTML via Pandoc, PMVB-schema design docs with first-principles reasoning callouts.
- **Test automation:** PyVISA, integrating with the Poor Man's Validation Bench.

## Background

This project is one of four interconnected portfolio tracks:

1. **FMCW Radar Sensor** (this repo). RF integration plus mixed-signal PCB plus digital, with first-principles documentation and DFT-first methodology.
2. **Hardware Validation.** 4+ years at Texas Instruments (gate-driver characterization, automated test with LabVIEW / TestStand / PXI, DUT board design in Altium).
3. **Digital Design.** A pipelined RISC processor in SystemVerilog.
4. **Test Infrastructure.** The Poor Man's Validation Bench, a SCPI + MCP instrument platform.

The radar connects all four: a mixed-signal and RF sensor (track 1), designed with validation-engineer discipline (track 2), with an FPGA backend (track 3) characterized on the homebrew bench (track 4).

## Status

- **5.8 GHz baseband foundation (complete).** First-principles system design document and schematic capture of the corrected single-channel baseband. Established the methodology, the analog signal chain, and the DFT infrastructure that all carry forward.
- **24 GHz radar system design (in progress).**
  - System SDD reframed to the radar scope and the PMVB schema.
  - D1 resolved: BGT24MTR11 (1 TX / 1 RX), two-board partition (RF Front-End Module plus I/Q Baseband Board).
  - Open: antenna and RF stackup, ADC arrangement, ramp generation, chirp plan, and digital backend (tracked in the SDD decision register).
- **Next.** RF Front-End Module and I/Q Baseband Board schematics; digital backend RTL; bring-up and characterization on the Poor Man's Validation Bench.

## License

A personal engineering portfolio project. The FMCW radar originated as a Texas Tech senior capstone (HOTRODS, Spring 2020). The Rev B redesign, the 24 GHz radar system design, documentation, and all digital design work are by Bradley Ward.

## Contact

Bradley Ward, bradw858@gmail.com, [LinkedIn](https://linkedin.com/in/bradley-ward-49087766/)
