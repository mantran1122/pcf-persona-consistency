"""Full experiment driver: generate all conditions, judge (C1+C2 first, then B0),
then sampling + analysis. Every stage is resume-safe; rerun this script to continue
after any interruption."""

import traceback

from src import analyze_results, generate_responses, judge_responses, load_config, sample_for_human_eval

ctx = load_config.load_all()

print("=== STAGE 1: generation (all conditions) ===", flush=True)
n_done, n_skip = generate_responses.generate_all(ctx)
print(f"generation: {n_done} new, {n_skip} skipped", flush=True)
generate_responses.collect_raw_csv()

for conds in (["C1", "C2", "C3", "C4"], ["B0"]):
    print(f"=== STAGE 2: judging {conds} ===", flush=True)
    try:
        judge_responses.judge_all(ctx, conditions=conds)
    except Exception:
        print(f"!!! judging {conds} aborted (budget/API error?); continuing with what we have", flush=True)
        traceback.print_exc()

print("=== STAGE 3: collect + sample + analyze ===", flush=True)
judged = judge_responses.collect_judged_csv()
print(f"{len(judged)} judged responses collected", flush=True)
sample_for_human_eval.make_sample(judged, ctx, fraction=0.25)
analyze_results.run_full_analysis(judged)
print("=== ALL DONE ===", flush=True)
