"""Bounded body-only smoke, explicitly excluding real MaleCNS neural execution.

Invoke through the unchanged guarded_child.py using the isolated body interpreter.
No graph preparation or registered source read is needed or permitted.
"""

import json
import math
from pathlib import Path
import sys

import validation_firewall

if not validation_firewall.ACTIVE:
    raise RuntimeError("source firewall must be installed before this body check")

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from malecns_sim.application.flight_body import FlybodyBody


def main():
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", required=True)
    parser.add_argument("--left-image", required=True)
    parser.add_argument("--right-image", required=True)
    parser.add_argument("--overview-image")
    parser.add_argument("--continuous-steps", type=int, default=0)
    args = parser.parse_args()
    if not 0 <= args.continuous_steps <= 10000:
        parser.error("continuous check must be 0..10000 steps")
    destinations = [Path(value).resolve() for value in (args.record, args.left_image, args.right_image)]
    if args.overview_image:
        destinations.append(Path(args.overview_image).resolve())
    if any(path.exists() for path in destinations):
        raise ValueError("new body-only evidence paths required")
    body = None
    action = {"left_wing_yaw_offset_rad": 0.0, "right_wing_yaw_offset_rad": 0.0, "frequency_fraction": 0.0}
    record = {"schema": "flight-body-only-smoke-v1",
              "real_neural_execution": False, "registered_payload_access": "denied by existing validation firewall",
              "claim": "body-only integration and camera smoke; no stable flight, neural flight control, or biological fidelity certification"}
    try:
        body = FlybodyBody(pattern_kind="engineered-oscillator")
        record["body_identity"] = body.identity
        before = body.reset(0)
        from concurrent.futures import ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=2) as callers:
            initial_frame = callers.submit(body.render).result()
        for _ in range(50):
            after = body.advance(action)
        assert math.isclose(after["time_ms"], 10.0, abs_tol=1e-8)
        with ThreadPoolExecutor(max_workers=2) as callers:
            frame = callers.submit(body.render).result()
        assert frame != initial_frame, "eye frame must reflect physical advancement"
        assert frame["overview"] != initial_frame["overview"], "third-person view must be live"
        assert set(frame) == {"left", "right", "overview"}
        for side, eye in frame.items():
            size = 512 if side == "overview" else 256
            assert len(eye) == size and all(len(row) == size for row in eye)
            assert all(len(pixel) == 3 for row in eye for pixel in row)
        assert before == body.reset(0)
        for _ in range(50):
            replay = body.advance(action)
        assert replay == after
        for _ in range(131):
            later = body.advance(action)
        assert math.isclose(later["time_ms"], 36.2, abs_tol=1e-8)
        with ThreadPoolExecutor(max_workers=2) as callers:
            later_frame = callers.submit(body.render).result()
        assert later_frame["overview"] != frame["overview"]
        with ThreadPoolExecutor(max_workers=2) as callers:
            encoded = callers.submit(body.render_encoded).result()
        import base64
        from PIL import Image
        import io
        jpeg = base64.b64decode(encoded["overview"]["image_url"].split(",", 1)[1])
        with Image.open(io.BytesIO(jpeg)) as decoded:
            assert decoded.size == (512, 512) and decoded.format == "JPEG"
        encoded_bytes = len(json.dumps(encoded).encode())
        raw_bytes = len(json.dumps({"overview": later_frame["overview"]}).encode())
        assert encoded_bytes < raw_bytes / 10
        record.update(outcome="PASS_BODY_ONLY", intervals_per_replay=50, replays=2,
                      initial=before, final=after, exact_replay=True,
                      eye_shape=[256, 256, 3])
        record.update(live_frame_changed=True, cross_thread_render=True,
                      overview_shape=[512, 512, 3], verified_camera_times_ms=[0, 10, 36.2])
        record.update(primary_encoded_bytes=encoded_bytes, primary_rgb_json_bytes=raw_bytes)
        if args.continuous_steps:
            end = body.reset(0)
            completed = 0
            for _ in range(args.continuous_steps):
                end = body.advance(action)
                completed += 1
                if end["terminal"]:
                    break
            record["continuous_check"] = {"requested_steps": args.continuous_steps,
                "completed_steps": completed, "time_ms": end["time_ms"],
                "physics_terminal": end["terminal"], "completed": completed == args.continuous_steps}
        from PIL import Image
        for side, destination in zip(("left", "right", "overview"), destinations[1:]):
            Image.fromarray(body.np.asarray(frame[side], dtype="uint8")).save(destination)
    except BaseException as exc:
        record.update(outcome="FAIL_BODY_ONLY", failure=str(exc))
        raise
    finally:
        if body is not None:
            body.close()
        with destinations[0].open("x", encoding="utf-8") as output:
            json.dump(record, output, indent=2, allow_nan=False)
            output.write("\n")
    print(json.dumps({"outcome": record["outcome"], "exact_replay": record["exact_replay"],
                      "eye_shape": record["eye_shape"], "real_neural_execution": False}))


if __name__ == "__main__":
    main()
