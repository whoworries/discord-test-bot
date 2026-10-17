"""
Imports tweets from an X (Twitter) data archive into tweets.json for the bot's /tweet command.

Usage (from the bot folder):
    venv\\Scripts\\python import_tweets.py path\\to\\tweets.js        (Windows)
    venv/bin/python import_tweets.py path/to/tweets.js              (Pi)

tweets.js is in the archive's "data" folder. Running it again with a newer archive
only adds tweets that aren't saved yet. Keeps the account's own posts and its own
threads; skips retweets and replies to other people.
"""
import html
import json
import sys
from datetime import datetime
from pathlib import Path

HANDLE = "ractingting"
OUT = Path(__file__).parent / "tweets.json"


def load_archive(path):
    text = Path(path).read_text(encoding="utf-8")
    return json.loads(text[text.index("["):])   # strip "window.YTD.tweets.part0 = "


def keep(t):
    if t["full_text"].startswith("RT @"):
        return False                              # retweet
    if t.get("in_reply_to_status_id") and (t.get("in_reply_to_screen_name") or "").lower() != HANDLE:
        return False                              # reply to someone else
    return True


def main():
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(1)
    existing = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else []
    seen = {t["id"] for t in existing}
    added = 0
    for item in load_archive(sys.argv[1]):
        t = item["tweet"]
        if t["id_str"] in seen or not keep(t):
            continue
        created = datetime.strptime(t["created_at"], "%a %b %d %H:%M:%S %z %Y")
        existing.append({"id": t["id_str"], "text": html.unescape(t["full_text"]),
                         "date": created.isoformat()})
        seen.add(t["id_str"])
        added += 1
    existing.sort(key=lambda t: t["date"])
    OUT.write_text(json.dumps(existing, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"Added {added} new tweets ({len(existing)} total) -> {OUT.name}")


if __name__ == "__main__":
    main()
