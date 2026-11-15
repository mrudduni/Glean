"""LLM-as-judge for cached assistant answers, plus rule checks that need no LLM.

Usage: python judge.py [--dry-run] [--rounds 2] [--fields ...]
Scores each cached answer, regenerates failures (max --rounds), and writes
model/out/assistant_review.md. Without LLM vars only the rule checks run, and the
report says so.
"""
from __future__ import annotations

import argparse
import os
import json
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import cache
from cache import TAG_RE, call_llm, llm_env, llm_ready
from context import facts_for, load
from number_check import check_numbers
from paths import CONTENT_DIR, FIELDS, OUT_WEB, REPO, SCENARIO

CRITERIA = ["accuracy", "no_invented_numbers", "no_overclaiming", "no_forbidden_advice", "readability",
            "language", "source_tags"]
PASS_SCORE = 4  # of 5

OVERCLAIM = re.compile(r"\b(will|guarantee[sd]?|guaranteed|proven|prove[sd]?|ensures?|always|definitely|certainly|"
                       r"garantiza\w*|garantizad\w*|comprobad\w*|seguro que|siempre|definitivamente|sin duda)\b", re.I)
FORBIDDEN = re.compile(r"\b(pesticid\w*|herbicid\w*|insecticid\w*|fungicid\w*|glyphosate|atrazine|nitrogen rate|"
                       r"lb\.? ?(of )?n\b|water rights?|lawsuit|attorney|invest\w*|"
                       r"plaguicida\w*|herbicida\w*|derechos de agua|abogado|inversi[oó]n)\b", re.I)
ES_WORDS = {"el", "la", "los", "las", "de", "del", "que", "en", "es", "una", "un", "con", "por", "para", "se", "su"}
EN_WORDS = {"the", "of", "and", "is", "to", "in", "that", "for", "with", "may", "this", "are", "it", "on"}
FACT_ID = re.compile(r"\b(?:replay|drought|field|climate|water|neighbors|validation|glossary|scenario)\.[A-Za-z0-9_.|:-]+")
ROT_CODE = re.compile(r"\bR[0-6]\b")


def rule_checks(resp: dict, lang: str, facts: list[dict]) -> list[str]:
    a = resp["answer_md"]
    issues = []
    words = re.findall(r"[\w'’]+", a)
    if len(words) > 150:
        issues.append(f"{len(words)} words, over the 150 limit")
    if not TAG_RE.search(a):
        issues.append("no [TAG] source tag")
    bad = [n["text"] for n in check_numbers(a, [f for f in facts if f["value"] is not None]) if not n["verified"]]
    if bad:
        issues.append("unverified numbers: " + ", ".join(bad))
    if m := OVERCLAIM.search(re.sub(r"(?<![A-Za-z])(not|no|without|sin)\s+(a\s+)?(guarantees?|garant\w+)", "", a, flags=re.I)):
        issues.append(f"overclaiming word: '{m.group(0)}'")
    if m := FORBIDDEN.search(a):
        issues.append(f"forbidden topic: '{m.group(0)}'")
    if FACT_ID.search(a):
        issues.append("fact id leaked into the answer")
    if ROT_CODE.search(a):
        issues.append("rotation code (R1, R2...) in the answer")
    low = [w.lower() for w in words]
    es, en = sum(w in ES_WORDS for w in low), sum(w in EN_WORDS for w in low)
    if lang == "en" and es > en:
        issues.append("answer does not look English")
    if lang == "es" and en >= es:
        issues.append("answer does not look Spanish")
    return issues


JUDGE_SYSTEM = """You review answers written by a farm-planning assistant. Score the ANSWER against the FACTS and the RULES.
Return only JSON: {"accuracy":1-5,"no_invented_numbers":1-5,"no_overclaiming":1-5,"no_forbidden_advice":1-5,
"readability":1-5,"language":1-5,"source_tags":1-5,"issues":["short sentence each"]}.
5 is perfect. Meanings:
- accuracy: every claim matches the facts, nothing contradicts them or is stretched beyond them.
- no_invented_numbers: every number is in a facts line (rounding and mm to inches are fine).
- no_overclaiming: no "will", "guaranteed", "proven"; uses "may", "estimated", "in similar fields".
- no_forbidden_advice: no pesticide, herbicide or fertilizer rates, legal advice on water rights, or financial guarantees.
- readability: 8th-grade level, plain, under 150 words.
- language: the answer is written in {lang_name} and matches the question's language.
- source_tags: sentences that use a fact end with that fact's source tag in square brackets.
Judge honestly. List real problems in issues; use an empty list if there are none."""


def llm_judge(client, env, prompt, lang, question, answer, facts_text) -> dict:
    sys_msg = JUDGE_SYSTEM.replace("{lang_name}", cache.LANG_NAME[lang])
    user = f"QUESTION ({lang}): {question}\n\nFACTS:\n{facts_text}\n\nANSWER:\n{answer}"
    raw = call_llm(client, env, [{"role": "system", "content": sys_msg}, {"role": "user", "content": user}],
                   {"temperature": 0, "max_tokens": 500})
    m = re.search(r"\{.*\}", raw, re.S)
    try:
        d = json.loads(m.group(0))
        return {k: int(d[k]) for k in CRITERIA} | {"issues": list(d.get("issues", []))}
    except Exception:
        return {k: 0 for k in CRITERIA} | {"issues": ["judge returned unreadable output"]}


def judge_one(resp, lang, qtext, facts, facts_text, client, jenv, prompt, use_llm) -> dict:
    issues = rule_checks(resp, lang, facts)
    scores = None
    if use_llm:
        scores = llm_judge(client, jenv, prompt, lang, qtext, resp["answer_md"], facts_text)
        low = [k for k in CRITERIA if scores[k] < PASS_SCORE]
        issues += [f"judge: {i}" for i in scores["issues"]] + ([f"low score: {', '.join(low)}"] if low else [])
    return {"pass": not issues, "scores": scores, "issues": issues}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fields", nargs="*", default=FIELDS)
    ap.add_argument("--rounds", type=int, default=2)
    ap.add_argument("--dry-run", action="store_true", help="rule checks only, no LLM calls, no regeneration")
    ap.add_argument("--out", type=Path, default=OUT_WEB)
    ap.add_argument("--model-web", type=Path, default=OUT_WEB)
    ap.add_argument("--report", type=Path, default=REPO / "model" / "out" / "assistant_review.md")
    ap.add_argument("--rules-only", action="store_true", help="skip the LLM judge (quota gone) but still regenerate rule failures")
    ap.add_argument("--sleep", type=float, default=2.0)
    a = ap.parse_args()

    use_llm = llm_ready() and not a.dry_run and not a.rules_only
    can_regen = llm_ready(cache.gen_prefix()) and not a.dry_run
    env, client = llm_env(), None
    genv = llm_env(cache.gen_prefix())  # backend that regenerates failed answers
    gclient = None
    if use_llm:
        client = cache.make_client(env)
    if can_regen:
        gclient = cache.make_client(genv)
    jenv = {**env, "LLM_MODEL": os.environ.get("JUDGE_MODEL", "openai/gpt-oss-20b")}
    prompt = load(a.out / "assistant" / "prompt.json")
    qs = {q["id"]: q for q in load(CONTENT_DIR / "assistant_questions.json")["questions"]}
    sources = cache.load_sources()
    results = []  # rows
    regen_total = 0
    for fid in a.fields:
        path = cache.cache_path(fid, a.out)
        doc = load(path)
        ctx = load(a.out / "field" / fid / "assistant_context.json")
        facts = facts_for(ctx, SCENARIO)
        facts_text = "\n".join(f"- ({f['id']}) {f['text']} [{f['source']}]" for f in facts)
        top_ids = doc.get("top_rotations") or cache.rank_rotations(fid, a.model_web)
        for qid, by_lang in doc["answers"].items():
            for lang, resp in list(by_lang.items()):
                qtext = qs[qid]["text"][lang]
                verdict, rounds = judge_one(resp, lang, qtext, facts, facts_text, client, jenv, prompt, use_llm), 0
                while not verdict["pass"] and can_regen and rounds < a.rounds:
                    rounds += 1
                    regen_total += 1
                    time.sleep(a.sleep)
                    new = cache.generate(fid, qid, lang, ctx, prompt, qs, top_ids, sources, gclient, genv,
                                         feedback=verdict["issues"])
                    v2 = judge_one(new, lang, qtext, facts, facts_text, client, jenv, prompt, use_llm)
                    if v2["pass"] or len(v2["issues"]) <= len(verdict["issues"]):
                        resp, verdict = new, v2
                        by_lang[lang] = new
                results.append({"field": fid, "q": qid, "lang": lang, "words": len(re.findall(r"[\w'’]+", resp["answer_md"])),
                                "rounds": rounds, **verdict})
        if can_regen:
            path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf8")

    write_report(a.report, results, use_llm, regen_total, a.dry_run, doc["_meta"].get("mock", False))
    passed = sum(r["pass"] for r in results)
    print(f"{passed}/{len(results)} pass; regenerated {regen_total}; report {a.report}")


def write_report(path: Path, rows: list[dict], use_llm: bool, regen: int, dry: bool, mock_cache: bool):
    passed = sum(r["pass"] for r in rows)
    L = ["# Assistant answer review", "",
         f"Generated {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} by `model/assistant/judge.py`.", ""]
    if not use_llm:
        L += ["> **No LLM judge ran.** The LLM variables in `~/.glean/.env` (or `~/.fieldshift/.env`) were empty or `--dry-run` was set.",
              "> Only the rule checks ran (length, tags, verified numbers, banned words, language).", ""]
    if mock_cache:
        L += ["> **The cache under review is a dry-run cache** built from templates, not LLM output.", ""]
    L += [f"**{passed} of {len(rows)} answers pass.** Regenerations: {regen}. Pass needs every rule check clean"
          + (f" and every judge score at {PASS_SCORE} or more of 5." if use_llm else "."), "",
          "| Field | Q | Lang | Words | Regen rounds | Result | Scores (acc/num/claim/advice/read/lang/tags) |",
          "|---|---|---|---|---|---|---|"]
    for r in rows:
        s = r["scores"]
        sc = "/".join(str(s[k]) for k in CRITERIA) if s else "n/a"
        L.append(f"| {r['field']} | {r['q']} | {r['lang']} | {r['words']} | {r['rounds']} | {'pass' if r['pass'] else 'FAIL'} | {sc} |")
    bad = [r for r in rows if not r["pass"]]
    L += ["", "## Remaining issues", ""]
    L += [f"- **{r['field']} {r['q']} {r['lang']}**: " + "; ".join(r["issues"]) for r in bad] or ["None."]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(L) + "\n", encoding="utf8")


if __name__ == "__main__":
    main()
