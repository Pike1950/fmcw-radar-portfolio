# Baseband Rev A — Eagle 9.5 (Original Senior Capstone)

## Overview

Original 3-channel FMCW radar baseband designed for the HOTRODS senior capstone project at Texas Tech University (Spring 2020). This design is preserved for reference — it shows what was built originally and documents the failures that motivated the Rev B redesign.

## Architecture

- **3 identical RX channels**, each with: LT6230 VGA + MCP4017 I²C digital pot → 4th-order Sallen-Key LP (LTC6242, 25 kHz cutoff) → SE-to-Diff converter (LTC6242, remaining 2 amps)
- **On-board ADC:** ADS1174IPAPT (quad 16-bit, 52 kSPS, 64-pin TQFP)
- **Power:** NCP163ASN330T1G 3.3V LDO, single rail, no analog/digital splitting
- **182 total components** on a single flat Eagle sheet

## What Went Wrong

1. **ADS1174 solder bridges** — 64-pin QFP with sub-mm pitch; pins bridged during hand assembly
2. **TPS717185 (1.8V LDO) solder bridges** — same issue
3. **No test infrastructure** — zero test points, no DFT header, no isolation capability
4. **Power routing error** — power connected through RX_3 section only; RX_1 required wire jumpers
5. **COVID-19 shutdown** — prevented further debugging after initial partial success

## Files

- `5_8GHzRadar.sch` — Eagle 9.5 schematic (all 3 channels + power on one sheet)
- `5_8GHzRadar.brd` — Eagle 9.5 board layout (4-layer, OSHPark)
