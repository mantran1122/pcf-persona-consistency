"""Structured memory for condition C2/C3: initialize, render, update (rule-based or LLM extraction)."""

import copy
import json

from . import utils

MEMORY_KEYS = ["persona_facts", "user_facts", "shared_events", "preferences", "constraints"]


def initialize_memory(persona):
    """Seed memory from the persona profile only (no invented facts)."""
    return {
        "persona_facts": list(persona["known_facts"]),
        "user_facts": [],
        "shared_events": [],
        "preferences": {"likes": list(persona["likes"]), "dislikes": list(persona["dislikes"])},
        "constraints": list(persona["behavioral_constraints"]),
        "recent_summary": "",
    }


def render_memory_block(template, memory):
    return template.format(
        persona_facts=json.dumps(memory["persona_facts"], ensure_ascii=False),
        user_facts=json.dumps(memory["user_facts"], ensure_ascii=False),
        shared_events=json.dumps(memory["shared_events"], ensure_ascii=False),
        preferences=json.dumps(memory["preferences"], ensure_ascii=False),
        constraints=json.dumps(memory["constraints"], ensure_ascii=False),
        recent_summary=memory["recent_summary"] or "(none yet)",
    )


def update_memory_rule(memory, user_prompt, response):
    """Minimal rule-based fallback: only refresh the recent summary."""
    memory = copy.deepcopy(memory)
    memory["recent_summary"] = f"User said: {user_prompt[:200]} | Assistant replied: {response[:200]}"
    return memory, {"mode": "rule"}


def update_memory_llm(memory, persona, user_prompt, response, ctx):
    """LLM extraction update. Falls back to rule-based on parse failure."""
    logger = utils.get_logger()
    prompt = ctx["prompts"]["memory_update"].format(
        memory_json=json.dumps(memory, ensure_ascii=False, indent=2),
        user_prompt=user_prompt,
        response=response,
        persona_name=persona["name"],
    )
    dry = json.dumps({"new_persona_facts": [], "new_user_facts": [], "new_shared_events": [],
                      "new_preferences": [], "conflicts_detected": [],
                      "recent_summary": "[DRY RUN] summary"})
    result = utils.chat_completion(ctx["models"]["memory_extractor"],
                                   [{"role": "user", "content": prompt}],
                                   dry_run_text=dry)
    try:
        delta = utils.parse_llm_json(result["text"])
    except (ValueError, json.JSONDecodeError) as e:
        logger.warning("Memory extraction JSON invalid (%s); falling back to rule-based update", e)
        return update_memory_rule(memory, user_prompt, response)

    memory = copy.deepcopy(memory)
    for src_key, dst_key in [("new_persona_facts", "persona_facts"),
                             ("new_user_facts", "user_facts"),
                             ("new_shared_events", "shared_events")]:
        for fact in delta.get(src_key, []) or []:
            if isinstance(fact, str) and fact and fact not in memory[dst_key]:
                memory[dst_key].append(fact)
    memory["recent_summary"] = str(delta.get("recent_summary", ""))[:500]
    audit = {"mode": "llm", "delta": delta, "retry_count": result["retry_count"]}
    return memory, audit


def update_memory(memory, persona, user_prompt, response, ctx):
    mode = ctx["experiment"].get("memory_update_mode", "llm")
    if mode == "llm":
        return update_memory_llm(memory, persona, user_prompt, response, ctx)
    return update_memory_rule(memory, user_prompt, response)
