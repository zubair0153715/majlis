# Majlis — Free AI Meeting Notes

**مجلس — free, unlimited meeting notes on the web. No account, no card, no subscription.**

Paste a transcript (or type notes live during the meeting) and Majlis
turns it into structured minutes: decisions, owned action items with
due dates, open questions, talk-share stats, and a WhatsApp-ready
follow-up draft — in English, Roman-Urdu or Urdu script.

## Why it exists

Premium AI notetakers (Granola, Otter, Fireflies) charge $8–35/user/month,
lock your own notes older than 30 days behind a paywall, have no web
version, keep no audio to check notes against, and don't speak Urdu.
Majlis is the free, open, original alternative — built clean-room from
public pricing pages and review complaints only. See the full gap
analysis in `../market-gaps/daily/2026-10-31-majlis.md` (in the
operator's workspace).

## What it does

- **Structure** — parses `Name: ...` turns, extracts decisions
  ("we agreed…", "decided:…"), action items ("I will…", "Sara
  will…") with owner + due date, and open questions — every item
  cites the transcript line it came from.
- **Stats** — word count, turns, speakers, talk-share % and an
  estimated length at 150 words/min. All arithmetic, hand-verified.
- **Follow-up** — a WhatsApp-ready draft listing decisions + who
  owes what by when.
- **Export** — download the minutes as Markdown, with checkboxes.
- **History** — meetings save in your own browser (localStorage);
  nothing is stored on any server, so there is no 30-day lock.
- **AI polish (optional)** — Gemini rewrites the summary in the
  meeting language. It may only reword what is already there; it
  never invents decisions, owners or dates. Works fully without a key.

## Honest limits

- Majlis does **not** record audio and does **not** transcribe speech.
  Paste a transcript from any recorder or free transcription tool, or
  type notes live. No invented transcript, no fake accuracy claim.
- Always tell the people in the meeting that you are taking notes.

## Run it

Live: https://clinic-demo.fastapicloud.dev/majlis

Local (from the clinic-demo app):

```bash
python -m pytest # no — see below
python tests/verify.py   # 50 checks, no network, no key needed
```

The app module lives in `majlis/` (`engine.py`, `gemini.py`,
`pages.py`, `routes.py`) and wires into the FastAPI app with two
lines in `app/main.py`. Tests run against the engine + routes
directly; the only network call is the optional Gemini polish,
which reads `GEMINI_API_KEY` from the environment at call time.

## Verification

`tests/verify.py` — **50/50 pass** (2026-10-31). Hand-computed
fixture: 50 words; Ayesha 24 (48%) / Bilal 26 (52%); 6 turns;
2 decisions; 3 actions (owners Bilal/Sara/Bilal; dues
Friday/tomorrow/Monday); 2 questions; ~0.3 min at 150 wpm.

## License

MIT. Original code, own name, no trademarks of any notetaker
product used anywhere.
