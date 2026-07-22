# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Working with the user

The user is learning by writing the implementation themselves. **Do not write
or edit code in source files unless explicitly asked to.** Instead, explain
the relevant principles, concepts, and design considerations, and (when
useful) break the task into an ordered checklist of subgoals for the user to
implement against. Only write actual code when the user specifically
requests it.

## Project status

Early scaffolding stage. Only `src/models.py` and `src/config.py` have real
content; `canvas.py`, `gestures.py`, `hand_tracker.py`, `smoothing.py`, and
`main.py` are empty placeholder files. `requirements.txt` is also empty even
though the design calls for `mediapipe`, `opencv-python`, and `pygame` (see
`PLAN.md`). There is no test suite, lint config, or build tooling yet — don't
assume any of that exists without checking first.

## Architecture

`PLAN.md` (in Swedish) is the authoritative design document — read it before
implementing any module, since it specifies exact responsibilities, method
signatures, and test strategy per file. The summary below is the gist.

Hand Painter lets a user draw on screen with their index finger, tracked via
webcam using MediaPipe. The pipeline for one frame is a straight-line
dependency chain:

```
webcam frame (BGR)
    → hand_tracker.py  → HandLandmarks (21 landmarks + handedness)
    → smoothing.py     → smooths fingertip position across frames
    → gestures.py      → GestureState (e.g. is_drawing=True/False)
    → canvas.py         → draws strokes on a Pygame surface from GestureState + BrushSettings
    → main.py           → glues the loop together, runs it per frame
```

Every module communicates only through the shared dataclasses in
`src/models.py` — no module needs to know another's internals. This is the
mechanism that's meant to make the hand-tracking backend or gesture set
swappable later without touching unrelated code.

### Module contracts (`src/models.py`)

- `Point(x, y, z=0.0)` — a normalized coordinate (0.0–1.0).
- `HandLandmarks(points, handedness, confidence)` — 21 `Point`s plus which
  hand ("Left"/"Right") and detection confidence.
- `GestureState(is_drawing, fingertip, gesture_name="none")` — the
  interpreted result of a hand pose.
- `BrushSettings(color, thickness, brush_type)` — `frozen=True`; create a
  modified copy with `dataclasses.replace` instead of mutating.

### Configuration (`src/config.py`)

All tunable constants live here: camera resolution, MediaPipe detection/
tracking confidence thresholds, landmark indices for thumb/index fingertip
(`LANDMARK_THUMB_TIP`, `LANDMARK_INDEX_TIP`), the pinch-gesture distance
threshold (`PINCH_THRESHOLD`), and the exponential smoothing factor
(`SMOOTHING_FACTOR`).

### Intended module responsibilities (not yet implemented)

- **`hand_tracker.py`** — the only module allowed to import `mediapipe`
  directly. Wraps it behind `HandTracker.process(frame) -> HandLandmarks | None`.
- **`smoothing.py`** — `ExponentialSmoother(alpha)` with
  `smooth(new_point: Point) -> Point`, weighting new vs. previous position:
  `smoothed = alpha * new_point + (1 - alpha) * previous_smoothed`. First
  call on a fresh instance returns the raw point unchanged.
- **`gestures.py`** — `interpret(landmarks: HandLandmarks) -> GestureState`.
  Computes distance between thumb tip and index tip; below
  `config.PINCH_THRESHOLD` means `is_drawing=True`, `gesture_name="pinch"`.
  New gestures should be added as new functions in this file only.
- **`canvas.py`** — scales normalized (0–1) coordinates to screen pixels and
  draws lines between consecutive fingertip positions on a Pygame surface
  while `is_drawing=True`.
- **`main.py`** — thin glue loop only: read camera → `hand_tracker.process()`
  → `smoothing.smooth()` → `gestures.interpret()` → `canvas.update()`/`render()`.

Build order follows the dependency chain in the table in `PLAN.md`:
`models.py` → `config.py` → `smoothing.py` → `hand_tracker.py` →
`gestures.py` → `canvas.py` → `main.py`. Everything up through `gestures.py`
is testable without a camera (mock MediaPipe's output for `hand_tracker.py`);
`canvas.py` needs visual/pixel-level checks; `main.py` realistically needs a
real camera or a recorded test video.
