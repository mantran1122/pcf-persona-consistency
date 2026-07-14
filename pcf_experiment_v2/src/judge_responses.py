"""LLM-as-a-Judge: score every raw response with the rubric. Resume-safe like generation.

The judge sees: persona profile, full dialogue history up to the turn, current user
message, and the target response. Output JSON is schema-validated with retry.
"""

import json

from . import build_dialogues, load_config, utils
from .utils import JUDGED_DIR, RAW_DIR, SUMMARY_DIR

SCORE_KEYS = ["persona_consistency", "memory_retention", "style_stability", "context_awareness"]


def validate_judgment(j, valid_labels):
    for k in SCORE_KEYS:
        if not isinstance(j.get(k), int) or not 1 <= j[k] <= 5:
            raise ValueError(f"{k} out of range: {j.get(k)!r}")
    if j.get("contradiction_flag") not in (0, 1):
        raise ValueError(f"contradiction_flag invalid: {j.get('contradiction_flag')!r}")
    if j.get("error_label") not in valid_labels:
        raise ValueError(f"error_label invalid: {j.get('error_label')!r}")
    conf = j.get("confidence")
    if not isinstance(conf, (int, float)) or not 0 <= conf <= 1:
        raise ValueError(f"confidence invalid: {conf!r}")
    return j


def rebuild_history(records, target):
    """Reconstruct dialogue history up to (not including) the target turn from raw records."""
    prior = [r for r in records
             if r["condition"] == target["condition"]
             and r["persona_id"] == target["persona_id"]
             and r["run_id"] == target["run_id"]
             and r.get("generator_id", "G1") == target.get("generator_id", "G1")
             and r["global_turn_id"] < target["global_turn_id"]]
    prior.sort(key=lambda r: r["global_turn_id"])
    history = []
    for r in prior:
        history.append({"role": "user", "content": r["user_prompt"]})
        history.append({"role": "assistant", "content": r["model_response"]})
    return history


def judge_one(record, history, persona, ctx):
    logger = utils.get_logger()
    rubric_text = json.dumps(ctx["rubric"]["dimensions"], ensure_ascii=False, indent=2)
    prompt = ctx["prompts"]["judge"].format(
        persona_profile=json.dumps(persona, ensure_ascii=False, indent=2),
        history=build_dialogues.format_history_for_eval(history),
        user_prompt=record["user_prompt"],
        response=record["model_response"],
        rubric=rubric_text,
    )
    valid_labels = set(ctx["rubric"]["error_labels"])
    dry = json.dumps({"persona_consistency": 4, "memory_retention": 4, "style_stability": 4,
                      "context_awareness": 4, "contradiction_flag": 0, "error_label": "none",
                      "confidence": 0.9, "note": "[DRY RUN]"})

    max_json_retries = ctx["experiment"].get("max_retries", 3)
    last_err = None
    for attempt in range(max_json_retries):
        result = utils.chat_completion(ctx["models"]["judge"],
                                       [{"role": "user", "content": prompt}], dry_run_text=dry)
        try:
            j = validate_judgment(utils.parse_llm_json(result["text"]), valid_labels)
            j["judge_model"] = ctx["models"]["judge"]["model"]
            j["judge_latency_seconds"] = result["latency_seconds"]
            j["judge_json_retries"] = attempt
            j["timestamp"] = utils.now_iso()
            return j
        except (ValueError, json.JSONDecodeError) as e:
            last_err = e
            logger.warning("Judge JSON invalid for %s (attempt %d): %s",
                           record["record_id"], attempt + 1, e)
    raise RuntimeError(f"Judge failed to return valid JSON for {record['record_id']}: {last_err}")


def judge_all(ctx=None, conditions=None):
    """Judge all raw records; `conditions` optionally restricts to a subset (budget control)."""
    if ctx is None:
        ctx = load_config.load_all()
    logger = utils.get_logger()
    utils.ensure_dirs()
    personas = {p["persona_id"]: p for p in ctx["personas"]}

    records = [utils.load_json(p) for p in sorted(RAW_DIR.rglob("*.json"))]
    targets = [r for r in records if conditions is None or r["condition"] in conditions]
    logger.info("Judging %d of %d raw records", len(targets), len(records))

    n_done = n_skipped = 0
    for rec in targets:
        out_path = JUDGED_DIR / rec["condition"] / f"{rec['record_id']}.json"
        if out_path.exists():
            n_skipped += 1
            continue
        history = rebuild_history(records, rec)
        judgment = judge_one(rec, history, personas[rec["persona_id"]], ctx)
        utils.save_json({"record_id": rec["record_id"], **judgment}, out_path)
        n_done += 1
        logger.info("judged %s -> %s", rec["record_id"], judgment["error_label"])
    logger.info("Judging finished: %d new, %d skipped", n_done, n_skipped)
    return n_done, n_skipped


def collect_judged_csv():
    """Merge raw metadata + judge scores into outputs/summaries/responses_judged.csv."""
    import pandas as pd
    raw = {r["record_id"]: r for r in (utils.load_json(p) for p in sorted(RAW_DIR.rglob("*.json")))}
    rows = []
    for path in sorted(JUDGED_DIR.rglob("*.json")):
        j = utils.load_json(path)
        r = raw.get(j["record_id"], {})
        rows.append({
            "record_id": j["record_id"],
            "condition": r.get("condition"),
            "run_id": r.get("run_id"),
            "generator_id": r.get("generator_id", "G1"),
            "generation_model": r.get("generation_model"),
            "persona_id": r.get("persona_id"),
            "scenario_id": r.get("scenario_id"),
            "scenario_position": r.get("scenario_position"),
            "turn_id": r.get("turn_id"),
            "global_turn_id": r.get("global_turn_id"),
            "tactic": r.get("tactic"),
            "difficulty": r.get("difficulty"),
            "user_prompt": r.get("user_prompt"),
            "model_response": r.get("model_response"),
            **{k: j[k] for k in SCORE_KEYS},
            "contradiction_flag": j["contradiction_flag"],
            "error_label": j["error_label"],
            "confidence": j["confidence"],
            "judge_note": j.get("note", ""),
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df["overall_score"] = df[SCORE_KEYS].mean(axis=1)
    out = SUMMARY_DIR / "responses_judged.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    judge_all()
    collect_judged_csv()
