"""Counterbalancing (Latin square), prompt rendering, and message assembly per condition."""

from . import memory_manager


def get_scenario_order(latin_square, persona_index, run_index, num_runs=3):
    """Deterministic counterbalanced order over a Williams design (10 rows for 5 scenarios).

    persona_index * num_runs + run_index enumerates dialogues 0..(P*R-1), spreading them
    across all rows so every row is used before any repeats.
    """
    order_index = (persona_index * num_runs + run_index) % len(latin_square)
    return list(latin_square[order_index])


def render_turn_prompt(turn, persona, domain_question):
    """Substitute persona placeholders into a scenario turn template."""
    return turn["prompt_template"].format(
        name=persona["name"],
        role=persona["role"],
        domain_boundary=persona["domain_boundary"],
        known_fact_1=persona["known_facts"][0],
        known_fact_2=persona["known_facts"][1] if len(persona["known_facts"]) > 1 else persona["known_facts"][0],
        dislike_1=persona["dislikes"][0],
        domain_question=domain_question,
    )


def build_system_prompt(template, persona):
    style = persona["speaking_style"]
    return template.format(
        name=persona["name"],
        role=persona["role"],
        background=persona["background"],
        core_traits=", ".join(persona["core_traits"]),
        tone=style["tone"],
        length=style["length"],
        vocabulary=style["vocabulary"],
        uses_emojis="yes" if style["uses_emojis"] else "no",
        known_facts="; ".join(persona["known_facts"]),
        likes=", ".join(persona["likes"]),
        dislikes=", ".join(persona["dislikes"]),
        domain_boundary=persona["domain_boundary"],
        behavioral_constraints="\n".join(f"- {c}" for c in persona["behavioral_constraints"]),
    )


B0_SYSTEM_PROMPT = "You are a helpful assistant."


def build_messages(condition, persona, history, user_prompt, memory, ctx):
    """Assemble the message list sent to the generator for one turn.

    B0: no persona (generic system prompt) + history.
    C1: persona system prompt + history.
    C2/C3: persona system prompt + structured memory block + history.
    C4: identical messages to C1; verification is applied post-generation.
    The ONLY difference between C1 and C2 is the memory block; the 2x2 factorial
    is memory (C2/C3 yes, C1/C4 no) x verification (C3/C4 yes, C1/C2 no).
    """
    if condition == "B0":
        system = B0_SYSTEM_PROMPT
    else:
        system = build_system_prompt(ctx["prompts"]["generator_system"], persona)
        if condition in ("C2", "C3"):
            system += "\n\n" + memory_manager.render_memory_block(
                ctx["prompts"]["generator_memory"], memory)

    return [{"role": "system", "content": system}] + history + [
        {"role": "user", "content": user_prompt}]


def format_history_for_eval(history):
    """Plain-text transcript for judge/verifier prompts."""
    if not history:
        return "(start of conversation)"
    lines = []
    for m in history:
        speaker = "User" if m["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {m['content']}")
    return "\n".join(lines)
