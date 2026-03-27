# SPI Controller — SystemVerilog

## Overview

A SystemVerilog SPI master controller designed to interface with the FMCW radar baseband's ADS8881 ADC and PGA113 programmable gain amplifier. This module bridges the analog baseband project with the digital verification track, demonstrating the full V-model from specification through bench validation.

## Status

**Planned** — RTL design and verification are Phase 4 of the project roadmap.

## Target Specifications

### ADS8881 SPI Interface
- CPOL=0, CPHA=1 (SPI Mode 1)
- SCLK: up to 70 MHz
- 18-bit data, MSB first
- CONVST pulse initiates conversion (600 ns conversion time)
- Data clocked out on SCLK falling edge

### PGA113 SPI Interface
- CPOL=0, CPHA=0 (SPI Mode 0)
- 16-bit command word (8-bit register address + 8-bit gain code)
- Separate chip select from ADC

## Planned Architecture

```
                    SPI Controller (Top)
    ┌─────────────────────────────────────────────┐
    │  ┌────────────┐     ┌────────────┐          │
    │  │ ADC SPI    │     │ PGA SPI    │          │
    │  │ Master     │     │ Master     │          │
    │  │ (Mode 1)   │     │ (Mode 0)   │          │
    │  └──────┬─────┘     └──────┬─────┘          │
    │         │                  │                 │
    │  ┌──────▼──────────────────▼─────┐          │
    │  │        Timing Controller      │          │
    │  │  (CONVST generation, gain     │          │
    │  │   scheduling, sample clock)   │          │
    │  └───────────────────────────────┘          │
    │                                             │
    │  ┌───────────────────────────────┐          │
    │  │     Data Output Interface     │──→ UART  │
    │  │  (FIFO, framing, streaming)   │          │
    │  └───────────────────────────────┘          │
    └─────────────────────────────────────────────┘
```

## Verification Plan

- Constrained-random testbench with self-checking scoreboard
- Timing verification against ADS8881 datasheet specifications
- PGA gain code verification against PGA113 register map
- Coverage targets: all gain settings, all timing corner cases

## FPGA Targets

- **Gowin GW1NR-9** (Tang Nano 9K, ~$20) — 8,640 LUT4, sufficient for SPI + DDS + FIR filter. Gowin EDA with SystemVerilog support. Primary target for the radar digital backend.
- **Gowin GW5A** (Tang Primer 25K, ~$35, in hand) — 23,040 LUT4, 1008Kb BSRAM, 3 PMOD ports. Shared with RISC processor project. Gowin EDA + open-source Yosys/Apicula toolchain.

## Toolchain

- **Simulation:** Verilator + GTKWave (WSL2 or native Linux)
- **Synthesis:** Yosys (iCE40) or Gowin EDA (GW1NR-9)
- **Place & Route:** nextpnr (iCE40) or Gowin EDA
