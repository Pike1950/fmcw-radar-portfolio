# Baseband Rev B — KiCad 9 Schematic

## Overview

Single-channel FMCW radar baseband signal conditioning path. 4-sheet hierarchical schematic, 90 components, 0 ERC errors.

## Sheets

| Sheet | File | Function | Components |
|-------|------|----------|------------|
| Root | `Baseband PCB.kicad_sch` | Top-level hierarchy with sheet instances | — |
| A | `Baseband_Power_Refs.kicad_sch` | Power (TPS7A2033 LDO, 3V3A/3V3D split), References (REF5025, OPA320 VCM buffer) | 29 |
| B | `Baseband_IF_Input_Protection_Bias.kicad_sch` | SMA input, ESD protection (TPD1E10B06), AC coupling, DC bias to VCM | 7 |
| C | `Baseband_PGA_AntiAlias.kicad_sch` | PGA113 (1–200× gain), 4th-order Sallen-Key Butterworth LP at 15 kHz (LTC6242) | 19 |
| D | `Baseband_FDA_Driver_ADC_SPI_Interface.kicad_sch` | THS4531A FDA, ADS8881 18-bit SAR ADC, J_DFT header, SPI interface | 35 |

## Key Design Decisions

See [Design Rationale](../../docs/design-rationale/RevB_Design_Rationale.html) for first-principles analysis of every component choice.

## Status

- [x] Schematic complete
- [x] ERC clean (0 errors, 0 warnings)
- [ ] Layout in progress
