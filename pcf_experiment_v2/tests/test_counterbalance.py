"""Unit tests for counterbalancing and prompt rendering (checklist item F)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src import build_dialogues, load_config, memory_manager  # noqa: E402


def test_williams_design_positions_balanced():
    """Williams design (10 rows, 5 scenarios): each scenario appears exactly
    len(square)/5 times in every position, and each row is a permutation."""
    ctx = load_config.load_all()
    square = ctx["latin_square"]
    n_scen = len(square[0])
    per_position = len(square) // n_scen
    for pos in range(n_scen):
        column = [row[pos] for row in square]
        for s in set(column):
            assert column.count(s) == per_position, \
                f"Position {pos}: {s} appears {column.count(s)}x, expected {per_position}"
    for row in square:
        assert len(set(row)) == n_scen, f"Row repeats a scenario: {row}"


def test_williams_design_carryover_balanced():
    """Each ordered pair (A immediately before B) occurs equally often across rows."""
    ctx = load_config.load_all()
    square = ctx["latin_square"]
    pairs = {}
    for row in square:
        for a, b in zip(row, row[1:]):
            pairs[(a, b)] = pairs.get((a, b), 0) + 1
    counts = set(pairs.values())
    n_scen = len(square[0])
    assert len(pairs) == n_scen * (n_scen - 1), "Not every ordered pair occurs"
    assert len(counts) == 1, f"Carryover unbalanced: pair counts vary {pairs}"


def test_personas_get_different_orders():
    """Not all personas share the same order within a run."""
    ctx = load_config.load_all()
    num_runs = ctx["experiment"]["num_runs"]
    orders = [tuple(build_dialogues.get_scenario_order(ctx["latin_square"], p, 0, num_runs))
              for p in range(len(ctx["personas"]))]
    assert len(set(orders)) > 1, "All personas received the same scenario order"


def test_runs_get_different_orders():
    ctx = load_config.load_all()
    num_runs = ctx["experiment"]["num_runs"]
    orders = [tuple(build_dialogues.get_scenario_order(ctx["latin_square"], 0, r, num_runs))
              for r in range(num_runs)]
    assert len(set(orders)) == len(orders), "Runs for one persona share an order"


def test_all_rows_used_across_dialogues():
    """With 6 personas x 3 runs = 18 dialogues, all 10 Williams rows are used."""
    ctx = load_config.load_all()
    num_runs = ctx["experiment"]["num_runs"]
    used = {(p * num_runs + r) % len(ctx["latin_square"])
            for p in range(len(ctx["personas"])) for r in range(num_runs)}
    assert used == set(range(len(ctx["latin_square"]))), \
        f"Rows never used: {set(range(len(ctx['latin_square']))) - used}"


def test_all_prompts_render_for_all_personas():
    """Every scenario turn template renders without KeyError for every persona."""
    ctx = load_config.load_all()
    for persona in ctx["personas"]:
        dq = ctx["domain_questions"][persona["persona_id"]]
        for scenario in ctx["scenarios"]:
            for turn in scenario["turns"]:
                text = build_dialogues.render_turn_prompt(turn, persona, dq)
                assert "{" not in text.replace("{}", ""), f"Unrendered placeholder in: {text[:80]}"


def test_c1_c2_differ_only_in_memory():
    """C2 system prompt == C1 system prompt + memory block (checklist item I)."""
    ctx = load_config.load_all()
    persona = ctx["personas"][0]
    memory = memory_manager.initialize_memory(persona)
    c1 = build_dialogues.build_messages("C1", persona, [], "hello", None, ctx)
    c2 = build_dialogues.build_messages("C2", persona, [], "hello", memory, ctx)
    assert c2[0]["content"].startswith(c1[0]["content"]), "C2 must extend C1, not change it"
    assert c1[1:] == c2[1:], "Non-system messages must be identical between C1 and C2"


def test_system_prompt_renders():
    ctx = load_config.load_all()
    for persona in ctx["personas"]:
        text = build_dialogues.build_system_prompt(ctx["prompts"]["generator_system"], persona)
        assert persona["name"] in text
        assert "{" not in text, "Unrendered placeholder in system prompt"


if __name__ == "__main__":
    for fn_name, fn in sorted(globals().items()):
        if fn_name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS {fn_name}")
    print("All tests passed.")
