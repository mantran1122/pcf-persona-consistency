"""Persona Verification (condition C3): accept / revise / reject a candidate response.

Original responses are never deleted: both the pre- and post-verification texts are kept
in the verification audit dict stored inside the raw record and mirrored to
outputs/verified_responses/.
"""

import json

from . import build_dialogues, utils
from .utils import VERIFIED_DIR

VALID_DECISIONS = {"accept", "revise", "reject"}
VALID_VIOLATIONS = {"role_breaking", "style_drift", "memory_failure", "context_confusion",
                    "self_contradiction", "domain_drift", "meta_disclosure", "constraint_violation"}


def verify_response(persona, history, user_prompt, response, ctx):
    prompt = ctx["prompts"]["verification"].format(
        persona_profile=json.dumps(persona, ensure_ascii=False, indent=2),
        history=build_dialogues.format_history_for_eval(history),
        user_prompt=user_prompt,
        response=response,
    )
    dry = json.dumps({"decision": "accept", "violations": [], "severity": "none",
                      "suggested_revision": ""})
    result = utils.chat_completion(ctx["models"]["verifier"],
                                   [{"role": "user", "content": prompt}], dry_run_text=dry)
    verdict = utils.parse_llm_json(result["text"])
    if verdict.get("decision") not in VALID_DECISIONS:
        raise ValueError(f"Invalid verifier decision: {verdict.get('decision')!r}")
    verdict["violations"] = [v for v in verdict.get("violations", []) if v in VALID_VIOLATIONS]
    verdict["latency_seconds"] = result["latency_seconds"]
    return verdict


def verify_and_maybe_revise(persona, history, user_prompt, response, ctx,
                            condition="C3", memory=None, generator_cfg=None):
    """Returns (final_response, audit). Revise uses the verifier's suggested revision;
    reject triggers one regeneration by the generator. Bounded by max_revisions.

    generator_cfg: the *same* generator config (G1 or G2) that produced `response`, so a
    reject-regeneration stays with the dialogue's own generator. Defaults to G1 for callers
    that don't pass it explicitly."""
    generator_cfg = generator_cfg or ctx["models"]["generators"]["G1"]
    logger = utils.get_logger()
    max_revisions = ctx["experiment"].get("max_revisions", 1)
    audit = {"original_response": response, "rounds": []}
    final = response

    for round_i in range(max_revisions + 1):
        verdict = verify_response(persona, history, user_prompt, final, ctx)
        audit["rounds"].append({"response": final, "verdict": verdict})

        if verdict["decision"] == "accept" or round_i == max_revisions:
            break
        if verdict["decision"] == "revise" and verdict.get("suggested_revision"):
            final = verdict["suggested_revision"]
            logger.info("verifier revised response (violations: %s)", verdict["violations"])
        elif verdict["decision"] == "reject":
            # Regenerate with the condition's own message shape (C4 has no memory,
            # C3 needs its memory block re-attached).
            messages = build_dialogues.build_messages(condition, persona, history,
                                                      user_prompt, memory, ctx)
            messages[0]["content"] += ("\n\nIMPORTANT: Your previous draft was rejected for: "
                                       + ", ".join(verdict["violations"])
                                       + ". Produce a fully in-character response avoiding these issues.")
            result = utils.chat_completion(generator_cfg, messages,
                                           dry_run_text="[DRY RUN] regenerated response")
            final = result["text"]
            logger.info("verifier rejected response; regenerated")
        else:
            break

    audit["final_response"] = final
    return final, audit


def export_verified(record_id, audit):
    utils.save_json(audit, VERIFIED_DIR / f"{record_id}.json")
