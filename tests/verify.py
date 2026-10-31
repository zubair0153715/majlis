"""Majlis verification — hand-computed fixtures, no AI needed.

Fixture transcript (hand-counted):
  L1 Ayesha: "Let's decide the launch date today. We agreed to launch
     on 5 November."  -> 6 + 7 = 13 words
  L2 Bilal: "I will prepare the pricing sheet by Friday." -> 8 words
  L3 Ayesha: "Sara will call the printer tomorrow." -> 6 words
  L4 Bilal: "Should we include the Urdu flyer? Decided: yes, include
     it." -> 6 + 4 = 10 words
  L5 Ayesha: "What about the stall booking?" -> 5 words
  L6 Bilal: "I need to confirm the stall by Monday." -> 8 words
Totals: 50 words; Ayesha 13+6+5 = 24 (48%); Bilal 8+10+8 = 26 (52%);
6 turns; 2 speakers; est. 50/150 = 0.3 min.
Decisions: L1 "We agreed..." + L4 "Decided: yes..." = 2.
Actions: L2 (Bilal, by Friday), L3 (Sara, tomorrow), L6 (Bilal, by
Monday) = 3. Questions: L4 "Should we..." + L5 = 2.
"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "clinic-demo"))

from app.majlis import engine
from app.majlis.routes import structure as route_structure
from app.majlis.pages import MAJLIS_HTML

FIXTURE = (
    "Ayesha: Let's decide the launch date today. We agreed to launch "
    "on 5 November.\n"
    "Bilal: I will prepare the pricing sheet by Friday.\n"
    "Ayesha: Sara will call the printer tomorrow.\n"
    "Bilal: Should we include the Urdu flyer? Decided: yes, include it.\n"
    "Ayesha: What about the stall booking?\n"
    "Bilal: I need to confirm the stall by Monday."
)

passed = failed = 0


def check(name, cond, extra=""):
    global passed, failed
    if cond:
        passed += 1
        print(f"PASS {name}")
    else:
        failed += 1
        print(f"FAIL {name} {extra}")


# --- parsing ---
turns = engine.parse_turns(FIXTURE)
check("turns == 6", len(turns) == 6, f"got {len(turns)}")
check("speakers in order",
      [t["speaker"] for t in turns] ==
      ["Ayesha", "Bilal", "Ayesha", "Bilal", "Ayesha", "Bilal"])
check("turn line numbers", [t["line"] for t in turns] == [1, 2, 3, 4, 5, 6])

t2 = engine.parse_turns("plain first line\nZubair - hello there\n"
                        "continuation line")
check("dash speaker + continuation + unknown",
      len(t2) == 2 and t2[0]["speaker"] == "Unknown"
      and t2[0]["text"] == "plain first line"
      and t2[1]["speaker"] == "Zubair"
      and "continuation line" in t2[1]["text"])

# --- stats (hand-computed) ---
st = engine.stats(turns)
check("total words == 50", st["words"] == 50, f"got {st['words']}")
check("turns == 6", st["turns"] == 6)
check("speakers == 2", st["speakers"] == 2)
check("share order Bilal first (26 words)",
      st["share"][0] == {"speaker": "Bilal", "words": 26, "pct": 52},
      f"got {st['share']}")
check("share Ayesha second (24 words, 48%)",
      st["share"][1] == {"speaker": "Ayesha", "words": 24, "pct": 48},
      f"got {st['share']}")
check("est minutes == 0.3", st["est_minutes"] == 0.3,
      f"got {st['est_minutes']}")

# --- classification ---
decisions, actions, questions = engine.analyse(turns)
check("decisions == 2", len(decisions) == 2, f"got {len(decisions)}")
check("decision lines 1 and 4",
      [d["line"] for d in decisions] == [1, 4])
check("decision texts",
      "agreed to launch on 5 November" in decisions[0]["text"]
      and "Decided: yes, include it." in decisions[1]["text"])
check("actions == 3", len(actions) == 3, f"got {len(actions)}")
check("action owners Bilal/Sara/Bilal",
      [a["owner"] for a in actions] == ["Bilal", "Sara", "Bilal"],
      f"got {[a['owner'] for a in actions]}")
check("action dues Friday/tomorrow/Monday",
      [a["due"] for a in actions] == ["Friday", "tomorrow", "Monday"],
      f"got {[a['due'] for a in actions]}")
check("action lines 2,3,6", [a["line"] for a in actions] == [2, 3, 6])
check("questions == 2", len(questions) == 2, f"got {len(questions)}")
check("question lines 4 and 5",
      [q["line"] for q in questions] == [4, 5])

# --- full pipeline ---
res = engine.structure_meeting({"title": "Launch sync", "date": "2026-10-31",
                                "mtype": "team", "language": "en",
                                "transcript": FIXTURE})
check("pipeline ok", res["ok"] is True)
check("pipeline title/date kept",
      res["title"] == "Launch sync" and res["date"] == "2026-10-31")
md = res["markdown"]
check("markdown has Decisions section", "## Decisions" in md)
check("markdown action checkbox + owner + due",
      "- [ ] I will prepare the pricing sheet by Friday. — Bilal, due Friday (line 2)" in md)
check("markdown line cites", "(line 1)" in md and "(line 4)" in md)
check("markdown has transcript", "## Transcript" in md
      and "Ayesha: Let's decide" in md)
fu = res["followup"]
check("follow-up has Decisions + Action items",
      "Decisions:" in fu and "Action items:" in fu)
check("follow-up lists owner + due",
      "Bilal, by Friday" in fu and "Sara, by tomorrow" in fu)

# --- languages ---
res_ur = engine.structure_meeting({"title": "M", "language": "ur",
                                   "transcript": FIXTURE})
check("urdu headings", "## فیصلے" in res_ur["markdown"]
      and "## ذمہ داریاں" in res_ur["markdown"])
check("urdu follow-up heading", "فالو اپ" in res_ur["followup"])
res_ro = engine.structure_meeting({"title": "M", "language": "roman",
                                   "transcript": FIXTURE})
check("roman headings", "## Faislay" in res_ro["markdown"]
      and "## Kaam (Action items)" in res_ro["markdown"])
res_bad = engine.structure_meeting({"title": "M", "language": "xx",
                                    "transcript": FIXTURE})
check("unknown language falls back to en",
      res_bad["language"] == "en" and "## Decisions" in res_bad["markdown"])
res_notype = engine.structure_meeting({"title": "M", "mtype": "nope",
                                       "transcript": FIXTURE})
check("unknown type falls back to other", res_notype["mtype"] == "other")
res_notitle = engine.structure_meeting({"title": "",
                                        "transcript": FIXTURE})
check("empty title -> Untitled meeting",
      res_notitle["title"] == "Untitled meeting")

# --- caps ---
check("transcript cap",
      engine.check_caps({"transcript": "x" * 100_001}) is not None)
check("transcript at cap ok",
      engine.check_caps({"transcript": "x" * 100_000}) is None)
check("title cap",
      engine.check_caps({"title": "x" * 201, "transcript": "hi"}) is not None)
check("empty input no cap error",
      engine.check_caps({"title": "", "transcript": ""}) is None)

# --- edge cases ---
check("empty transcript -> zero stats",
      engine.stats([]) == {"words": 0, "turns": 0, "speakers": 0,
                           "share": [], "est_minutes": 0})
check("no decisions/actions -> follow-up says so",
      "No decisions recorded." in engine.followup_message(
          "T", "", [], [], "en"))
check("decided-line as own line joins previous turn",
      engine.parse_turns("A: hello\nDecided: yes")[0]["text"] ==
      "hello Decided: yes")

# --- routes (call the handler functions directly) ---
resp = asyncio.run(route_structure(title="T", date="", mtype="team",
                                   language="en", transcript=""))
check("route rejects empty transcript (400)",
      resp.status_code == 400)
resp = asyncio.run(route_structure(title="T", date="2026-10-31",
                                   mtype="team", language="en",
                                   transcript=FIXTURE))
check("route accepts fixture (dict result)", isinstance(resp, dict))
check("route body actions == 3", len(resp["actions"]) == 3)
check("route body stats words == 50", resp["stats"]["words"] == 50)

# --- page: user content is escaped client-side ---
check("page defines esc()", "const esc=" in MAJLIS_HTML)
check("page escapes title/decisions in output",
      "esc(d.title)" in MAJLIS_HTML and "esc(x.text)" in MAJLIS_HTML)
check("page states no-audio limit",
      "does NOT" in MAJLIS_HTML and "record audio" in MAJLIS_HTML
      and "transcribe speech" in MAJLIS_HTML)
check("page has consent reminder", "Consent:" in MAJLIS_HTML)
check("page has localStorage history",
      "localStorage.getItem('majlis_hist')" in MAJLIS_HTML)
check("page has sample meeting", "Load a sample meeting" in MAJLIS_HTML)

print(f"\n{passed} passed, {failed} failed")
sys.exit(1 if failed else 0)
