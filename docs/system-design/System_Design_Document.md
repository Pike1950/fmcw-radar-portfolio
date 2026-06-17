# 24 GHz FMCW Radar System Design Document

## Rev B: 24 GHz I/Q

**Version:** 0.8 (June 2026, system-scope radar SDD in the PMVB schema; all architecture decisions D1 to D7 resolved; schematic capture is the next phase)
**Project:** FMCW Radar Portfolio (`fmcw-radar-portfolio`)
**Revision:** Rev B (24 GHz I/Q)
**Status:** In Design
**Engineer:** Bradley Ward
**Scope:** A complete 24 GHz FMCW radar sensor, partitioned into two boards: an **RF Front-End Module** (BGT24MTR11, 24 GHz antennas, chirp ramp, first gain stage) and an **I/Q Baseband Board** (gain, anti-alias filtering, dual simultaneous-sampling ADC, digital interface). The digital backend that runs the range-Doppler FFT is downstream of both.
**Supersedes:** `System_Design_Document.html` (5.8 GHz single-ended baseband, v1.0, February 2026), retained in-repo as reference
**Format reference:** PMVB System Design Document and Module Design Document Schema

---

## Document Conventions

This document follows the PMVB module-doc section schema. The reasoning style from the original FMCW SDD is preserved: load-bearing design choices are called out with one of four tags so the "why" is explicit and auditable.

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> First-principles derivation or physical reasoning.</strong></div>
<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> A specific design choice with its rationale.</strong></div>
<div class="callout"><strong><span class="tag tag-tradeoff">TRADEOFF</span> What was gained versus what was given up.</strong></div>
<div class="callout callout-red"><strong><span class="tag tag-risk">RISK</span> A known limitation or sensitivity requiring attention.</strong></div>

A fifth marker is specific to this revision. Because the 24 GHz design is mid-definition, blocks that depend on an unresolved decision are flagged and cross-referenced to the decision register in section 10:

<div class="pending"><strong>PENDING (Dx):</strong> content blocked on an open decision; see section 10.</div>

Per the PMVB rule, the body describes what is used. Where a 24-GHz choice is not yet locked, the section states what carries over from the 5.8 GHz design, what must change, and which decision gates it, rather than guessing values that will move.

---

## Table of Contents

- [1. Theory of Operation](#1-theory-of-operation)
  - [1.1 What the system does](#11-what-the-system-does)
  - [1.2 Signal chain](#12-signal-chain)
  - [1.3 Methodology: work backward from the ADC](#13-methodology-work-backward-from-the-adc)
  - [1.4 The coupled parameter chain](#14-the-coupled-parameter-chain)
  - [1.5 The baseband is set by the chirp plan, not the carrier](#15-the-baseband-is-set-by-the-chirp-plan-not-the-carrier)
- [2. Functional Block Diagram](#2-functional-block-diagram)
- [3. Schematic Notes](#3-schematic-notes)
  - [3.1 Sheet A: Power and References](#31-sheet-a-power-and-references)
  - [3.2 Sheet B: I/Q Input from the MMIC](#32-sheet-b-iq-input-from-the-mmic)
  - [3.3 Sheet C: Gain and Anti-Alias Filter](#33-sheet-c-gain-and-anti-alias-filter)
  - [3.4 Sheet D: I/Q Digitization](#34-sheet-d-iq-digitization)
  - [3.5 DFT Infrastructure](#35-dft-infrastructure)
- [4. Pin Assignments](#4-pin-assignments)
- [5. Specifications](#5-specifications)
- [6. Sample Applications](#6-sample-applications)
- [7. Bill of Materials](#7-bill-of-materials)
- [8. Calibration Procedure](#8-calibration-procedure)
- [9. Layout Design Rationale](#9-layout-design-rationale)
- [10. Open Decisions and Known Issues](#10-open-decisions-and-known-issues)
- [11. References](#11-references)

---

## 1. Theory of Operation

### 1.1 What the system does

This is a complete short-range 24 GHz FMCW radar sensor. A transceiver MMIC transmits a frequency chirp, receives the reflection, and downconverts it on-chip to a complex baseband beat signal; the baseband then conditions and digitizes that signal into complex samples for a downstream range-Doppler FFT.

The sensor is partitioned into two boards (decision D1, section 10):

- **RF Front-End Module.** The Infineon BGT24MTR11 (1 TX / 1 RX) integrated transceiver, its 24 GHz TX and RX antennas, the chirp ramp source, and a first gain stage. The MMIC contains the VCO, PA, LNA, and quadrature mixers and presents differential in-phase (I) and quadrature (Q) beat signals at zero IF.
- **I/Q Baseband Board.** Per-channel gain and anti-alias filtering, simultaneous 18-bit sampling of I and Q, MMIC configuration over SPI, and the digital interface to the backend.

The two boards meet at a low-frequency analog I/Q interface, not a 24 GHz interface, because the MMIC has already downconverted on-chip. That is what makes the split practical (section 10, D1).

The radar is a signal-acquisition path, not a signal processor: it transforms microvolt-to-millivolt beat signals into clean complex samples, and range and velocity extraction happen downstream in the FFT engine.

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> 24 GHz integrated MMIC, two-board partition</strong>
<p>The 5.8 GHz Rev B was baseband-only and treated the RF front end (a discrete free-running VCO, mixers, and LNA) as external. At 24 GHz the project adopts the BGT24MTR11, which collapses that discrete RF chain into a single MMIC, so the RF front end is now part of the design. The sensor is split into an RF Front-End Module and an I/Q Baseband Board because the inter-board seam is low-frequency analog I/Q: that keeps the costly 24 GHz material and the iteration-prone RF isolated to a small board while the baseband stays on cheap FR4 and can be validated standalone. The complex I/Q output is also what enables sign-of-velocity discrimination (sections 1.5 and 3.4).</p></div>

### 1.2 Signal chain

Locked blocks are in plain text; blocks whose implementation depends on an open decision are flagged.

```
RF FRONT-END MODULE
  24 GHz MMIC (on-chip VCO, PA, LNA, I/Q mixers); TX and RX via 24 GHz antennas
  I, Q (zero IF) -> first gain stage -> [ I/Q interface connector ]
  chirp ramp -> MMIC VCO tune (kept local to this board)     (DAC ramp, calibrated)

I/Q BASEBAND BOARD
  [ I/Q interface connector ] -> per channel: VGA -> anti-alias filter -> SAR ADC
     I and Q sampled simultaneously to preserve complex phase
  -> digital backend: Tang Primer 25K FPGA (range-Doppler FFT) -> host
  MMIC configuration + control over SPI (routed across the connector)
```

The two conditioning chains (I and Q) are nominally identical. Channel-to-channel gain and phase match is a first-class concern: I/Q imbalance maps directly to image-frequency leakage in the complex spectrum and corrupts the sign of the measured velocity.

### 1.3 Methodology: work backward from the ADC

This methodology carries over from the 5.8 GHz design unchanged, because it is independent of carrier frequency and of real-versus-complex sampling. Every analog decision is anchored to what the ADC needs to see.

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> The ADC defines the budget</strong>
<p>The ADS8881 digitizes a differential input against a 2.500 V reference (REF5025). One LSB at 18 bits over the differential full scale is V<sub>REF</sub> &times; 2 / 2<sup>18</sup> = 5.000 V / 262,144 &approx; 19 &micro;V. Every upstream stage exists to deliver a clean signal into that window: the VGA fills the ADC range regardless of target distance, the anti-alias filter keeps out-of-band energy from folding in, and the reference and bias networks must hold stable to a small fraction of an LSB or they waste resolution. Noise or offset referred to the input is only meaningful relative to that ~19 &micro;V step.</p></div>

### 1.4 The coupled parameter chain

The chirp timing, the sample rate, and the FFT size are not independent. They are bound by one relation that Rev A violated and Rev B respects.

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> The three coupled parameters</strong>
<p>f<sub>s</sub> &times; T<sub>sweep</sub> = N<sub>samples</sub>, and N<sub>samples</sub> must be at least N<sub>FFT</sub> for useful frequency resolution.</p>
<p>Rev A set T<sub>sweep</sub> = 50 &micro;s without checking: at 100 kS/s that is only 5 samples per ramp, and a 5-point FFT has no resolution. The corrected design sets T<sub>sweep</sub> in the millisecond range so that f<sub>s</sub> &times; T<sub>sweep</sub> yields several hundred samples per ramp, enough for a 512-point FFT. The ADC sample rate did not cause the Rev A failure; the chirp rate did.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Chirp plan (D6)</strong>
<p>Sweep 250 MHz over a 1 ms chirp (slope 250 GHz/s), 50 m design range, sampled at 256 kSPS for 256 samples per chirp and a 256-point range FFT (~83 range bins of 0.6 m). 128 chirps per frame give a 128 ms frame (~8 frames/s), ~5 cm/s velocity resolution, and ±3.1 m/s unambiguous velocity. The max beat at 50 m is 83 kHz, well inside the 128 kHz Nyquist, leaving the anti-alias filter an 83-to-128 kHz transition band. More range is paid for with sample rate (the ADS8881 reaches 1 MSPS), not chirp time, so velocity is unaffected.</p></div>

### 1.5 The baseband is set by the chirp plan, not the carrier

This is the point that makes the band move tractable: moving from 5.8 GHz to 24 GHz does not, by itself, change the baseband.

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> Beat frequency depends on slope and range, not carrier</strong>
<p>For a target at range R, the beat frequency is f<sub>beat</sub> = 2&middot;R&middot;S / c, where S is the chirp slope (sweep bandwidth / sweep time). The carrier frequency f<sub>0</sub> does not appear. So the anti-alias filter cutoff and the ADC rate are governed by the maximum range beat, set by the chirp plan, and are re-derived with the same analysis used at 5.8 GHz.</p>
<p>Range resolution is set by usable sweep bandwidth: &Delta;R = c / (2B). Across the 24 GHz ISM band (~250 MHz usable) the floor is about 0.6 m, roughly an 8&times; improvement over the 30 MHz / 5.0 m of the 5.8 GHz §15.245 mode, and a hard limit independent of the ADC.</p></div>

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> What the carrier does change: Doppler</strong>
<p>Doppler shift scales with carrier: f<sub>D</sub> = 2&middot;v&middot;f<sub>0</sub> / c. At 24 GHz the Doppler is about 4&times; that at 5.8 GHz for the same velocity. Doppler is resolved in the slow-time (chirp-to-chirp) FFT and sets velocity-axis scaling and maximum unambiguous velocity; it does not drive the fast-time anti-alias filter, which remains governed by the range beat.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Complex I/Q resolves the sign of velocity</strong>
<p>A single real beat channel cannot tell an approaching target from a receding one; both fold to the same positive beat frequency. Sampling I and Q gives a complex baseband whose FFT is two-sided, so positive and negative Doppler are distinct. This is the architectural reason the board doubles to two channels (section 3.4) and the reason simultaneous sampling and I/Q match matter.</p></div>

---

## 2. Functional Block Diagram

The system and sheet-level block diagrams live in `docs/block-diagrams/` (`block_diagram_system.svg`, `block_diagram_sheet_a.svg`, `block_diagram_sheets_bcd.svg`).

The existing diagrams show the 5.8 GHz single real chain (one mixer input, one PGA, one filter, one FDA, one ADC). They are redrawn to show the two-board partition: the BGT24MTR11 with its antennas and first gain stage on the RF Front-End Module, the differential I and Q crossing the interface connector, and the two parallel conditioning chains into a simultaneous-sampling ADC stage on the I/Q Baseband Board.

---

## 3. Schematic Notes

The design spans two boards. The notes below explain the intent behind each block; the full schematics live in the KiCad projects, and detailed per-board design documents (RF Front-End Module, I/Q Baseband Board) will sit under this system SDD as each board matures, mirroring the PMVB per-module docs. Section 3.0 summarizes the RF Front-End Module; sections 3.1 to 3.5 cover the I/Q Baseband Board, where Sheet A (power and references) and the DFT infrastructure carry over from the 5.8 GHz design and Sheets B, C, and D are reworked for the MMIC I/Q interface and the dual-channel architecture.

### 3.0 RF Front-End Module

The RF Front-End Module carries the BGT24MTR11 transceiver, its 24 GHz TX and RX antennas, the chirp ramp source, a first gain stage on each of the I and Q outputs, and the connector to the baseband board.

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> The first gain stage lives on the RF module</strong>
<p>The I and Q signals leaving the MMIC are low-level (microvolt to millivolt) and have to cross a board-to-board connector. A first gain stage on the RF module amplifies them before the crossing, so the inter-board interface carries a larger, lower-impedance signal and is far less vulnerable to pickup. The remaining gain and all of the filtering live on the baseband board.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> External patch array on 4-layer RO4350B (D2)</strong>
<p>The RF module uses external PCB patch antennas (a small patch array), microstrip-fed from the BGT24MTR11, plus a build-option 2.92 mm connector launch (DNP) so an external 24 GHz antenna can drive first bring-up. The stackup is 4-layer RO4350B (L1 RF and antenna, L2 solid ground reference, L3 power, L4 control), fabricated at PCBWay, which runs 4-layer Rogers. RO4350B sits just above its sweet spot at 24 GHz, giving up a little patch efficiency versus RO3003, which is held as a later upgrade. ENIG finish for the fine-pitch MMIC and the patches.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> DAC-driven chirp ramp with calibration (D5)</strong>
<p>The VCO tune voltage is generated open-loop by a DAC and pre-distorted from a measured frequency-versus-voltage curve, rather than closed-loop with an FMCW ramp PLL. Over the ~250 MHz sweep at 24 GHz the fractional bandwidth is about 1%, the same regime in which the original 5.8 GHz design ran its VCO, so the residual nonlinearity is modest and a calibrated open-loop ramp is adequate. The ramp source stays local to the RF module so the tune line is short. The accepted cost is open-loop drift with temperature and the calibration table to maintain; an ADF4159-class ramp PLL is the upgrade path if bench measurement shows linearity is limiting range accuracy.</p></div>

### 3.1 Sheet A: Power and References

Sheet A is band-agnostic and carries over essentially intact, with one change: the common-mode and reference nets now fan out to two channels instead of one. The architecture is a single 5 V input, an on-board 3.3 V LDO, an analog/digital supply split via ferrite bead, a precision 2.500 V reference, and a buffered mid-supply common-mode rail.

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Analog/digital split via ferrite bead, single ground plane</strong>
<p>The 3V3A and 3V3D rails are separated by a BLM18PG221SN1D ferrite bead (220 &Omega; at 100 MHz, under 1 &Omega; DC). It passes DC cleanly to the analog rail while presenting high impedance to the digital switching spectrum, giving over 40 dB of attenuation to SPI-edge noise. The ground stays a single continuous plane; isolation is done on the supply, not by splitting the return (see section 9.3).</p></div>

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> Why V<sub>CM</sub> = V<sub>DD</sub>/2 = 1.650 V</strong>
<p>All active parts run from a single 3.3 V supply with no negative rail, so an AC signal must be biased to the midpoint to maximize swing before clipping. At V<sub>CM</sub> = 1.650 V the signal gets symmetric &plusmn;1.65 V headroom (less op-amp saturation, ~100&ndash;200 mV per rail). This common-mode voltage appears everywhere: it biases the I/Q inputs, sets the PGA reference, and drives each FDA's VOCM pin. A single buffered, low-impedance source (an OPA320 on Sheet A) feeds all stages so they share one common mode; any mismatch becomes a DC offset that wastes ADC range. With two channels, the same buffered V<sub>CM</sub> and V<sub>REF</sub> nets fan out to both I and Q.</p></div>

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> Reference error is gain error</strong>
<p>REF5025 (2.500 V, 0.05%, 3 &micro;V<sub>pp</sub> noise) sets the ADC full scale. Any error in V<sub>REF</sub> maps directly to a gain error on every reading: gain error = &Delta;V<sub>REF</sub> / V<sub>REF,nom</sub>. The reference therefore gets a paired-capacitor decoupling network (10 &micro;F bulk + 100 nF high-frequency, different self-resonant frequencies) at the ADC reference pin, as the ADS8881 datasheet recommends.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Decoupling placement is a derived budget, not a guideline</strong>
<p>Trace inductance is ~1 nH/mm. The placement distance for each bypass capacitor follows from the frequency it must serve and the acceptable trace impedance: the higher the frequency, the shorter the trace. The design's rules (100 nF within 2 mm, 1 &micro;F within 5 mm, 10 &micro;F within 10 mm) are the quantitative result of that inductance-versus-impedance analysis, not copied from a reference design. This carries over unchanged.</p></div>

### 3.2 Sheet B: I/Q Input from the MMIC

This is the most-changed sheet. The 5.8 GHz Sheet B was a single-ended, AC-coupled input: an SMA from a discrete mixer, a series current-limit resistor, an ESD diode, a 100 nF C0G capacitor to strip the mixer's undefined DC, and a 47 kΩ bias to V<sub>CM</sub> (high-pass corner ~34 Hz). For a 24 GHz zero-IF I/Q front end that topology is largely replaced.

<div class="pending"><strong>Input interface (D1 resolved):</strong> The BGT24MTR11 presents differential I and Q at zero IF. The baseband-board input interfaces to two differential pairs arriving over the interconnect from the RF module's first gain stage, not a single-ended SMA. The exact termination, common-mode handling, and ESD network follow the BGT24MTR11 I/Q output specification.</div>

<div class="callout callout-red"><strong><span class="tag tag-risk">RISK</span> Zero-IF DC must not be blocked</strong>
<p>The old Sheet B AC-coupled specifically to remove the mixer's undefined DC bias. At zero IF the beat band extends down to DC, so a stationary or slow-moving target sits near DC. The Rev B input cannot high-pass the way the 5.8 GHz design did. DC offset is handled instead (per-channel calibration or a servo), and 1/f (flicker) noise now sits in-band and must be budgeted. This is the single biggest conceptual change from the old input stage.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Keep ESD and current-limiting, adapted to differential</strong>
<p>The connector/interface ESD protection (TPD1E10B06 class) and the per-line series current-limit concept carry over, applied to each leg of the differential I and Q pairs rather than a single-ended line.</p></div>

### 3.3 Sheet C: Gain and Anti-Alias Filter

The gain and filter method carries over; the component values re-derive from the 24 GHz chirp plan (D6), and the whole chain duplicates for I and Q.

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> Variable gain follows the R<sup>&minus;4</sup> range law</strong>
<p>Received power varies as R<sup>&minus;4</sup> (the radar range equation): a target at 10 m returns 10,000&times; the power of the same target at 100 m, about 40 dB, and a 100-to-1 span is roughly 80 dB, which approaches the ~84 dB an 18-bit SAR can usefully cover and is exceeded for wider spans. Without variable gain the ADC would clip on near targets or bury far ones in the noise. An SPI-controlled differential VGA per channel fills the ADC window for each range regime. (The Rev B PGA113 was a single-ended part; the differential I/Q here keeps the gain stage differential, so the adaptive-gain concept and the SPI control carry forward, but the part changes.)</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Anti-alias before sampling, cutoff set by Nyquist not by the chirp</strong>
<p>A 4th-order Sallen-Key Butterworth low-pass sits before each ADC. Its cutoff is set by f<sub>s</sub>/2 and the signal band, not by the chirp rate. Whether the chirp is fast or slow, energy above Nyquist must be kept from folding into the band. The topology and the singly-terminated design method carry over from the 5.8 GHz Sheet C. With the chirp plan set (D6: 256 kSPS, 83 kHz max beat), the cutoff lands near 100 kHz, inside the 83-to-128 kHz window between the max beat and Nyquist; the L/C/R values follow from a Butterworth synthesis at that cutoff.</p></div>

<div class="callout"><strong><span class="tag tag-tradeoff">TRADEOFF</span> Duplicating for Q buys complex sampling at the cost of match</strong>
<p>Adding a second identical gain-plus-filter chain for Q is what enables sign-of-velocity, but it introduces channel mismatch. Gain and phase match between the I and Q chains must be held through matched components and symmetric layout, or image rejection in the complex FFT degrades.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Adaptive differential gain per channel (D4)</strong>
<p>Each channel uses an SPI-controlled differential VGA rather than a fixed-gain stage, so the receiver fills the 18-bit ADC across the R<sup>&minus;4</sup> range swing instead of compromising between near-target clipping and far-target SNR. A differential VGA (not the single-ended PGA113) keeps the I/Q path differential through to the ADC; the part is chosen to match the BGT24MTR11 I/Q levels and the ADS8881 input range. I and Q use matched VGAs, with residual gain and phase mismatch calibrated on PMVB.</p></div>

The only open item on this sheet is the component synthesis at that cutoff, which is design work, not a gated decision.

### 3.4 Sheet D: I/Q Digitization

This sheet changes from one ADC to a simultaneous-sampling I/Q pair. The ADS8881 and REF5025 rationale carry over; the count doubles and the convert is shared.

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Two ADS8881 on a shared CONVST, simultaneous I/Q (D3)</strong>
<p>To preserve the complex phase relationship between I and Q, the two channels are sampled at the same instant. Two ADS8881 18-bit SAR ADCs share one CONVST line so their sample apertures coincide. This reuses the proven Rev B converter, the REF5025 reference, and the existing SPI controller RTL; the one cost, a small inter-channel aperture skew, is negligible at the radar's low beat frequencies and is calibrated out on PMVB. Because the MMIC output is already differential, the THS4531A's old single-ended-to-differential role is revisited: it likely becomes a differential receiver and level-shifter into the ADC rather than an SE-to-Diff converter.</p></div>

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> SAR, not sigma-delta</strong>
<p>A SAR ADC samples at a discrete, deterministic instant. A sigma-delta averages over its decimation window, which would smear the instantaneous beat frequency and corrupt the range-Doppler FFT. The ADS8881 (18-bit, up to 1 MSPS, run well below its maximum) is the right converter class, and this rationale is unchanged from the 5.8 GHz design.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Tang Primer 25K FPGA backend (D7)</strong>
<p>A Gowin GW5A (Tang Primer 25K) ingests both ADC streams over SPI and runs the range-Doppler FFT, reusing the SPI controller RTL and the Verilator-clean SystemVerilog methodology shared with the RISC CPU project. The ~9 Mbps data rate is light for the part; the FPGA is chosen over an MCU for the digital-design showcase and the RTL reuse, with a board dedicated per radar (additional Tang Primers planned rather than time-sharing the PMVB unit).</p></div>

### 3.5 DFT Infrastructure

Design-for-test is a first-class requirement and carries over, now per channel. The 5.8 GHz board used a J_DFT header, 17 test points, 5 MMCX probe connectors, and six 10 kΩ isolation resistors on the analog monitor nets.

<div class="callout callout-blue"><strong><span class="tag tag-physics">PHYSICS</span> An isolation resistor plus a probe is a harmless low-pass</strong>
<p>A 10 kΩ isolation resistor with a ~15 pF scope-probe tip forms a low-pass at f = 1/(2&pi; &times; 10k &times; 15p) &approx; 1 MHz, well above the beat band, so the probe point never meaningfully loads the chain. The resistors are always populated; they protect the signal chain even when the header is unconnected.</p></div>

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Per-channel observability</strong>
<p>With two chains, the monitor set (VGA output, filter output, ADC differential inputs, FDA outputs) is provided for both I and Q, so each path is independently observable. Bring-up and characterization run on the PMVB instrument platform rather than commercial bench gear.</p></div>

---

## 4. Pin Assignments

With the backend fixed as the Tang Primer 25K (D7), the interface is defined in kind and the detailed pin map is now a design task. The two ADS8881 and the MMIC sit on a shared SPI bus (shared SCLK and SDI, per-device chip-select), the ramp DAC drives the VCO tune, and the FPGA generates CONVST and the chirp timing. The J_DFT pinout concept carries over, extended for the second channel and the MMIC control interface.

---

## 5. Specifications

| Parameter | Value | Status |
|-----------|-------|--------|
| Carrier band | 24 GHz ISM, 24.0&ndash;24.25 GHz (~250 MHz usable) | Locked |
| Range resolution floor | ~0.6 m (&Delta;R = c/2B at 250 MHz) | Locked |
| Baseband | Complex I/Q, two channels, simultaneous sampling | Locked |
| ADC | Two ADS8881 (18-bit SAR), differential, shared CONVST for simultaneous I/Q, 2.500 V REF5025 | Locked |
| Sweep bandwidth / chirp duration / slope | 250 MHz / 1 ms / 250 GHz/s | Locked (D6) |
| Max range (design) | 50 m (sample rate gives headroom; far detection is link-budget-limited) | Locked (D6) |
| Max beat frequency / sample rate | 83 kHz at 50 m / 256 kSPS | Locked (D6) |
| Samples per chirp / range FFT | 256 / 256-point (~83 range bins) | Locked (D6) |
| Chirps per frame / frame rate | 128 / ~8 frames per second | Locked (D6) |
| Velocity resolution / max unambiguous velocity | ~5 cm/s / ±3.1 m/s | Locked (D6) |
| I/Q gain and phase match target | sets image rejection | Design + calibration (matched VGAs) |
| Digital backend | Tang Primer 25K (Gowin GW5A) FPGA, range-Doppler FFT, ~9 Mbps ingest | Locked (D7) |

This table is kept in parity with any downstream summary table as values lock.

---

## 6. Sample Applications

Outline; the backend is the Tang Primer 25K FPGA (D7), and these recipes detail out as the firmware and RTL come up.

1. **Single moving target.** Transmit a chirp frame, capture I and Q, run the range-Doppler FFT, read the occupied range bin and the sign of the Doppler (approaching versus receding).
2. **Two targets at different ranges.** Demonstrate range separation at the ~0.6 m resolution floor.
3. **Bench characterization on PMVB.** Stimulus and measurement recipe for noise floor, I/Q gain and phase match, and chirp linearity using PMVB Tier 1 / Tier 2 modules.

---

## 7. Bill of Materials

The architecture parts are now fully specified across both boards and the backend. The final BOM with exact passives and part numbers is produced at schematic capture, sourced per the PMVB rule (Mouser &gt; Digi-Key &gt; Microcenter &gt; Amazon).

Carries over: ADS8881 (&times;2, one per I/Q channel), REF5025, THS4531A, OPA320, TPS7A2033 LDO, BLM18PG221SN1D ferrite. Changes: the single-ended PGA113 is replaced by a differential VGA per channel (D4). Adds: the BGT24MTR11 transceiver and its RF-module support, a ramp DAC for the VCO tune (D5), a Tang Primer 25K FPGA backend (D7), and second-channel duplicates of the conditioning chain.

---

## 8. Calibration Procedure

Targets (outline; detailed once the chain and backend lock): I/Q gain match, I/Q phase match (image rejection), per-channel DC offset (the zero-IF concern from section 3.2), chirp linearity, and range accuracy. Each references the SCPI commands the bring-up firmware exposes.

---

## 9. Layout Design Rationale

The layout rationale carries over almost wholesale. The original chapter notes that at a DC-to-tens-of-kHz beat band, transmission-line impedance and wavelength effects are irrelevant; the real layout drivers are confining return current and isolating digital (SPI) noise. Those drivers are unchanged at 24 GHz, because the high-frequency RF is inside the MMIC, not on this board.

- **Stackup (carries over).** 4-layer: L1 signal and components, L2 continuous ground with no splits, L3 power (3V3A pour with a small 3V3D island), L4 secondary signal.
- **Ground plane (carries over).** One continuous unbroken ground; the split-plane approach is rejected on a worked loop-area noise calculation (a split forces a large return loop and tens of LSBs of induced noise; the continuous plane keeps it to a fraction of an LSB).
- **Placement (carries over, duplicated).** Signal-flow zones left to right, bypass placement per the derived budget, FDA-to-ADC pin-to-pin under 5 mm. The analog chain zone is duplicated for the Q path.

<div class="callout callout-teal"><strong><span class="tag tag-decision">DECISION</span> Dual I/Q differential routing</strong>
<p>Two matched differential pairs run into the two ADCs, each length-matched (the original ~0.4 ns skew budget transfers). New for I/Q: inter-pair separation (3W or a guard trace) so the I and Q pairs do not couple, and channel-to-channel layout symmetry so the gain and phase match the design depends on actually holds on the board.</p></div>

---

## 10. Open Decisions and Known Issues

All seven architecture decisions (D1 through D7) are resolved. The register below is the settled record; the next phase is schematic capture, not further architecture decisions.

| # | Decision | Options | Drives | Depends on |
|---|----------|---------|--------|------------|
| D1 | MMIC and board split | **RESOLVED:** BGT24MTR11 (1 TX / 1 RX); two boards (RF Front-End Module + I/Q Baseband Board), split at the low-frequency I/Q seam after a first gain stage on the RF module | I/Q interface, RF layout scope, connectors | done |
| D2 | Antenna and RF stackup | **RESOLVED:** external PCB patch array + DNP 2.92 mm connector launch; 4-layer RO4350B at PCBWay (RO3003 held as a later efficiency upgrade), ENIG finish | RF layout, stackup, cost | done |
| D3 | ADC arrangement | **RESOLVED:** two synchronized ADS8881 (18-bit SAR) on a shared CONVST; reuses the proven part, REF5025, and SPI RTL | I/Q phase fidelity, BOM, layout | done |
| D4 | Front-end gain | **RESOLVED:** adaptive gain via an SPI-controlled differential VGA per channel (replaces the single-ended PGA113); matched I/Q, residual calibrated on PMVB | gain match, dynamic range | done |
| D5 | Ramp generation | **RESOLVED:** DAC-driven VCO tune with calibration (open-loop, adequate at ~1% fractional BW); ADF4159-class ramp PLL noted as the upgrade if linearity limits range | chirp linearity, parts, firmware | done |
| D6 | Chirp plan | **RESOLVED:** 250 MHz / 1 ms (250 GHz/s), 50 m, 256 kSPS, 256-pt FFT, 128 chirps/frame; 0.6 m range res, ±3.1 m/s, ~5 cm/s, ~8 fps | filter cutoff, ADC rate, range/velocity | done |
| D7 | Digital backend | **RESOLVED:** Tang Primer 25K (Gowin GW5A) FPGA running the range-Doppler FFT, reusing the SPI controller RTL and SystemVerilog methodology; dedicated board per radar (more Tang Primers planned) | throughput, FPGA acquisition | done |

**Known issues / future work.** Rev C adds receive channels for angle estimation (the original 1 TX / 3 RX trilateration goal) on a proven single-channel Rev B front end.

<div class="callout callout-red"><strong><span class="tag tag-risk">RISK</span> The 5.8 GHz design already flagged the chirp-linearity path</strong>
<p>The original SDD noted that the free-running HMC431LP4E VCO was acceptable only because the 30 MHz mode used ~5% of its tuning range, and that wider sweeps would reveal nonlinearity for which a PLL-based control loop was the recommended upgrade. At 24 GHz over ~250 MHz the fractional bandwidth is again about 1%, so D5 takes the calibrated open-loop DAC ramp, with an ADF4159-class FMCW ramp PLL held as the upgrade if bench measurement shows chirp linearity is limiting range accuracy.</p></div>

---

## 11. References

Carried over from the 5.8 GHz SDD:

- Eric Bogatin, *Signal and Power Integrity, Simplified* (Prentice Hall).
- Henry Ott, *Electromagnetic Compatibility Engineering* (Wiley), Ch. 17&ndash;18.
- TI SLYT499 / SLYT512, grounding in mixed-signal systems.
- TI SLTA055, bypass capacitor selection for high-speed ADCs; Murata capacitor impedance library.
- TI SLOA024B, analysis of the Sallen-Key architecture.
- TI SLOA054, fully differential amplifiers; THS4531A and ADS8881 datasheets.
- Merrill Skolnik, *Introduction to Radar Systems* (McGraw-Hill).

Added for Rev B (24 GHz I/Q):

- Infineon BGT24MTR11 24 GHz transceiver datasheet (front-end candidate, D1).
- Analog Devices ADF4159 FMCW ramp-generating PLL datasheet (ramp candidate, D5).
- FCC rules for the 24 GHz ISM band (regulatory limits, to be cited in a regulatory subsection).
- TI REF5025 voltage reference datasheet.
- PMVB System Design Document and Module Design Document Schema (documentation format reference).
