"""Second-generator replication run (addresses reviewer note: results only held for one
generator, gpt-4o-mini). Generates + judges the SAME conditions/personas/scenarios/turns
with generator G2 (claude-3-5-haiku, see config/model_config.json), then re-collects CSVs
and runs the G1-vs-G2 comparison analysis.

Opt-in and separate from run_full.py on purpose: this roughly doubles the conditions'
worth of API calls (add up to 1,080 more responses), so it should only run when you're
ready for that cost. Resume-safe like every other stage: rerun to continue after
an interruption.

Usage:
    python run_generator2.py                 # all conditions, G2
    python run_generator2.py C1 C2 C3 C4      # skip B0 (persona-bearing conditions only,
                                               # cheaper: B0 has no persona so it's the
                                               # least informative condition to replicate)
"""

import sys
import traceback

from src import analyze_results, generate_responses, judge_responses, load_config

ctx = load_config.load_all()
conditions = sys.argv[1:] or ctx["experiment"]["conditions"]

print(f"=== STAGE 1: generation (G2, conditions={conditions}) ===", flush=True)
n_done, n_skip = generate_responses.generate_all(ctx, limit_conditions=conditions, generator_id="G2")
print(f"generation: {n_done} new, {n_skip} skipped", flush=True)
generate_responses.collect_raw_csv()

print("=== STAGE 2: judging (all unjudged raw records, G1+G2) ===", flush=True)
try:
    judge_responses.judge_all(ctx, conditions=None)  # judge everything not yet judged
except Exception:
    print("!!! judging aborted (budget/API error?); rerun this script to resume", flush=True)
    traceback.print_exc()

print("=== STAGE 3: collect + analyze (G1 primary + G1-vs-G2 comparison) ===", flush=True)
judged = judge_responses.collect_judged_csv()
print(f"{len(judged)} judged responses collected "
      f"({(judged['generator_id'] == 'G2').sum()} from G2)", flush=True)
analyze_results.run_full_analysis(judged)
print("=== DONE. See outputs/summaries/statistical_tests_generator_comparison.csv "
      "and summary_by_generator.csv ===", flush=True)
