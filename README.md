# ASIN to Video Autopilot

A Claude Code skill. One Amazon ASIN in, a finished 30-second listing video out:
cinematic footage, sound design, music, voiceover and animated text overlays.
Zero questions during the run, one cost cap you set once.

Each run spends Genrupt credits on the renders and the audio. You set a spending cap
once, and the run stops before it can ever exceed what you allowed.

## Install

```bash
npx skills add https://jaygptpro.com/video-autopilot/asin-to-video-autopilot.zip -g -a claude-code
```

Run the same line again whenever there is a new version. Then quit and reopen Claude
Code, because skills are only picked up on a fresh start.

Then, in Claude Code:

```
Run the asin-to-video-autopilot environment check
```

Anything missing is printed with the exact fix. Tell Claude to fix it.

## Requirements

You provide two things:

- **Claude Code** (desktop app or CLI)
- **A Genrupt account with credits** for rendering (Seedance 2.5), listing scraping,
  music and voiceover. Add Genrupt as an MCP connector pointed at
  `https://genrupt.com/api/agent/mcp`, or run
  `claude mcp add --transport http --scope user genrupt https://genrupt.com/api/agent/mcp`.
  Full setup guide: https://jaygptpro.com/video-autopilot/

The skill also uses free tools on your machine — ffmpeg, Node 18+ (for the overlay
renderer via npx), Python 3 with pillow + numpy, and whisper-cpp with a `base.en`
model. Claude installs these for you; `setup/check-env.sh` verifies them.

## Use

```
/asin-to-video-autopilot B0XXXXXXXXX
```

First run creates `config.json` and asks once for the spending cap you want per video.
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

Amazon listing videos: 1280x720 (16:9), 30 seconds, English voiceover.
9:16 social cuts, PPC and UGC formats come later.

---

© Jay GPT Pro. All rights reserved. Licensed to the individual it was shared with,
for their own use. Not for redistribution or resale.
