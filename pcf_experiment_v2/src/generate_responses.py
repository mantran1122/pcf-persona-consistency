"""Main generation loop: conditions x personas x runs x counterbalanced scenarios x turns.

Every response is saved to its own JSON file immediately (resume-safe): rerunning
skips records that already exist on disk.
"""

import copy

from . import build_dialogues, load_config, memory_manager, utils
from .utils import RAW_DIR


def record_id(condition, persona_id, run_id, scenario_id, turn_id, generator_id="G1"):
    """G1 keeps the original unprefixed id (backward-compatible with the 1,080 responses
    already on disk); any other generator_id is prefixed so it can never collide with G1."""
    base = f"{condition}_{persona_id}_r{run_id}_{scenario_id}_t{turn_id}"
    return base if generator_id == "G1" else f"{generator_id}_{base}"


def record_path(rid, condition):
    return RAW_DIR / condition / f"{rid}.json"


def generate_all(ctx=None, limit_personas=None, limit_conditions=None, generator_id="G1"):
    """Run the full generation. limit_* allow small pilot runs (e.g. 1 persona, 1 condition).
    generator_id selects which entry of models.generators to use (default "G1", the paper's
    primary generator); pass "G2" to run the second-generator replication."""
    if ctx is None:
        ctx = load_config.load_all()
    logger = utils.get_logger()
    utils.ensure_dirs()
    load_config.snapshot_environment(ctx)

    exp = ctx["experiment"]
    conditions = limit_conditions or exp["conditions"]
    personas = ctx["personas"][:limit_personas] if limit_personas else ctx["personas"]
    scenarios_by_id = {s["scenario_id"]: s for s in ctx["scenarios"]}

    n_done = n_skipped = 0
    for condition in conditions:
        for p_idx, persona in enumerate(personas):
            for run_id in range(1, exp["num_runs"] + 1):
                order = (build_dialogues.get_scenario_order(ctx["latin_square"], p_idx,
                                                            run_id - 1, exp["num_runs"])
                         if exp.get("counterbalance", True)
                         else [s["scenario_id"] for s in ctx["scenarios"]])
                d, s = run_dialogue(condition, persona, run_id, order, scenarios_by_id, ctx,
                                    generator_id=generator_id)
                n_done += d
                n_skipped += s
    logger.info("Generation finished: %d new responses, %d skipped (already on disk)", n_done, n_skipped)
    return n_done, n_skipped


def run_dialogue(condition, persona, run_id, scenario_order, scenarios_by_id, ctx, generator_id="G1"):
    """One full dialogue: all scenarios in counterbalanced order, shared history and memory."""
    logger = utils.get_logger()
    exp = ctx["experiment"]
    gen_cfg = ctx["models"]["generators"][generator_id]
    domain_q = ctx["domain_questions"][persona["persona_id"]]

    history = []
    memory = memory_manager.initialize_memory(persona) if condition in ("C2", "C3") else None
    global_turn = 0
    n_done = n_skipped = 0

    for position, scenario_id in enumerate(scenario_order, start=1):
        scenario = scenarios_by_id[scenario_id]
        for turn in scenario["turns"][:exp["turns_per_scenario"]]:
            global_turn += 1
            rid = record_id(condition, persona["persona_id"], run_id, scenario_id, turn["turn_id"],
                            generator_id=generator_id)
            path = record_path(rid, condition)

            if path.exists() and exp.get("resume_on_failure", True):
                # Resume: replay saved turn into history/memory so later turns see it.
                rec = utils.load_json(path)
                history.append({"role": "user", "content": rec["user_prompt"]})
                history.append({"role": "assistant", "content": rec["model_response"]})
                if memory is not None and rec.get("memory_state_after"):
                    memory = rec["memory_state_after"]
                n_skipped += 1
                continue

            user_prompt = build_dialogues.render_turn_prompt(turn, persona, domain_q)
            messages = build_dialogues.build_messages(condition, persona, history, user_prompt, memory, ctx)
            memory_before = copy.deepcopy(memory)

            result = utils.chat_completion(
                gen_cfg, messages,
                dry_run_text=f"[DRY RUN] {persona['name']} answers turn {turn['turn_id']} of {scenario_id}.")
            response = result["text"]

            verification = None
            if condition in ("C3", "C4") and exp.get("run_verification"):
                from . import verifier
                response, verification = verifier.verify_and_maybe_revise(
                    persona, history, user_prompt, response, ctx,
                    condition=condition, memory=memory, generator_cfg=gen_cfg)

            if memory is not None:
                memory, mem_audit = memory_manager.update_memory(
                    memory, persona, user_prompt, response, ctx)
            else:
                mem_audit = None

            rec = {
                "record_id": rid,
                "experiment_id": exp["experiment_name"],
                "condition": condition,
                "run_id": run_id,
                "persona_id": persona["persona_id"],
                "scenario_id": scenario_id,
                "scenario_position": position,
                "turn_id": turn["turn_id"],
                "global_turn_id": global_turn,
                "tactic": turn["tactic"],
                "difficulty": turn["difficulty"],
                "system_prompt": messages[0]["content"],
                "memory_state_before": memory_before,
                "memory_state_after": copy.deepcopy(memory),
                "memory_update_audit": mem_audit,
                "user_prompt": user_prompt,
                "model_response": response,
                "verification": verification,
                "generator_id": generator_id,
                "generation_model": gen_cfg["model"],
                "temperature": gen_cfg["temperature"],
                "timestamp": utils.now_iso(),
                "latency_seconds": result["latency_seconds"],
                "usage": result["usage"],
                "retry_count": result["retry_count"],
            }
            utils.save_json(rec, path)
            n_done += 1
            logger.info("saved %s", rid)

            history.append({"role": "user", "content": user_prompt})
            history.append({"role": "assistant", "content": response})

    return n_done, n_skipped


def collect_raw_csv():
    """Aggregate all per-response JSON files into outputs/summaries/responses_raw.csv."""
    import pandas as pd
    rows = []
    for path in sorted(RAW_DIR.rglob("*.json")):
        rec = utils.load_json(path)
        row = {k: rec.get(k) for k in [
            "record_id", "experiment_id", "condition", "run_id", "persona_id",
            "scenario_id", "scenario_position", "turn_id", "global_turn_id",
            "tactic", "difficulty", "user_prompt", "model_response",
            "generation_model", "temperature", "timestamp",
            "latency_seconds", "retry_count"]}
        row["generator_id"] = rec.get("generator_id", "G1")  # pre-G2 raw files predate this field
        rows.append(row)
    df = pd.DataFrame(rows)
    utils.ensure_dirs()
    out = utils.SUMMARY_DIR / "responses_raw.csv"
    df.to_csv(out, index=False, encoding="utf-8-sig")
    return df


if __name__ == "__main__":
    generate_all()
    collect_raw_csv()
