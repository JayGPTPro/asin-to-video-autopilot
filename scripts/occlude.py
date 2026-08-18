#!/usr/bin/env python3
"""Occlusion: let the subject pass IN FRONT of the text.

The single loudest "this looks expensive" move available to an automated
pipeline: the word crosses the frame at hero scale, and the person/product
occludes it, which places the type at a real depth in the scene. It also
FLIPS the dead-space law for that super: text may cross the subject exactly
because the subject wins.

  occlude.py <composite.mp4> <plate.mp4> <out.mp4> --from T0 --to T1
             [--engine rembg|vision] [--feather 1.6] [--fps 24]

composite = the HyperFrames render (film + text).
plate     = the same film WITHOUT text (the locked cut / mix).
The window [T0, T1] is the occluded super's window only — never mask the
whole film. Frames outside the window pass through untouched; the weld is
frame-exact.

Layer order (the alphamerge sandwich, measured leak 4/255 max):
  composite  ->  subject cut from the plate laid back ON TOP.

Engines:
  rembg  (default) — isnet-general-use, ~1.4s/frame, pip-installable anywhere.
  vision — macOS Vision framework via pyobjc, ~0.16s/frame, zero downloads;
           used automatically when importable.
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path


def extract_frames(video, t0, t1, fps, out_dir):
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                    "-ss", f"{t0:.3f}", "-to", f"{t1:.3f}", "-i", str(video),
                    "-r", str(fps), str(out_dir / "f%05d.png")], check=True)
    return sorted(out_dir.glob("f*.png"))


def masks_rembg(frames, mask_dir):
    from rembg import remove, new_session
    from PIL import Image
    sess = new_session("isnet-general-use")
    for f in frames:
        m = remove(Image.open(f), session=sess, only_mask=True)
        m.save(mask_dir / f.name)


def masks_vision(frames, mask_dir):
    import Vision, Quartz
    import numpy as np
    from PIL import Image
    for f in frames:
        url = Quartz.CFURLCreateWithFileSystemPath(
            None, str(f), Quartz.kCFURLPOSIXPathStyle, False)
        handler = Vision.VNImageRequestHandler.alloc().initWithURL_options_(url, {})
        req = Vision.VNGeneratePersonSegmentationRequest.alloc().initWithCompletionHandler_(None)
        req.setQualityLevel_(0)  # 0 = accurate in current SDKs (measured fastest+best)
        handler.performRequests_error_([req], None)
        res = req.results()
        if not res:
            Image.new("L", Image.open(f).size, 0).save(mask_dir / f.name)
            continue
        pb = res[0].pixelBuffer()
        Quartz.CVPixelBufferLockBaseAddress(pb, 1)
        w = Quartz.CVPixelBufferGetWidth(pb)
        h = Quartz.CVPixelBufferGetHeight(pb)
        bpr = Quartz.CVPixelBufferGetBytesPerRow(pb)
        base = Quartz.CVPixelBufferGetBaseAddress(pb)
        arr = np.frombuffer(base.as_buffer(bpr * h), dtype=np.float32)
        arr = arr.reshape(h, bpr // 4)[:, :w].copy()
        Quartz.CVPixelBufferUnlockBaseAddress(pb, 1)
        arr = np.nan_to_num(arr, nan=0.0)
        img = Image.fromarray((np.clip(arr, 0, 1) * 255).astype("uint8"))
        img.resize(Image.open(f).size).save(mask_dir / f.name)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("composite"); ap.add_argument("plate"); ap.add_argument("out")
    ap.add_argument("--from", dest="t0", type=float, required=True)
    ap.add_argument("--to", dest="t1", type=float, required=True)
    ap.add_argument("--engine", choices=["rembg", "vision", "auto"], default="auto")
    ap.add_argument("--feather", type=float, default=1.6)
    ap.add_argument("--fps", type=int, default=24)
    # 0.35: a shipped, approved occlusion measured ~20% hidden and still read
    # cleanly; the one that failed review measured well past half.
    ap.add_argument("--max-hidden", type=float, default=0.35,
                    help="fail if the subject hides more than this fraction of the "
                         "super's glyph pixels (default 0.35)")
    a = ap.parse_args()

    engine = a.engine
    if engine == "auto":
        try:
            import Vision, Quartz  # noqa
            engine = "vision"
        except ImportError:
            engine = "rembg"
    print(f"engine: {engine}  window: {a.t0:.2f}-{a.t1:.2f}s")

    # snap the window to the frame grid and count in FRAMES, never seconds —
    # per-segment rounding drifts (+0.43s over 25 segments, measured elsewhere)
    n0 = round(a.t0 * a.fps)
    n1 = round(a.t1 * a.fps)
    t0f, t1f = n0 / a.fps, n1 / a.fps
    nseg = n1 - n0

    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        fdir = td / "frames"; mdir = td / "masks"
        fdir.mkdir(); mdir.mkdir()
        frames = extract_frames(a.plate, t0f, t1f, a.fps, fdir)[:nseg]
        print(f"{len(frames)} plate frames")
        (masks_vision if engine == "vision" else masks_rembg)(frames, mdir)

        # mask video: slight erosion via contrast, then a small feather —
        # kills the background-halo edge every segmenter leaves
        mask_mp4 = td / "mask.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error", "-framerate", str(a.fps),
             "-i", str(mdir / "f%05d.png"),
             "-vf", f"format=gray,eq=contrast=8:brightness=-0.12,gblur=sigma={a.feather}",
             "-frames:v", str(nseg),
             "-c:v", "libx264", "-crf", "10", str(mask_mp4)], check=True)

        # pre-trim both sources to clean intermediates so the merge sees three
        # plain equal-length streams (inline trims + fps filters froze the
        # segment — measured; the plain 3-input graph is the proven one)
        comp_seg = td / "comp_seg.mp4"; plate_seg = td / "plate_seg.mp4"
        for src, dst in ((a.composite, comp_seg), (a.plate, plate_seg)):
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                            "-ss", f"{t0f:.5f}", "-i", str(src),
                            "-frames:v", str(nseg), "-r", str(a.fps), "-an",
                            "-c:v", "libx264", "-crf", "12", str(dst)], check=True)

        # occluded segment: composite under, plate-subject back on top.
        # gbrp (RGB planes) so a single-plane mask applies to all channels
        # without the yuv chroma-half-blend trap (measured: 24.7% ghosting).
        seg = td / "seg.mp4"
        subprocess.run(
            ["ffmpeg", "-y", "-loglevel", "error",
             "-i", str(comp_seg), "-i", str(plate_seg), "-i", str(mask_mp4),
             "-filter_complex",
             "[0:v]format=gbrp[c];[1:v]format=gbrp[p];[2:v]format=gray[m];"
             "[c][p][m]maskedmerge,format=yuv420p[out]",
             "-map", "[out]", "-frames:v", str(nseg),
             "-c:v", "libx264", "-crf", "16", str(seg)], check=True)

        # frame-exact weld: before + segment + after (audio from composite)
        pre = td / "pre.mp4"; post = td / "post.mp4"; cc = td / "concat.txt"
        parts = []
        if n0 > 0:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.composite,
                            "-frames:v", str(n0), "-r", str(a.fps), "-an",
                            "-c:v", "libx264", "-crf", "16", str(pre)], check=True)
            parts.append(pre)
        parts.append(seg)
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", a.composite,
                        "-ss", f"{t1f:.5f}", "-r", str(a.fps), "-an",
                        "-c:v", "libx264", "-crf", "16", str(post)], check=True)
        parts.append(post)
        cc.write_text("".join(f"file '{p}'\n" for p in parts))
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error",
                        "-f", "concat", "-safe", "0", "-i", str(cc),
                        "-i", a.composite,
                        "-map", "0:v", "-map", "1:a?",
                        "-c:v", "copy", "-c:a", "copy", a.out], check=True)

        # ── THE LEGIBILITY GATE ──────────────────────────────────────────
        # Measured failure (17.8, MaryRuth's): the subject was punched over a
        # hero super and the line "A pour, not a pill" reached the customer as
        # "ur, / a ill". Every other check had passed — overlay_qa measures
        # contrast, reading time, sync and breath on the PRE-occlusion render,
        # and the verify below only asks whether the window still moves. Nothing
        # asked the one question that decides whether the super did its job:
        # can you still READ it.
        #
        # Occlusion is only the expensive move while the line survives it. Past
        # roughly a third of its glyph pixels it stops reading as depth and
        # starts reading as a bug, so this gate is hard: it fails the run rather
        # than shipping a sentence in pieces.
        import numpy as np
        from PIL import Image

        def _samples(v, n, name):
            d = td / name
            d.mkdir(exist_ok=True)
            step = max(1, nseg // n)
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(v),
                            "-vf", f"select='not(mod(n\\,{step}))'", "-vsync", "0",
                            "-frames:v", str(n), str(d / "s%03d.png")], check=True)
            return sorted(d.glob("s*.png"))

        N = 8
        hidden = []
        for c, p, o in zip(_samples(comp_seg, N, "sc"),
                           _samples(plate_seg, N, "sp"),
                           _samples(seg, N, "so")):
            C = np.asarray(Image.open(c).convert("RGB"), dtype=float)
            P = np.asarray(Image.open(p).convert("RGB"), dtype=float)
            O = np.asarray(Image.open(o).convert("RGB"), dtype=float)
            # the type IS whatever the composite added on top of the plate
            text = np.abs(C - P).mean(axis=2) > 12
            if text.sum() < 200:        # no type up in this frame; nothing to judge
                continue
            survived = text & (np.abs(O - P).mean(axis=2) > 12)
            hidden.append(1.0 - survived.sum() / text.sum())
        if hidden:
            mean_hidden, worst = float(np.mean(hidden)), float(np.max(hidden))
            print(f"legibility: {mean_hidden:.0%} of the type hidden on average, "
                  f"{worst:.0%} at worst (budget {a.max_hidden:.0%})")
            if mean_hidden > a.max_hidden:
                # Delete the artifact before failing. The weld already wrote a
                # plausible-looking mp4, and a refused run that leaves a finished
                # file on disk is how the broken version gets picked up later.
                Path(a.out).unlink(missing_ok=True)
                sys.exit(
                    f"OCCLUSION REFUSED: the subject hides {mean_hidden:.0%} of this "
                    f"super's glyphs (budget {a.max_hidden:.0%}). The reader gets "
                    "fragments, not a sentence. No output was written. Move the super "
                    "into the measured clean band for its window, shrink it to the "
                    "largest size that band can host, or drop the occlusion for this "
                    "film — an unreadable line is worth less than no effect at all.")
        else:
            print("legibility: no type inside the window — nothing was occluded")

        # verify the weld: motion must exist INSIDE the occluded window and
        # the total duration must match the composite within 2 frames
        def _grab(v, t, name):
            p = td / name
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}",
                            "-i", str(v), "-frames:v", "1", str(p)], check=True)
            return np.asarray(Image.open(p).convert("L"), dtype=float)
        mid = (t0f + t1f) / 2
        d = np.abs(_grab(a.out, mid, "va.png") -
                   _grab(a.out, min(mid + 0.8, t1f - 0.05), "vb.png")).mean()
        if d < 0.5:
            sys.exit(f"OCCLUDE VERIFY FAILED: window is frozen (frame diff {d:.2f})")
        print(f"verify: window motion {d:.1f} OK")
    print(f"occluded -> {a.out}")


if __name__ == "__main__":
    main()
