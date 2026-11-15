"""Generate assistant_cache.json: q1-q6 x en/es for each field at cap300|actual.

Builds the prompt exactly as the web route does (README 9), calls the LLM through
the OpenAI SDK, runs the number check, retries once, and stores AskResponse objects.

Usage:
  python cache.py [--fields f1 f2] [--questions q1 q2] [--langs en es] [--force] [--dry-run]
--dry-run writes template answers built from the facts (no LLM call) and marks the
file _meta.mock = true. Never ship a dry-run cache.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import paths
from context import facts_block, facts_for, load, scenario_label
from number_check import check_numbers
from paths import CONTENT_DIR, DATA_WEB, FIELDS, OUT_WEB, SCENARIO

TAGS = ["POWER", "IMERG", "SMAP", "MODIS", "HLS", "ECOSTRESS", "GRACE", "SRTM", "SSURGO", "CSB", "NASS",
        "OpenET", "PRISM", "USGS", "CoCoRaHS", "GAEZ", "AMS", "FAO56", "MODEL"]
TAG_RE = re.compile(r"\[(" + "|".join(TAGS) + r")\]")
LANG_NAME = {"en": "English", "es": "Spanish"}
RETRY_MSG = "Rewrite your answer using only numbers from the facts."


def llm_env() -> dict:
    return {k: os.environ.get(k, "") for k in ("LLM_PROVIDER", "LLM_BASE_URL", "LLM_MODEL", "LLM_API_KEY")}


def llm_ready() -> bool:
    return all(llm_env().values())


# ---- prompt building -------------------------------------------------------------

def rank_rotations(fid: str, model_web: Path) -> list[str]:
    ctx = load(model_web / "field" / fid / "assistant_context.json")
    cur = ctx["rotation_names"]["R0"].replace(" (current)", "")
    """Default weights (all sliders equal): R0 plus the top 3 feasible rotations by mean norm."""
    strat = load(model_web / "field" / fid / "strategies.json")["scenarios"][SCENARIO]
    scored = []
    for e in strat:
        if e["rotation_id"] == "R0" or not e["feasible"] or ctx["rotation_names"][e["rotation_id"]] == cur:
            continue
        norms = [c["norm"] for c in e["criteria"].values()]
        scored.append((-sum(norms) / len(norms), e["rotation_id"]))
    scored.sort()
    return [r for _, r in scored[:3]] + ["R0"]


def top_rotations_text(ctx: dict, ids: list[str]) -> str:
    names = ctx["rotation_names"]
    return ", ".join(names[r] for r in ids)


def prompt_facts(ctx: dict, scenario: str, top_ids: list[str]) -> list[dict]:
    """Scenario facts, limited to the strategies on screen (plus alfalfa for 'why not alfalfa')."""
    keep = set(top_ids) | {"R4"}
    return [f for f in facts_for(ctx, scenario) if (f.get("rotation_id") is None or f["rotation_id"] in keep)]


def build_messages(prompt: dict, ctx: dict, lang: str, scenario: str, top_ids: list[str], question: str,
                   history: list[dict] | None = None) -> list[dict]:
    system = (prompt["system"]
              .replace("{lang_name}", LANG_NAME[lang])
              .replace("{field_name}", ctx["field_name"])
              .replace("{scenario_label}", scenario_label(scenario))
              .replace("{top_rotations}", top_rotations_text(ctx, top_ids))
              .replace("{facts_block}", facts_block(prompt_facts(ctx, scenario, top_ids))))
    return [{"role": "system", "content": system}, *(history or []), {"role": "user", "content": question}]


def checkable(ctx: dict, scenario: str, top_ids: list[str]) -> list[dict]:
    return [f for f in prompt_facts(ctx, scenario, top_ids) if f["value"] is not None]


# ---- LLM call --------------------------------------------------------------------

def clean_text(t: str) -> str:
    """Plain spaces and hyphens; models like to emit narrow no-break spaces and non-breaking hyphens."""
    for a, b in ((" ", " "), (" ", " "), ("‑", "-"), ("‒", "-")):
        t = t.replace(a, b)
    return t.strip()


def call_llm(client, env: dict, messages: list[dict], prompt: dict, max_tries: int = 8) -> str:
    import openai
    for n in range(max_tries):
        try:
            extra = {}
            effort = os.environ.get("LLM_REASONING_EFFORT", "low" if "gpt-oss" in env["LLM_MODEL"] else "")
            if effort:
                extra["extra_body"] = {"reasoning_effort": effort}
            r = client.chat.completions.create(
                model=env["LLM_MODEL"], messages=messages,
                temperature=prompt["temperature"], max_tokens=prompt["max_tokens"], **extra)
            return clean_text(r.choices[0].message.content or "")
        except openai.RateLimitError as e:
            wait = min(90, 4 * 2 ** n)
            m = re.search(r"try again in (?:(\d+)m)?([\d.]+)(ms|s)", str(e))
            if m:
                wait = (int(m.group(1) or 0) * 60 + float(m.group(2)) / (1000 if m.group(3) == "ms" else 1)) + 1
            print(f"  429, waiting {wait:.0f}s: {str(e)[60:330]}", flush=True)
            time.sleep(wait)
        except (openai.APIConnectionError, openai.APITimeoutError, openai.InternalServerError):
            time.sleep(2 ** n)
    raise RuntimeError("LLM call failed after retries")


# ---- dry run ---------------------------------------------------------------------

def dry_answer(ctx: dict, q: str, lang: str, top_ids: list[str]) -> str:
    """Template answer from facts. Only for exercising the pipeline."""
    by = {f["id"]: f for f in facts_for(ctx, SCENARIO)}
    names = ctx["rotation_names"]

    def fx(key):
        f = by.get(key)
        return f"{f['value']:g}" if f and f["value"] is not None else "?"

    top = top_ids[0]
    en = lang == "en"
    p = f"replay.{top}.{SCENARIO}"
    if q == "q1":
        return (f"{'The top strategy is' if en else 'La primera estrategia es'} {names[top]}. "
                f"{'It may use about' if en else 'Podria usar cerca de'} {fx(p + '.irrigation_mm_mean')} mm "
                f"{'of irrigation per year' if en else 'de riego por año'} [MODEL]. "
                f"{'Estimated income is about' if en else 'El ingreso estimado es cerca de'} ${fx(p + '.revenue_usd_ac_mean')}/ac [MODEL].")
    if q == "q2":
        cur = f"replay.R0.{SCENARIO}.irrigation_mm_mean"
        return (f"{'The current rotation may use' if en else 'La rotacion actual podria usar'} {fx(cur)} mm [MODEL]. "
                f"{names[top]} {'may use' if en else 'podria usar'} {fx(p + '.irrigation_mm_mean')} mm [MODEL].")
    if q == "q3":
        f = by.get(f"replay.R4.{SCENARIO}.irrigation_mm_mean")
        if f:
            return (f"{'Alfalfa may use about' if en else 'La alfalfa podria usar cerca de'} {f['value']:g} mm "
                    f"{'of irrigation per year' if en else 'de riego por año'} [MODEL].")
        return "Alfalfa is not feasible with this water limit [MODEL]." if en else "La alfalfa no es viable con este limite de agua [MODEL]."
    if q == "q4":
        return (f"{'In 2012, ' if en else 'En 2012, '}{names[top]} "
                f"{'may have earned about' if en else 'podria haber ganado cerca de'} "
                f"${fx(f'drought.2012.{top}.revenue_usd_ac')}/ac [MODEL].")
    if q == "q5":
        return (f"{'Model water use differed from OpenET by' if en else 'El uso de agua del modelo difirio de OpenET en'} "
                f"{fx('validation.et_vs_openet')}% [OpenET]. "
                f"{'These are estimates, not forecasts.' if en else 'Son estimaciones, no pronosticos.'} [MODEL]")
    return ("Ask a K-State Research and Extension agent about water limits, seed and market access before switching [MODEL]."
            if en else "Consulte a un agente de extension de K-State sobre limites de agua, semilla y mercado antes de cambiar [MODEL].")


# ---- response assembly -----------------------------------------------------------

def load_sources() -> dict:
    p = DATA_WEB / "sources.json"
    return {s["tag"]: s for s in load(p)["sources"]} if p.exists() else {}


def citations(answer: str, sources: dict) -> list[dict]:
    seen, out = set(), []
    for t in TAG_RE.findall(answer):
        if t in seen:
            continue
        seen.add(t)
        s = sources.get(t, {})
        out.append({"tag": t, "name": s.get("name", t), "url": s.get("url", "")})
    return out


def make_response(answer: str, numbers: list[dict], sources: dict, provider: str, model: str | None) -> dict:
    return {"answer_md": answer, "citations": citations(answer, sources), "numbers": numbers,
            "cached": True, "provider": provider, "model": model}


def generate(fid: str, qid: str, lang: str, ctx: dict, prompt: dict, questions: dict, top_ids: list[str],
             sources: dict, client=None, env: dict | None = None, dry: bool = False,
             feedback: list[str] | None = None) -> dict:
    facts = checkable(ctx, SCENARIO, top_ids)
    qtext = questions[qid]["text"][lang]
    if dry:
        ans = dry_answer(ctx, qid, lang, top_ids)
        return make_response(ans, check_numbers(ans, facts), sources, "cache", "dry-run")
    msgs = build_messages(prompt, ctx, lang, SCENARIO, top_ids, qtext)
    if feedback:
        msgs[-1]["content"] += "\n\nFix these problems from a reviewer: " + "; ".join(feedback)
    ans = call_llm(client, env, msgs, prompt)
    nums = check_numbers(ans, facts)
    bad = [n for n in nums if not n["verified"]]
    if bad:
        retry = msgs + [{"role": "assistant", "content": ans}, {"role": "user", "content": RETRY_MSG}]
        ans2 = call_llm(client, env, retry, prompt)
        nums2 = check_numbers(ans2, facts)
        if sum(not n["verified"] for n in nums2) <= len(bad):
            ans, nums = ans2, nums2
    return make_response(ans, nums, sources, env["LLM_PROVIDER"], env["LLM_MODEL"])


def cache_path(fid: str, out: Path) -> Path:
    return out / "field" / fid / "assistant_cache.json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fields", nargs="*", default=FIELDS)
    ap.add_argument("--questions", nargs="*")
    ap.add_argument("--langs", nargs="*", default=["en", "es"])
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--out", type=Path, default=OUT_WEB)
    ap.add_argument("--model-web", type=Path, default=OUT_WEB)
    ap.add_argument("--sleep", type=float, default=float(os.environ.get("LLM_SLEEP", "4")))
    a = ap.parse_args()

    dry = a.dry_run
    env = llm_env()
    if not dry and not llm_ready():
        missing = [k for k, v in env.items() if not v]
        raise SystemExit(f"LLM vars empty in {paths.ENV_FILE}: {', '.join(missing)}. Fill them or pass --dry-run.")
    client = None
    if not dry:
        from openai import OpenAI
        client = OpenAI(base_url=env["LLM_BASE_URL"], api_key=env["LLM_API_KEY"], timeout=60, max_retries=0)
    prompt = load(a.out / "assistant" / "prompt.json")
    qs = {q["id"]: q for q in load(CONTENT_DIR / "assistant_questions.json")["questions"]}
    sources = load_sources()
    for fid in a.fields:
        ctx = load(a.out / "field" / fid / "assistant_context.json")
        top_ids = rank_rotations(fid, a.model_web)
        path = cache_path(fid, a.out)
        doc = load(path) if path.exists() and not a.force else None
        if doc and doc["_meta"].get("mock") != dry:
            doc = None
        answers = doc["answers"] if doc else {}
        for qid in (a.questions or list(qs)):
            for lang in a.langs:
                if lang in answers.get(qid, {}):
                    continue
                print(f"{fid} {qid} {lang}")
                r = generate(fid, qid, lang, ctx, prompt, qs, top_ids, sources, client, env, dry)
                answers.setdefault(qid, {})[lang] = r
                if not dry:
                    time.sleep(a.sleep)
        out = {"_meta": {"schema": "assistant_cache@1", "mock": dry,
                         "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                         "generator": "model/assistant/cache.py"},
               "field_id": fid, "scenario": SCENARIO, "top_rotations": top_ids, "answers": answers}
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(out, ensure_ascii=False, indent=1) + "\n", encoding="utf8")
        bad = sum(not n["verified"] for q in answers.values() for r in q.values() for n in r["numbers"])
        print(f"{fid}: {sum(len(q) for q in answers.values())} answers, {bad} unverified numbers")


if __name__ == "__main__":
    main()
