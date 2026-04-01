# AURIX TC3xx to TC4xx Migration Guide

> **Comprehensive step-by-step playbook for porting iLLD code examples from TC3xx to TC4xx**

---

## Table of Contents

- [Part 1: Overview](#part-1-overview)
- [Part 2: Infrastructure Migration (Generic)](#part-2-infrastructure-migration-generic)
  - [2.1 Project Naming Convention](#21-project-naming-convention)
  - [2.2 `.ads/install-libraries.json`](#22-adsinstall-librariesjson)
  - [2.3 `Configurations/Ifx_Cfg.h`](#23-configurationsifx_cfgh)
  - [2.4 `Boards/board.h` (New for TC4xx)](#24-boardsboardh-new-for-tc4xx)
  - [2.5 Linker Script Changes](#25-linker-script-changes)
  - [2.6 `Cpu0_Main.c` Boilerplate Changes](#26-cpu0_mainc-boilerplate-changes)
  - [2.7 Additional `CpuX_Main.c` Files](#27-additional-cpux_mainc-files)
  - [2.8 `.cproject` Changes](#28-cproject-changes)
- [Part 3: Peripheral API Migration](#part-3-peripheral-api-migration)
  - [3.1 GTM TOM → EGTM ATOM (Timer/PWM)](#31-gtm-tom--egtm-atom-timerpwm)
  - [3.2 EVADC → ADC / TMADC](#32-evadc--adc--tmadc)
  - [3.3 OneEye Integration](#33-oneeye-integration)
- [Part 4: TC4xx Sub-Family Variant Table](#part-4-tc4xx-sub-family-variant-table)
- [Part 5: Migration Checklist](#part-5-migration-checklist)

---

## Part 1: Overview

### What Are TC3xx and TC4xx?

**TC3xx** and **TC4xx** refer to successive generations of the Infineon **AURIX™ TriCore** microcontroller families designed for automotive and safety-critical applications.

| Generation | iLLD Version | Key Characteristics |
|------------|-------------|---------------------|
| **TC3xx** | iLLD **v1.x** (`iLLD_1_0_1_17_0`) | 2–4 TriCore cores, GTM timer module, EVADC, SCU-based clock & watchdog |
| **TC4xx** | iLLD **v2.x** (`iLLD_2_2_0_0_0` / `iLLD_2_3_0`) | Up to 6 TriCore cores, EGTM timer module, new ADC/TMADC, WTU-based watchdog, PPU co-processor support, LLVM toolchain support |

### TC3xx Devices in This Repository

| Device | Core Count | Example Prefix |
|--------|-----------|----------------|
| **TC375** | 3 (CPU0–CPU2) | `iLLD_TC375_ADS_*`, `*_KIT_TC375_LK` |
| **TC387** | 4 (CPU0–CPU3) | `iLLD_TC387_ADS_*`, `*_KIT_TC387_TFT` |
| **TC397** | 6 (CPU0–CPU5) | `iLLD_TC397_ADS_*`, `*_KIT_TC397_TFT` |

### TC4xx Devices in This Repository

| Device | Sub-family | Remap Name | Example Prefix |
|--------|-----------|-----------|----------------|
| **TC4D7** | TC4Dx | TC4DA | `iLLD_TC4D7_LK_ADS_*` |
| **TC4D9** | TC4Dx | TC4DA | (supported in install-libraries.json) |
| **TC499** | TC49x | TC49xN | (supported in install-libraries.json) |
| **TC497** | TC49x | TC49xN | (supported in install-libraries.json) |
| **TC489** | TC48x | TC48x | (supported in install-libraries.json) |
| **TC487** | TC48x | TC48x | (supported in install-libraries.json) |
| **TC469** | TC46x | TC46x | (supported in install-libraries.json) |
| **TC467** | TC46x | TC46x | (supported in install-libraries.json) |
| **TC457** | TC45x | TC45x | (supported in install-libraries.json) |
| **TC447** | TC44x | TC44x | (supported in install-libraries.json) |

### Recommended Migration Approach

> **Start from a TC4xx template project, then port your application logic into it.**
>
> Do **not** attempt to modify a TC3xx project in-place. The infrastructure differences
> (linker scripts, library paths, clock configuration, watchdog APIs) are extensive enough
> that starting from a known-good TC4xx template is faster and less error-prone.

**Steps:**
1. Create a new TC4xx project in AURIX Development Studio using the appropriate device/board template.
2. Copy your application-specific `.c` and `.h` files into the new project.
3. Update peripheral API calls following the migration tables in [Part 3](#part-3-peripheral-api-migration).
4. Verify the `Configurations/Ifx_Cfg.h` and `Boards/board.h` settings match your target hardware.
5. Build, flash, and test.

---

## Part 2: Infrastructure Migration (Generic)

These steps apply to **every** example being migrated, regardless of which peripherals it uses.

---

### 2.1 Project Naming Convention

TC4xx project names include a **board abbreviation** that TC3xx names do not have.

| Generation | Pattern | Example |
|------------|---------|---------|
| **TC3xx** | `iLLD_TC375_ADS_<Name>` | `iLLD_TC375_ADS_ISR_MONITOR` |
| **TC3xx** | `iLLD_TC387_ADS_<Name>` | `iLLD_TC387_ADS_GTM_TOM_3_Phase_Inverter_PWM_2` |
| **TC4xx** | `iLLD_TC4D7_LK_ADS_<Name>` | `iLLD_TC4D7_LK_ADS_ADC_Single_Channel` |
| **TC4xx** | `iLLD_TC4D7_LK_ADS_<Name>` | `iLLD_TC4D7_LK_ADS_EGTM_ATOM_3_Phase_Inverter_PWM_1` |

> `LK` = Lite Kit. Other boards use `COM` (COM TRB), `STD` (Standard TRB), etc.

---

### 2.2 `.ads/install-libraries.json`

This file controls which iLLD zip is installed and which linker configurations are deployed. The TC4xx version is significantly larger due to the many sub-families and new architecture support.

#### Device Map Changes

**TC3xx** (`iLLD_TC375_ADS_ISR_MONITOR/.ads/install-libraries.json`, lines 4–16):

```json
"maps": [
    {"variable": "device", "from": "TC39xXA_B-Step", "to": "TC39B"},
    {"variable": "device", "from": "TC38xQP_A-Step", "to": "TC38A"},
    {"variable": "device", "from": "TC37xTX_A-Step", "to": "TC37AED"},
    {"variable": "device", "from": "TC37xTP_A-Step", "to": "TC37A"},
    {"variable": "device", "from": "TC36xDP_A-Step", "to": "TC36A"},
    {"variable": "device", "from": "TC35xTA_A-Step", "to": "TC35A"},
    {"variable": "device", "from": "TC33xLP_A-Step", "to": "TC33A"},
    {"variable": "device", "from": "TC33xDA_A-Step", "to": "TC33AED"},
    {"variable": "device", "from": "TC32xLP_A-Step", "to": "TC32A"}
]
```

**TC4xx** (`iLLD_TC4D7_LK_ADS_ADC_Single_Channel/.ads/install-libraries.json`, lines 3–60):

```json
"maps": [
    {"variable": "device", "from": "TC4D7XP_A-Step_CC_COM", "to": "TC4DA"},
    {"variable": "device", "from": "TC4D7XE_A-Step_MC_COM", "to": "TC4DA"},
    {"variable": "device", "from": "TC4D7XQ_A-Step_MC_COM", "to": "TC4DA"},
    {"variable": "device", "from": "TC4D9XP_A-Step_CC_COM", "to": "TC4DA"},
    {"variable": "device", "from": "TC4D9XE_A-Step_MC_COM", "to": "TC4DA"},
    {"variable": "device", "from": "TC499PQ_A-Step_MS_STD", "to": "TC49xN"},
    {"variable": "device", "from": "TC497PQ_A-Step_MS_STD", "to": "TC49xN"},
    {"variable": "device", "from": "TC489QP_A-Step_MC_COM", "to": "TC48x"},
    {"variable": "device", "from": "TC487QP_A-Step_MS_STD", "to": "TC48x"},
    {"variable": "device", "from": "TC469QP_A-Step_MS_STD", "to": "TC46x"},
    {"variable": "device", "from": "TC467QP_A-Step_MS_STD", "to": "TC46x"},
    {"variable": "device", "from": "TC457DP_A-Step_MR",     "to": "TC45x"},
    {"variable": "device", "from": "TC447TP_A-Step_MC_COM", "to": "TC44x"},
    ...
]
```

Key observations:
- TC4xx device names include a **suffix** indicating the configuration variant: `CC_COM`, `MC_COM`, `MS_STD`, `MR`.
- TC4xx supports **AB-Step** silicon revisions in addition to A-Step.

#### New Platform Mappings (TC4xx only)

TC4xx introduces `platform` variable mappings that TC3xx does not have:

```json
{"variable": "platform", "from": "KIT_A3G_TC4D7_LITE",    "to": "TC4D7LK"},
{"variable": "platform", "from": "KIT_TC4D9XP_COM_TRB",   "to": "TC4D9COM"},
{"variable": "platform", "from": "KIT_TC4D7XP_COM_TRB",   "to": "TC4D7COM"},
{"variable": "platform", "from": "KIT_TC497_LITE",         "to": "TC497LK"},
{"variable": "platform", "from": "KIT_TC499_STD_TRB",      "to": "TC499STD"},
{"variable": "platform", "from": "KIT_TC497_STD_TRB",      "to": "TC497STD"},
{"variable": "platform", "from": "KIT_TC489QP_COM_TRB",    "to": "NO-IMAGE-BOARD"},
{"variable": "platform", "from": "KIT_TC487QP_COM_TRB",    "to": "NO-IMAGE-BOARD"},
{"variable": "platform", "from": "Custom Board",           "to": "CUSTOM"},
```

#### iLLD Zip Reference Change

```diff
- "from": "iLLDs/Full_Set/iLLD_1_0_1_17_0__TC37A.zip"
+ "from": "iLLDs/Full_Set/iLLD_2_2_0_0_0__TC4DA.zip"
```

Newer TC4xx examples use iLLD 2.3.0:

```json
"from": "iLLDs/Full_Set/iLLD_2_3_0__TC4DA.zip"
```

> Reference: `iLLD_TC4D7_LK_ADS_EGTM_ATOM_ADC_TMADC_Multiple_Channels_1/.ads/install-libraries.json`

#### New Architecture Support (TC4xx)

TC4xx linker configuration commands support three architectures, controlled by the `${architectures}` variable:

| Architecture | Linker Path | Condition |
|-------------|------------|-----------|
| **TriCore** (default) | `Linker_conf/{Toolchain}/${device#remap}/TriCore` | `architectures` does not contain `arc` or `scr` |
| **PPU** | `Linker_conf/{Toolchain}/${device#remap}/PPU` | `architectures` contains `arc` |
| **SCR** | `Linker_conf/{Toolchain}/${device#remap}/SCR` | `architectures` contains `scr` |

TC4xx also adds **LLVM** toolchain support alongside the existing GnuC and Tasking toolchains:

```json
{"type": "CONTENT", "from": "Linker_conf/LLVM/${device#remap}/TriCore", "to": "/", ...}
{"type": "CONTENT", "from": "Linker_conf/LLVM/${device#remap}/PPU", "to": "/", ...}
{"type": "CONTENT", "from": "Linker_conf/LLVM/${device#remap}/SCR", "to": "/", ...}
```

---

### 2.3 `Configurations/Ifx_Cfg.h`

This is the central project configuration header. Nearly every macro name changes between TC3xx and TC4xx.

#### Clock Macro Renaming

**TC3xx** (`iLLD_TC375_ADS_ISR_MONITOR/Configurations/Ifx_Cfg.h`):

```c
/* Configuration for IfxScu_cfg.h */
#define IFX_CFG_SCU_XTAL_FREQUENCY      (20000000)
#define IFX_CFG_SCU_PLL_FREQUENCY       (300000000)
#define IFX_CFG_SCU_PLL1_FREQUENCY      (320000000)
#define IFX_CFG_SCU_PLL2_FREQUENCY      (200000000)
```

**TC4xx** (`iLLD_TC4D7_LK_ADS_ADC_Single_Channel/Configurations/Ifx_Cfg.h`):

```c
#define IFX_BOARD KIT_TC4D7_LITE
#include "board.h"

/* Configuration for IfxClock_cfg.h */
#define IFX_CFG_CLOCK_XTAL_FREQUENCY    (BOARD_CLOCK_XTAL_HZ)
#define IFX_CFG_CLOCK_SYSPLL_FREQUENCY  (500000000)
#define IFX_CFG_CLOCK_PPUPLL_FREQUENCY  (450000000)   /* NEW: PPU PLL */
#define IFX_CFG_CLOCK_PERPLL1_FREQUENCY (160000000)
#define IFX_CFG_CLOCK_PERPLL2_FREQUENCY (200000000)
#define IFX_CFG_CLOCK_PERPLL3_FREQUENCY (200000000)   /* NEW: PLL3 */
```

#### Summary of Clock Macro Changes

```diff
- #define IFX_CFG_SCU_XTAL_FREQUENCY      (20000000)
+ #define IFX_CFG_CLOCK_XTAL_FREQUENCY    (BOARD_CLOCK_XTAL_HZ)

- #define IFX_CFG_SCU_PLL_FREQUENCY       (300000000)
+ #define IFX_CFG_CLOCK_SYSPLL_FREQUENCY  (500000000)

+ #define IFX_CFG_CLOCK_PPUPLL_FREQUENCY  (450000000)   /* NEW */

- #define IFX_CFG_SCU_PLL1_FREQUENCY      (320000000)
+ #define IFX_CFG_CLOCK_PERPLL1_FREQUENCY (160000000)

- #define IFX_CFG_SCU_PLL2_FREQUENCY      (200000000)
+ #define IFX_CFG_CLOCK_PERPLL2_FREQUENCY (200000000)

+ #define IFX_CFG_CLOCK_PERPLL3_FREQUENCY (200000000)   /* NEW */
```

Key changes:
- `SCU` → `CLOCK` in all clock macro names (reflects new clock subsystem)
- `PLL` → `SYSPLL` (System PLL)
- `PLL1` → `PERPLL1`, `PLL2` → `PERPLL2` (Peripheral PLLs)
- **New** `PPUPLL` (PPU co-processor PLL) at 450 MHz
- **New** `PERPLL3` (third peripheral PLL) at 200 MHz
- Crystal frequency now references `BOARD_CLOCK_XTAL_HZ` from `board.h` instead of a hardcoded value
- System PLL increases from **300 MHz** (TC3xx) to **500 MHz** (TC4xx)

#### New Board Include (TC4xx only)

TC4xx adds a board abstraction at the top of `Ifx_Cfg.h`:

```c
#define IFX_BOARD KIT_TC4D7_LITE
#include "board.h"
```

This must appear **before** any clock macros that reference `BOARD_CLOCK_XTAL_HZ`.

#### New CPU Priority Macros (TC4xx)

TC4xx defines interrupt priority macros for all 6 cores:

```c
#define IFX_CFG_CPU0_PRIO               10
#define IFX_CFG_CPU1_PRIO               10
#define IFX_CFG_CPU2_PRIO               10
#define IFX_CFG_CPU3_PRIO               10
#define IFX_CFG_CPU4_PRIO               10
#define IFX_CFG_CPU5_PRIO               10
```

#### New STM Resolution Macro (TC4xx)

```c
#define IFX_STM_RESOULTION              IFX_CFG_CLOCK_SYSPLL_FREQUENCY
#define IFX_CFG_INTERRUPT_INTERVAL      (0.003)
```

---

### 2.4 `Boards/board.h` (New for TC4xx)

TC4xx introduces a **board abstraction layer** that does not exist in TC3xx. This file is located at `Boards/board.h` and **must** be created for every TC4xx project.

> Reference: `iLLD_TC4D7_LK_ADS_ADC_Single_Channel/Boards/board.h`

```c
#ifndef BOARD_H
#define BOARD_H

#define IFX_DEVICE_FAMILY IFX_DEVICE_FAMILY_TC4
#define IFX_DEVICE_SERIES IFX_DEVICE_SERIES_TC4D

#define KIT_TC4D7_LITE              (1)
#define KIT_TC4D9_COM_TRB           (2)
#define KIT_TC4D9_ZONE_GW_BTX_APP   (3)

#if defined(IFX_BOARD)
#if IFX_BOARD == KIT_TC4D7_LITE
#include "KIT_TC4D7_LITE/clock.h"
#define BOARD_PIN_FILE "KIT_TC4D7_LITE/pin.h"
#elif IFX_BOARD == KIT_TC4D9_COM_TRB
#include "KIT_TC4D9_COM_TRB/clock.h"
#define BOARD_PIN_FILE "KIT_TC4D9_COM_TRB/pin.h"
#elif IFX_BOARD == KIT_TC4D9_ZONE_GW_BTX_APP
#include "KIT_TC4D9_ZONE_GW_BTX_APP/clock.h"
#define BOARD_PIN_FILE "KIT_TC4D9_ZONE_GW_BTX_APP/pin.h"
#else
#error("board.h: unknown board selected")
#endif
#endif
#else
#error("board.h: no board selected")
#endif
```

**Required defines:**

| Define | Purpose | Example Value |
|--------|---------|---------------|
| `IFX_DEVICE_FAMILY` | Selects the device family in iLLD | `IFX_DEVICE_FAMILY_TC4` |
| `IFX_DEVICE_SERIES` | Selects the device series within the family | `IFX_DEVICE_SERIES_TC4D` |
| `IFX_BOARD` | Set in `Ifx_Cfg.h`; selects board-specific clock/pin configs | `KIT_TC4D7_LITE` |

Each board ID maps to a subdirectory containing `clock.h` (which defines `BOARD_CLOCK_XTAL_HZ`) and `pin.h`.

> **TC3xx has no equivalent.** Board-specific configuration in TC3xx is handled entirely through hardcoded values in `Ifx_Cfg.h`.

---

### 2.5 Linker Script Changes

The linker script undergoes substantial changes to accommodate the new memory map, additional cores, and larger flash/RAM regions.

#### File Name Change

```diff
- Lcf_Gnuc_Tricore_Tc.lsl    (TC3xx, GNU C compiler)
+ Lcf_Gcc_Tricore_Tc.lsl      (TC4xx, GCC compiler)
```

> Note the rename from `Gnuc` to `Gcc`.

#### Derivative Memory Map

```diff
- __TRICORE_DERIVATE_MEMORY_MAP__ = 0x380;   /* TC375 / TC387 */
+ __TRICORE_DERIVATE_MEMORY_MAP__ = 0x4D0;   /* TC4D7 */
```

#### Core Count and Stack/CSA Definitions

**TC375** (3 cores: CPU0–CPU2):

```
LCF_CSA0_SIZE = 8k; LCF_USTACK0_SIZE = 2k; LCF_ISTACK0_SIZE = 1k;
LCF_CSA1_SIZE = 8k; LCF_USTACK1_SIZE = 2k; LCF_ISTACK1_SIZE = 1k;
LCF_CSA2_SIZE = 8k; LCF_USTACK2_SIZE = 2k; LCF_ISTACK2_SIZE = 1k;
```

**TC387** (4 cores: CPU0–CPU3): adds `LCF_CSA3_SIZE`, `LCF_USTACK3_SIZE`, `LCF_ISTACK3_SIZE`.

**TC4D7** (6 cores: CPU0–CPU5): adds definitions through CPU5:

```
LCF_CSA0_SIZE = 8k; ... through ... LCF_CSA5_SIZE = 8k;
LCF_USTACK0_SIZE = 2k; ... through ... LCF_USTACK5_SIZE = 2k;
LCF_ISTACK0_SIZE = 1k; ... through ... LCF_ISTACK5_SIZE = 1k;
```

#### DSPR (Data Scratchpad RAM) Sizes

| Core | TC375 | TC387 | TC4D7 |
|------|-------|-------|-------|
| DSPR0 | 240K @ `0x70000000` | 240K @ `0x70000000` | 240K @ `0x70000000` |
| DSPR1 | 240K @ `0x60000000` | 240K @ `0x60000000` | 240K @ `0x60000000` |
| DSPR2 | 96K @ `0x50000000` | 96K @ `0x50000000` | 240K @ `0x50000000` |
| DSPR3 | — | 96K @ `0x40000000` | 240K @ `0x40000000` |
| DSPR4 | — | — | 240K @ `0x30000000` |
| DSPR5 | — | — | 240K @ `0x20000000` |

> Note: TC4D7 gives **all** cores 240K DSPR, whereas TC375/TC387 give smaller cores only 96K.

#### Interrupt Vector Table Addresses

| Core | TC375 | TC387 | TC4D7 |
|------|-------|-------|-------|
| INTVEC0 | `0x802FE000` | `0x802FE000` | `0x803FE000` |
| INTVEC1 | `0x805FC000` | `0x805FE000` | `0x807FE000` |
| INTVEC2 | `0x805FE000` | `0x808FE000` | `0x809FE000` |
| INTVEC3 | — | `0x809FE000` | `0x80DFE000` |
| INTVEC4 | — | — | `0x811FE000` |
| INTVEC5 | — | — | `0x813FE000` |

#### Trap Vector and Start Pointer Addresses (TC4D7)

```
LCF_TRAPVEC0_START = 0x80000100;
LCF_TRAPVEC1_START = 0x80400100;
LCF_TRAPVEC2_START = 0x80800100;
LCF_TRAPVEC3_START = 0x80A00100;
LCF_TRAPVEC4_START = 0x80E00100;
LCF_TRAPVEC5_START = 0x81200100;

LCF_STARTPTR_CPU0 = 0x80000000;
LCF_STARTPTR_CPU1 = 0x80400000;
LCF_STARTPTR_CPU2 = 0x80800000;
LCF_STARTPTR_CPU3 = 0x80A00000;
LCF_STARTPTR_CPU4 = 0x80E00000;
LCF_STARTPTR_CPU5 = 0x81200000;
```

#### Flash Memory Layout (TC4D7)

TC4D7 has **6 program flash banks** (pfls0–pfls5), compared to TC375's 2 (pfls0–pfls1) and TC387's 4 (pfls0–pfls3):

```
pfls0 (rx!p): org = 0x80000000, len = 4M
pfls1 (rx!p): org = 0x80400000, len = 4M
pfls2 (rx!p): org = 0x80800000, len = 2M
pfls3 (rx!p): org = 0x80A00000, len = 4M
pfls4 (rx!p): org = 0x80E00000, len = 4M
pfls5 (rx!p): org = 0x81200000, len = 2M
```

#### DLMU Memory (TC4D7)

TC4D7 provides **512K** DLMU per core (vs 64K on TC3xx), with a shared LMU RAM region:

```
cpu0_dlmu (w!xp): org = 0x90000000, len = 512K
cpu1_dlmu (w!xp): org = 0x90080000, len = 512K
...
cpu5_dlmu (w!xp): org = 0x90280000, len = 512K
lmuram   (w!xp): org = 0x90400000, len = 5M
```

> **Important:** The linker script memory map values are **device-specific** and must be adjusted when targeting different TC4xx sub-families. Consult the device datasheet for exact values.

---

### 2.6 `Cpu0_Main.c` Boilerplate Changes

The main entry point has several systematic changes.

#### Before (TC3xx)

> Reference: `iLLD_TC387_ADS_GTM_TOM_3_Phase_Inverter_PWM_2/Cpu0_Main.c`

```c
#include "Ifx_Types.h"
#include "IfxCpu.h"
#include "IfxScuWdt.h"
#include "Bsp.h"
#include "GTM_TOM_3_Phase_Inverter_PWM.h"

#define WAIT_TIME   10

IfxCpu_syncEvent g_cpuSyncEvent = 0;

int core0_main(void)
{
    IfxCpu_enableInterrupts();

    IfxScuWdt_disableCpuWatchdog(IfxScuWdt_getCpuWatchdogPassword());
    IfxScuWdt_disableSafetyWatchdog(IfxScuWdt_getSafetyWatchdogPassword());

    IfxCpu_emitEvent(&g_cpuSyncEvent);
    IfxCpu_waitEvent(&g_cpuSyncEvent, 1);

    Ifx_TickTime ticksFor10ms = IfxStm_getTicksFromMilliseconds(BSP_DEFAULT_TIMER, WAIT_TIME);

    initGtmTomPwm();

    while(1)
    {
        updateGtmTomPwmDutyCycles();
        waitTime(ticksFor10ms);
    }
    return (1);
}
```

#### After (TC4xx)

> Reference: `iLLD_TC4D7_LK_ADS_EGTM_ATOM_3_Phase_Inverter_PWM_1/Cpu0_Main.c`

```c
#include "EGTM_ATOM_3_Phase_Inverter_PWM.h"
#include "Ifx_Types.h"
#include "Ifx_Cfg.h"
#include "IfxCpu.h"
#include "IfxWtu.h"
#include "Bsp.h"

#define WAIT_TIME   500

IFX_ALIGN(4) IfxCpu_syncEvent g_cpuSyncEvent = 0;

void core0_main(void)
{
    IfxCpu_enableInterrupts();

    IfxWtu_disableCpuWatchdog(IfxWtu_getCpuWatchdogPassword());
    IfxWtu_disableSystemWatchdog(IfxWtu_getSystemWatchdogPassword());

    IfxCpu_emitEvent(&g_cpuSyncEvent);
    IfxCpu_waitEvent(&g_cpuSyncEvent, 1);

    Ifx_TickTime ticksFor500ms = IfxStm_getTicksFromMilliseconds(WAIT_TIME);

    initEgtmAtom3phInv();

    while(1)
    {
        updateEgtmAtom3phInvDuty();
        waitTime(ticksFor500ms);
    }
}
```

#### Detailed Change Summary

| Change | TC3xx | TC4xx |
|--------|-------|-------|
| **Watchdog header** | `#include "IfxScuWdt.h"` | `#include "IfxWtu.h"` |
| **Config header** | (not included) | `#include "Ifx_Cfg.h"` |
| **CPU watchdog disable** | `IfxScuWdt_disableCpuWatchdog(IfxScuWdt_getCpuWatchdogPassword())` | `IfxWtu_disableCpuWatchdog(IfxWtu_getCpuWatchdogPassword())` |
| **Safety/System watchdog** | `IfxScuWdt_disableSafetyWatchdog(IfxScuWdt_getSafetyWatchdogPassword())` | `IfxWtu_disableSystemWatchdog(IfxWtu_getSystemWatchdogPassword())` |
| **Return type** | `int core0_main(void)` | `void core0_main(void)` |
| **Return statement** | `return (1);` | (removed) |
| **STM tick API** | `IfxStm_getTicksFromMilliseconds(BSP_DEFAULT_TIMER, WAIT_TIME)` | `IfxStm_getTicksFromMilliseconds(WAIT_TIME)` |
| **Sync event alignment** | `IfxCpu_syncEvent g_cpuSyncEvent = 0;` | `IFX_ALIGN(4) IfxCpu_syncEvent g_cpuSyncEvent = 0;` |

> **Key rename:** `Safety` watchdog → `System` watchdog. This reflects a terminology change in the TC4xx hardware.

> **Signature change:** `IfxStm_getTicksFromMilliseconds` no longer takes `BSP_DEFAULT_TIMER` as the first parameter in iLLD v2.x.

---

### 2.7 Additional `CpuX_Main.c` Files

TC3xx and TC4xx both require a `CpuX_Main.c` file for each available core. The number of files increases with core count:

| Device | Files Required |
|--------|---------------|
| TC375 (3 cores) | `Cpu0_Main.c`, `Cpu1_Main.c`, `Cpu2_Main.c` |
| TC387 (4 cores) | `Cpu0_Main.c`, `Cpu1_Main.c`, `Cpu2_Main.c`, `Cpu3_Main.c` |
| TC4D7 (6 cores) | `Cpu0_Main.c`, `Cpu1_Main.c`, `Cpu2_Main.c`, `Cpu3_Main.c`, `Cpu4_Main.c`, `Cpu5_Main.c` |

Each secondary `CpuX_Main.c` (X ≥ 1) follows the same boilerplate pattern: enable interrupts, disable the CPU watchdog (using `IfxWtu` on TC4xx), wait for the sync event, then enter an infinite loop.

When migrating from TC375 to TC4D7, you must **create** `Cpu3_Main.c`, `Cpu4_Main.c`, and `Cpu5_Main.c` (or copy them from a TC4xx template project).

---

### 2.8 `.cproject` Changes

The Eclipse/ADS `.cproject` file contains build configuration that must be updated.

#### CPU Derivative Value

```diff
- value="com.infineon.aurix.buildsystem.managed.gcc.c.option.mcpu.tc37x"
+ value="com.infineon.aurix.buildsystem.managed.gcc.c.option.mcpu.tc4dax"
```

> Reference: `iLLD_TC4D7_LK_ADS_ONEEYE_DAS_QUICKSTART/.cproject`, line 29

#### Include Paths

All library include paths change from TC3xx-specific paths to TC4xx paths:

```diff
- Libraries/iLLD/TC37A/CpuGeneric
- Libraries/iLLD/TC37A/Tricore
+ Libraries/iLLD/TC4xx/CpuGeneric
+ Libraries/iLLD/TC4xx/Tricore
```

Note that TC4xx uses a **generic** `TC4xx` path rather than a device-specific path like `TC37A`.

#### SFR Include Paths

```diff
- Libraries/Infra/Sfr/TC37A
+ Libraries/Infra/Sfr/TC4Dx
```

#### SSW Include Paths

```diff
- Libraries/Infra/Ssw/TC37A
+ Libraries/Infra/Ssw/TC4xx/Tricore
```

#### Build Booster Library Roots

```diff
- <path>/Libraries/iLLD/TC37A/CpuGeneric</path>
- <path>/Libraries/iLLD/TC37A/Tricore</path>
+ <path>/Libraries/iLLD/TC4xx/CpuGeneric</path>
+ <path>/Libraries/iLLD/TC4xx/Tricore</path>
```

> **Tip:** When using AURIX Development Studio, creating a new TC4xx project from a template will generate a correct `.cproject` file automatically. Manual editing is only needed if you are migrating the project file in-place.

---

## Part 3: Peripheral API Migration

This section covers the API changes for specific peripherals. Each subsection shows the TC3xx → TC4xx mapping with real code from the repository.

---

### 3.1 GTM TOM → EGTM ATOM (Timer/PWM)

The TC3xx **Generic Timer Module (GTM)** is replaced by the **Enhanced Generic Timer Module (EGTM)** in TC4xx. The iLLD v2.x provides a unified `IfxEgtm_Pwm_*` API that replaces the older `IfxGtm_Tom_PwmHl_*` API.

**Matched pair:**
- TC3xx: `iLLD_TC387_ADS_GTM_TOM_3_Phase_Inverter_PWM_2/GTM_TOM_3_Phase_Inverter_PWM.c`
- TC4xx: `iLLD_TC4D7_LK_ADS_EGTM_ATOM_3_Phase_Inverter_PWM_1/EGTM_ATOM_3_Phase_Inverter_PWM.c`

#### Include Changes

```diff
- #include "IfxGtm_Tom_PwmHl.h"
- #include "IfxCpu_Irq.h"
- #include "IfxGtm_cfg_TC38x.h"
+ #include "IfxEgtm_Pwm.h"
+ #include "IfxPort.h"
+ #include "IfxPort_Pinmap.h"
```

#### Module Reference

```diff
- IfxGtm_enable(&MODULE_GTM);
+ IfxEgtm_enable(&MODULE_EGTM);

- IfxGtm_Cmu_setGclkFrequency(&MODULE_GTM, ...);
+ IfxEgtm_Cmu_setGclkFrequency(&MODULE_EGTM, ...);

- IfxGtm_Cmu_setClkFrequency(&MODULE_GTM, IfxGtm_Cmu_Clk_0, ...);
+ IfxEgtm_Cmu_setClkFrequency(&MODULE_EGTM, IfxEgtm_Cmu_Clk_0, ...);

- IfxGtm_Cmu_enableClocks(&MODULE_GTM, IFXGTM_CMU_CLKEN_FXCLK);
+ IfxEgtm_Cmu_enableClocks(&MODULE_EGTM, IFXEGTM_CMU_CLKEN_CLK0);
```

#### Type/Function Prefix Changes

| TC3xx (iLLD v1.x) | TC4xx (iLLD v2.x) |
|---|---|
| `IfxGtm_Tom_Timer` | (no direct equivalent — use `IfxEgtm_Pwm`) |
| `IfxGtm_Tom_PwmHl` | `IfxEgtm_Pwm` |
| `IfxGtm_Tom_PwmHl_Config` | `IfxEgtm_Pwm_Config` |
| `IfxGtm_Tom_ToutMapP` | `IfxEgtm_Pwm_ToutMap*` |
| `IfxGtm_Tom_PwmHl_init()` | `IfxEgtm_Pwm_init()` |
| `IfxGtm_Tom_PwmHl_initConfig()` | `IfxEgtm_Pwm_initConfig()` |
| `IfxGtm_Tom_PwmHl_setMode()` | (set via `config.alignment`) |
| `IfxGtm_Tom_PwmHl_setOnTime()` | `IfxEgtm_Pwm_updateChannelsDutyImmediate()` |
| `IfxGtm_Tom_Timer_run()` | (set via `config.syncStart = TRUE`) |
| `IfxGtm_Tom_Timer_disableUpdate()` | (handled internally) |
| `IfxGtm_Tom_Timer_applyUpdate()` | (handled internally) |

#### New TC4xx Configuration Types

The TC4xx unified PWM API introduces structured configuration types:

```c
IfxEgtm_Pwm_Config config;                               /* Main PWM config              */
IfxEgtm_Pwm_ChannelConfig channelConfig[NUM_OF_CHANNELS]; /* Per-channel configuration    */
IfxEgtm_Pwm_DtmConfig dtmConfig[NUM_OF_CHANNELS];         /* Dead-time configuration      */
IfxEgtm_Pwm_InterruptConfig interruptConfig;              /* Interrupt configuration      */
IfxEgtm_Pwm_OutputConfig output[NUM_OF_CHANNELS];         /* Output pin configuration     */
```

#### Pin Macro Changes

```diff
- #define PHASE_U_HS  &IfxGtm_TOM1_2_TOUT12_P00_3_OUT
+ #define PHASE_U_HS  &IfxEgtm_ATOM0_0_TOUT64_P20_8_OUT

- #define PHASE_U_LS  &IfxGtm_TOM1_1_TOUT11_P00_2_OUT
+ #define PHASE_U_LS  &IfxEgtm_ATOM0_0N_TOUT65_P20_9_OUT
```

> Pin assignments are board-specific and must be updated according to the TC4xx board pinout.

#### New VM ID Field (TC4xx)

TC4xx interrupt configuration requires a Virtual Machine ID:

```c
interruptConfig.mode        = IfxEgtm_IrqMode_pulseNotify;
interruptConfig.isrProvider = IfxSrc_Tos_cpu0;
interruptConfig.priority    = ISR_PRIORITY_ATOM;
interruptConfig.vmId        = IfxSrc_VmId_0;               /* NEW: VM ID */
```

#### Duty Cycle Update API

**TC3xx** (low-level timer control):

```c
IfxGtm_Tom_Timer_disableUpdate(&g_pwm3PhaseOutput.timer);
IfxGtm_Tom_PwmHl_setOnTime(&g_pwm3PhaseOutput.pwm, g_pwm3PhaseOutput.pwmOnTimes);
IfxGtm_Tom_Timer_applyUpdate(&g_pwm3PhaseOutput.timer);
```

**TC4xx** (unified API, single call):

```c
IfxEgtm_Pwm_updateChannelsDutyImmediate(&g_egtmAtom3phInv.pwm, (float32*)g_egtmAtom3phInv.dutyCycles);
```

> The TC4xx API uses **percentage-based duty cycles** (`float32`, range 0.0–100.0) rather than tick-based on-times (`Ifx_TimerValue`).

#### Architecture Comparison

| Aspect | TC3xx GTM TOM PwmHl | TC4xx EGTM Pwm |
|--------|-------------------|-----------------|
| Timer & PWM | Separate `Timer` + `PwmHl` objects | Single unified `IfxEgtm_Pwm` object |
| Configuration | Two-step: init timer, then init PwmHl | Single-step: one `IfxEgtm_Pwm_init()` call |
| Dead-time | Set via `pwmHlConfig.base.deadtime` (float seconds) | Set via `IfxEgtm_Pwm_DtmConfig` per channel (rising/falling) |
| Duty update | Manual disable/set/apply sequence | `IfxEgtm_Pwm_updateChannelsDutyImmediate()` |
| Alignment | Set via `IfxGtm_Tom_PwmHl_setMode()` | Set via `config.alignment = IfxEgtm_Pwm_Alignment_center` |
| Start | `IfxGtm_Tom_Timer_run()` | `config.syncStart = TRUE` |

---

### 3.2 EVADC → ADC / TMADC

TC3xx uses the **Enhanced Versatile Analog-to-Digital Converter (EVADC)** module. TC4xx replaces this with a new **ADC** module and introduces the **TMADC** (Time-Multiplexed ADC) for certain use cases.

**TC4xx ADC examples in this repo:**
- `iLLD_TC4D7_LK_ADS_ADC_Single_Channel/`
- `iLLD_TC4D7_LK_ADS_TMADC_Single_Channel/`
- `iLLD_TC4D7_LK_ADS_EGTM_ATOM_ADC_TMADC_Multiple_Channels_1/`
- `iLLD_TC4D7_LK_ADC_CDSP_TMADC_Filtering/`

**Key changes:**
- The EVADC peripheral does not exist on TC4xx — all `IfxEvadc_*` APIs must be replaced.
- TC4xx ADC examples use a different initialization pattern; refer to the TC4xx template projects.
- GTM trigger connections (`IfxGtm_Trig_toEVadc`) are replaced by EGTM-based trigger connections.
- The TC4xx TMADC module provides time-multiplexed conversion that has no direct TC3xx equivalent.

> **Recommendation:** For ADC migration, start from the `iLLD_TC4D7_LK_ADS_ADC_Single_Channel` example and adapt the channel configuration and trigger setup to your application's requirements.

---

### 3.3 OneEye Integration

OneEye DAS (Direct Access Service) integration requires additional configuration macros on TC4xx.

**Matched pair:**
- TC3xx: `OneEye_DAS_QuickStart_1_KIT_TC375_LK/`
- TC4xx: `iLLD_TC4D7_LK_ADS_ONEEYE_DAS_QUICKSTART/`

#### `Ifx_Cfg.h` Changes for OneEye

**TC3xx** (`OneEye_DAS_QuickStart_1_KIT_TC375_LK/Configurations/Ifx_Cfg.h`):

```c
#define DEVICE_TC37X                    1
#define IFX_PIN_PACKAGE_LQFP176         1

#define IFX_CFG_OE_AL_UC IFX_CFG_OE_AL_UC_AURIX_ILLD
#define IFX_CFG_OE_AL_UC_VARIANT IFX_CFG_OE_AL_UC_VARIANT_NONE
```

**TC4xx** (`iLLD_TC4D7_LK_ADS_ONEEYE_DAS_ALLINONE/Configurations/Ifx_Cfg.h`, lines 64–80):

```c
#define IFX_CFG_OE_AL_UC IFX_CFG_OE_AL_UC_AURIX_ILLD
#define DEVICE_TC4DX

#define IFX_CFG_OE_AL_UC_VARIANT IFX_CFG_OE_AL_UC_VARIANT_AURIX_ILLD_TC4
```

#### OneEye Migration Summary

```diff
- #define DEVICE_TC37X                    1
+ #define DEVICE_TC4DX

- #define IFX_CFG_OE_AL_UC_VARIANT IFX_CFG_OE_AL_UC_VARIANT_NONE
+ #define IFX_CFG_OE_AL_UC_VARIANT IFX_CFG_OE_AL_UC_VARIANT_AURIX_ILLD_TC4
```

| Setting | TC3xx | TC4xx |
|---------|-------|-------|
| Device macro | `DEVICE_TC37X` (value: `1`) | `DEVICE_TC4DX` (no value) |
| UC variant | `IFX_CFG_OE_AL_UC_VARIANT_NONE` | `IFX_CFG_OE_AL_UC_VARIANT_AURIX_ILLD_TC4` |

> The TC4xx OneEye configuration also supports optional pin-package defines for larger packages:
> ```c
> /* #define IFX_PIN_PACKAGE_LFBGA436_COM */  /* TC499 COM */
> /* #define IFX_PIN_PACKAGE_LFBGA292_COM */  /* TC497 COM */
> ```

---

## Part 4: TC4xx Sub-Family Variant Table

The following table summarizes the TC4xx sub-families supported in the `install-libraries.json` files. Use this as a reference when targeting a specific device.

| Sub-family | Remap Name | iLLD Zip (v2.2.0) | iLLD Zip (v2.3.0) | Devices | Configuration Variants |
|------------|-----------|--------------------|--------------------|---------|----------------------|
| **TC4Dx** | `TC4DA` | `iLLD_2_2_0_0_0__TC4DA.zip` | `iLLD_2_3_0__TC4DA.zip` | TC4D7, TC4D9 | CC_COM, MC_COM |
| **TC4Zx** | `TC4Zx` | — | — | TC4Z7, TC4Z9 | MC_COM |
| **TC49x** | `TC49xN` | `iLLD_2_2_0_0_0__TC49xN.zip` | `iLLD_2_3_0__TC49xN.zip` | TC499, TC497 | MS_STD |
| **TC48x** | `TC48x` | `iLLD_2_2_0_0_0__TC48x.zip` | `iLLD_2_3_0__TC48x.zip` | TC489, TC487, TC486 | MC_COM, MS_STD |
| **TC46x** | `TC46x` | `iLLD_2_2_0_0_0__TC46x.zip` | `iLLD_2_3_0__TC46x.zip` | TC469, TC467, TC466 | MS_STD |
| **TC45x** | `TC45x` | `iLLD_2_2_0_0_0__TC45x.zip` | `iLLD_2_3_0__TC45x.zip` | TC457 | MR |
| **TC44x** | `TC44x` | — | (from EGTM example) | TC447, TC446, TC445 | MC_COM, MS_STD |

**Configuration Variant Key:**

| Abbreviation | Meaning |
|-------------|---------|
| **CC_COM** | Connectivity Controller, Communication variant |
| **MC_COM** | Micro Controller, Communication variant |
| **MS_STD** | Micro Controller, Standard variant |
| **MR** | Micro Controller, Reduced variant |

> **Important:** The linker script memory map (`__TRICORE_DERIVATE_MEMORY_MAP__`, DSPR sizes, flash bank layout, interrupt vector addresses) must be adjusted per sub-family. The values documented in [Section 2.5](#25-linker-script-changes) are specific to TC4Dx (`0x4D0`). Consult the Infineon device datasheet for other sub-families.

---

## Part 5: Migration Checklist

Use this checklist to verify that all migration steps are complete.

### Project Setup

- [ ] Created a new TC4xx project from ADS template (or adapted naming: `iLLD_<DEVICE>_<BOARD>_ADS_<Name>`)
- [ ] Updated `.ads/install-libraries.json` with TC4xx device maps and iLLD v2.x zip references
- [ ] Added platform mappings to `.ads/install-libraries.json` if targeting a specific board

### Configuration Files

- [ ] Created `Boards/board.h` with `IFX_DEVICE_FAMILY`, `IFX_DEVICE_SERIES`, and board-specific clock/pin includes
- [ ] Updated `Configurations/Ifx_Cfg.h`:
  - [ ] Added `#define IFX_BOARD <board_name>` and `#include "board.h"` at the top
  - [ ] Renamed `IFX_CFG_SCU_XTAL_FREQUENCY` → `IFX_CFG_CLOCK_XTAL_FREQUENCY` (using `BOARD_CLOCK_XTAL_HZ`)
  - [ ] Renamed `IFX_CFG_SCU_PLL_FREQUENCY` → `IFX_CFG_CLOCK_SYSPLL_FREQUENCY` (updated to 500 MHz)
  - [ ] Renamed `IFX_CFG_SCU_PLL1_FREQUENCY` → `IFX_CFG_CLOCK_PERPLL1_FREQUENCY`
  - [ ] Renamed `IFX_CFG_SCU_PLL2_FREQUENCY` → `IFX_CFG_CLOCK_PERPLL2_FREQUENCY`
  - [ ] Added `IFX_CFG_CLOCK_PPUPLL_FREQUENCY` (450 MHz)
  - [ ] Added `IFX_CFG_CLOCK_PERPLL3_FREQUENCY` (200 MHz)
  - [ ] Added CPU priority macros for all 6 cores (`IFX_CFG_CPU0_PRIO` through `IFX_CFG_CPU5_PRIO`)

### Linker Script

- [ ] Updated `__TRICORE_DERIVATE_MEMORY_MAP__` for target device (e.g., `0x4D0` for TC4D7)
- [ ] Added stack/CSA definitions for cores 3–5 (if migrating from TC375)
- [ ] Updated DSPR sizes and addresses for all cores
- [ ] Updated interrupt vector table addresses (`LCF_INTVEC0_START` through `LCF_INTVEC5_START`)
- [ ] Updated trap vector addresses and start pointers for all cores
- [ ] Updated flash memory bank definitions (pfls0–pfls5)
- [ ] Updated DLMU addresses and sizes
- [ ] Renamed linker script file from `Lcf_Gnuc_Tricore_Tc.lsl` to `Lcf_Gcc_Tricore_Tc.lsl` if using GCC

### Source Code

- [ ] Updated `Cpu0_Main.c`:
  - [ ] Changed `#include "IfxScuWdt.h"` → `#include "IfxWtu.h"`
  - [ ] Added `#include "Ifx_Cfg.h"`
  - [ ] Changed `IfxScuWdt_disableCpuWatchdog(...)` → `IfxWtu_disableCpuWatchdog(...)`
  - [ ] Changed `IfxScuWdt_disableSafetyWatchdog(...)` → `IfxWtu_disableSystemWatchdog(...)`
  - [ ] Changed return type from `int core0_main(void)` to `void core0_main(void)`
  - [ ] Removed `return (1);`
  - [ ] Changed `IfxStm_getTicksFromMilliseconds(BSP_DEFAULT_TIMER, ms)` → `IfxStm_getTicksFromMilliseconds(ms)`
  - [ ] Added `IFX_ALIGN(4)` to `g_cpuSyncEvent` declaration
- [ ] Created `Cpu3_Main.c`, `Cpu4_Main.c`, `Cpu5_Main.c` (if not present)
- [ ] Applied same watchdog/return-type changes to all `CpuX_Main.c` files

### Peripheral APIs (as applicable)

- [ ] Replaced `IfxGtm_*` with `IfxEgtm_*` (GTM → EGTM)
- [ ] Replaced `MODULE_GTM` with `MODULE_EGTM`
- [ ] Replaced `IfxGtm_Tom_PwmHl_*` API with unified `IfxEgtm_Pwm_*` API
- [ ] Added `vmId = IfxSrc_VmId_0` to all interrupt configurations
- [ ] Replaced EVADC APIs with TC4xx ADC/TMADC APIs
- [ ] Updated GTM trigger connections to EGTM equivalents
- [ ] Updated OneEye macros (`DEVICE_TC4DX`, `IFX_CFG_OE_AL_UC_VARIANT_AURIX_ILLD_TC4`)

### Build Configuration

- [ ] Updated `.cproject` CPU derivative (e.g., `tc37x` → `tc4dax`)
- [ ] Updated all include paths from `TC37A`/`TC38A` → `TC4xx` and `TC4Dx`
- [ ] Verified build completes without errors in AURIX Development Studio

---

## Appendix: Reference Files

The following files from this repository were used to derive the migration steps in this guide:

| Section | TC3xx Reference | TC4xx Reference |
|---------|----------------|-----------------|
| install-libraries.json | `iLLD_TC375_ADS_ISR_MONITOR/.ads/install-libraries.json` | `iLLD_TC4D7_LK_ADS_ADC_Single_Channel/.ads/install-libraries.json` |
| install-libraries.json (v2.3) | — | `iLLD_TC4D7_LK_ADS_EGTM_ATOM_ADC_TMADC_Multiple_Channels_1/.ads/install-libraries.json` |
| Ifx_Cfg.h | `iLLD_TC375_ADS_ISR_MONITOR/Configurations/Ifx_Cfg.h` | `iLLD_TC4D7_LK_ADS_ADC_Single_Channel/Configurations/Ifx_Cfg.h` |
| board.h | (none) | `iLLD_TC4D7_LK_ADS_ADC_Single_Channel/Boards/board.h` |
| Linker script (TC375) | `iLLD_TC375_ADS_ISR_MONITOR/Lcf_Gnuc_Tricore_Tc.lsl` | — |
| Linker script (TC387) | `iLLD_TC387_ADS_GTM_TOM_3_Phase_Inverter_PWM_2/Lcf_Gnuc_Tricore_Tc.lsl` | — |
| Linker script (TC4D7) | — | `iLLD_TC4D7_LK_ADS_ADC_Single_Channel/Lcf_Gcc_Tricore_Tc.lsl` |
| Cpu0_Main.c | `iLLD_TC387_ADS_GTM_TOM_3_Phase_Inverter_PWM_2/Cpu0_Main.c` | `iLLD_TC4D7_LK_ADS_EGTM_ATOM_3_Phase_Inverter_PWM_1/Cpu0_Main.c` |
| GTM/EGTM PWM | `iLLD_TC387_ADS_GTM_TOM_3_Phase_Inverter_PWM_2/GTM_TOM_3_Phase_Inverter_PWM.c` | `iLLD_TC4D7_LK_ADS_EGTM_ATOM_3_Phase_Inverter_PWM_1/EGTM_ATOM_3_Phase_Inverter_PWM.c` |
| OneEye (TC3xx) | `OneEye_DAS_QuickStart_1_KIT_TC375_LK/Configurations/Ifx_Cfg.h` | — |
| OneEye (TC4xx) | — | `iLLD_TC4D7_LK_ADS_ONEEYE_DAS_ALLINONE/Configurations/Ifx_Cfg.h` |
| .cproject | — | `iLLD_TC4D7_LK_ADS_ONEEYE_DAS_QUICKSTART/.cproject` |

---

*This guide was generated from the actual code examples in the [COG-GTM/AURIX_code_examples](https://github.com/COG-GTM/AURIX_code_examples) repository. All code snippets are derived from real files — no code was invented.*
