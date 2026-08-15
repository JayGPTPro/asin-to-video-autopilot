# ASIN to Video Autopilot

A Claude Code skill. One Amazon ASIN in, a finished 30-second listing video out:
cinematic footage, sound design, music, voiceover and animated text overlays.
Zero questions during the run, one cost cap you set once.

Typical cost per video: **9-12 USD** of Genrupt credits. The cap in `config.json`
stops a run before it can ever exceed what you allowed.

## Install

```bash
npx skills add JayGPTPro/asin-to-video-autopilot -g
```

Then, in Claude Code:

```
Run the asin-to-video-autopilot environment check
```

Anything missing is printed with the exact fix. Tell Claude to fix it.

## Requirements

You provide two things:

- **Claude Code** (desktop app or CLI)
- **A Genrupt account with credits** — rendering (Seedance 2.5), listing scraping,
  music and voiceover. Connect the Genrupt MCP to Claude from Genrupt's settings.

The skill also uses free tools on your machine — ffmpeg, Node 18+ (for the overlay
renderer via npx), Python 3 with pillow + numpy, and whisper-cpp with a `base.en`
model. Claude installs these for you; `setup/check-env.sh` verifies them.

## Use

```
/asin-to-video-autopilot B0XXXXXXXXX
```

First run creates `config.json` and asks once for your cost cap (default 20 USD).
After that the run is autonomous: it reports each expense as it happens and stops
only if an action would cross the cap.

## What ships in this skill

| Path | Owns |
|---|---|
| `SKILL.md` | The run flow, money contract, stage map |
| `references/taste.md` | Every creative decision rule, measured on paid renders |
| `references/seedance25-rules.md` | Prompt grammar: end states, reference roles, camera, density |
| `references/genrupt-flow.md` | Exact MCP calls, live pricing, traps, audio doctrine, edit recipes |
| `references/overlay-grammar.md` | The text system: house register, choreography, dead space |
| `scripts/compose.py` | Brief + shot plan → one master prompt |
| `scripts/lint.py` | Hard gate before any credit moves |
| `scripts/prep_refs.py` | Reference plates: crops, people screening, legal aspect ratios |
| `scripts/qa.py` | Measured QA: mood bands, motion, end states, cut timing |
| `scripts/report.py` | The per-run HTML decision report |
| `examples/dry-run/` | A complete worked brief and shot plan, zero cost |

## Scope of version one

Amazon listing videos: 1280x720 (16:9), 27-30 seconds, English voiceover.
9:16 social cuts, PPC and UGC formats come later.

---

© Jay GPT Pro. All rights reserved. Licensed for use by the purchaser;
not for redistribution or resale.
