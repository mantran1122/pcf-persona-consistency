"""Load configs, data files, and prompt templates; snapshot the environment for reproducibility."""

import platform
import sys
from importlib.metadata import PackageNotFoundError, version

from . import utils
from .utils import CONFIG_DIR, DATA_DIR, PROMPTS_DIR, SUMMARY_DIR


def load_all():
    """Return a single context dict used by every pipeline stage."""
    ctx = {
        "experiment": utils.load_json(CONFIG_DIR / "experiment_config.json"),
        "models": utils.load_json(CONFIG_DIR / "model_config.json"),
        "rubric": utils.load_json(CONFIG_DIR / "rubric.json"),
        "personas": utils.load_json(DATA_DIR / "personas.json"),
        "scenarios": utils.load_json(DATA_DIR / "scenarios.json")["scenarios"],
        "domain_questions": {k: v for k, v in utils.load_json(DATA_DIR / "domain_questions.json").items()
                             if not k.startswith("_")},
        "latin_square": utils.load_json(DATA_DIR / "latin_square_orders.json"),
        "prompts": {
            "generator_system": utils.load_text(PROMPTS_DIR / "generator_system_prompt.txt"),
            "generator_memory": utils.load_text(PROMPTS_DIR / "generator_memory_prompt.txt"),
            "memory_update": utils.load_text(PROMPTS_DIR / "memory_update_prompt.txt"),
            "verification": utils.load_text(PROMPTS_DIR / "verification_prompt.txt"),
            "judge": utils.load_text(PROMPTS_DIR / "judge_prompt.txt"),
        },
    }
    validate(ctx)
    return ctx


def validate(ctx):
    exp = ctx["experiment"]
    assert exp["conditions"], "No conditions configured"
    for c in exp["conditions"]:
        assert c in {"B0", "C1", "C2", "C3", "C4"}, f"Unknown condition {c}"
    if {"C3", "C4"} & set(exp["conditions"]):
        assert exp.get("run_verification"), "C3/C4 require run_verification=true"
    ids = [p["persona_id"] for p in ctx["personas"]]
    assert len(ids) == len(set(ids)), "Duplicate persona_id"
    for p in ctx["personas"]:
        assert p["persona_id"] in ctx["domain_questions"], f"Missing domain question for {p['persona_id']}"
    sids = [s["scenario_id"] for s in ctx["scenarios"]]
    for order in ctx["latin_square"]:
        assert sorted(order) == sorted(sids), f"Latin square row {order} does not match scenarios {sids}"


def snapshot_environment(ctx):
    """Save SDK versions, model IDs, and full config for the paper's reproducibility section."""
    def pkg_version(name):
        try:
            return version(name)
        except PackageNotFoundError:
            return "not installed"

    snap = {
        "timestamp": utils.now_iso(),
        "python": sys.version,
        "platform": platform.platform(),
        "sdk_versions": {p: pkg_version(p) for p in
                         ["openai", "anthropic", "pandas", "numpy", "scipy", "matplotlib"]},
        "experiment_config": ctx["experiment"],
        "model_config": ctx["models"],
        "num_personas": len(ctx["personas"]),
        "num_scenarios": len(ctx["scenarios"]),
    }
    utils.ensure_dirs()
    utils.save_json(snap, SUMMARY_DIR / "environment_snapshot.json")
    return snap
