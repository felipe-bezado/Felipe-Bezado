"""Render an arcade-style contribution streak card with grace days.

A streak survives up to GRACE_DAYS empty days in a row; the next empty day breaks it.
Usage: GITHUB_TOKEN=... python scripts/streak_card.py <login> <out.svg>
"""
import base64
import json
import os
import sys
import urllib.request
from datetime import date, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

GRACE_DAYS = 3
TZ = ZoneInfo("America/Sao_Paulo")
FONT_FILE = Path(__file__).resolve().parent.parent / "assets" / "fonts" / "ps2p.woff2"

QUERY = """
query($login: String!, $from: DateTime!, $to: DateTime!) {
  user(login: $login) {
    createdAt
    contributionsCollection(from: $from, to: $to) {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
    }
  }
}"""


def graphql(token, variables):
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": variables}).encode(),
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    if "errors" in payload:
        raise RuntimeError(payload["errors"])
    return payload["data"]["user"]


def fetch_days(login, token, today):
    """Return {date: count} from account creation to today, one-year windows at a time."""
    created = graphql(token, {"login": login, "from": f"{today}T00:00:00Z", "to": f"{today}T23:59:59Z"})["createdAt"]
    start = date.fromisoformat(created[:10])
    days = {}
    while start <= today:
        end = min(start + timedelta(days=364), today)
        user = graphql(token, {"login": login, "from": f"{start}T00:00:00Z", "to": f"{end}T23:59:59Z"})
        for week in user["contributionsCollection"]["contributionCalendar"]["weeks"]:
            for d in week["contributionDays"]:
                days[date.fromisoformat(d["date"])] = d["contributionCount"]
        start = end + timedelta(days=1)
    return days


def streaks(days, today):
    """Split active days into streaks, where a gap of more than GRACE_DAYS empty days breaks one."""
    active = sorted(d for d, c in days.items() if c > 0 and d <= today)
    runs = []
    for d in active:
        if runs and (d - runs[-1][1]).days - 1 <= GRACE_DAYS:
            runs[-1][1] = d
            runs[-1][2] += 1
        else:
            runs.append([d, d, 1])
    current = None
    if runs:
        # Today is still playable, so an empty today does not cost a heart yet.
        empty_since_last = (today - runs[-1][1]).days - (0 if days.get(today, 0) else 1)
        if (today - runs[-1][1]).days - 1 <= GRACE_DAYS:
            current = (*runs[-1], max(empty_since_last, 0))
    longest = max(runs, key=lambda r: ((r[1] - r[0]).days, r[2], r[1]), default=None)
    return current, longest


def span(run):
    return (run[1] - run[0]).days + 1


def heart(x, y, px, fill):
    shape = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
    return "".join(
        f'<rect x="{x + c * px}" y="{y + r * px}" width="{px}" height="{px}" fill="{fill}"/>'
        for r, row in enumerate(shape)
        for c, ch in enumerate(row)
        if ch == "X"
    )


def render(total, first_day, current, longest, today):
    font = base64.b64encode(FONT_FILE.read_bytes()).decode()
    pink, cyan, yellow, purple, dim = "#ff2a6d", "#05d9e8", "#f9f871", "#b967ff", "#3a2a5e"
    w, h = 900, 250
    cur_days = span(current) if current else 0
    lives = GRACE_DAYS - current[3] if current else 0
    hearts = "".join(
        heart(450 - (GRACE_DAYS * 34 - 8) // 2 + i * 34, 176, 4, pink if i < lives else dim) for i in range(GRACE_DAYS)
    )
    cur_sub = f"since {current[0]:%b %d, %Y}" if current else "insert coin to start a combo"
    best_days = span(longest) if longest else 0
    best_sub = f"{longest[0]:%b %d, %Y} - {longest[1]:%b %d, %Y}" if longest else "-"
    status = "COMBO ALIVE" if current and lives else ("LAST LIFE!" if current else "GAME OVER")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <style>@font-face{{font-family:'PS2P';src:url(data:font/woff2;base64,{font}) format('woff2');}}
  text{{font-family:'PS2P',monospace}} .s{{font-family:'Segoe UI',-apple-system,'Helvetica Neue',Arial,sans-serif;font-weight:600}}</style>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset="1" stop-color="#241056"/></linearGradient>
  <filter id="glow" x="-20%" y="-50%" width="140%" height="200%"><feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
</defs>
<rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="13" fill="none" stroke="{purple}" stroke-opacity="0.55" stroke-width="3"/>
<line x1="300" y1="40" x2="300" y2="{h - 40}" stroke="{purple}" stroke-opacity="0.4" stroke-dasharray="4 6"/>
<line x1="600" y1="40" x2="600" y2="{h - 40}" stroke="{purple}" stroke-opacity="0.4" stroke-dasharray="4 6"/>

<text x="150" y="62" text-anchor="middle" font-size="11" fill="{cyan}">TOTAL XP</text>
<text x="150" y="122" text-anchor="middle" font-size="34" fill="#fff" filter="url(#glow)">{total:,}</text>
<text x="150" y="152" text-anchor="middle" font-size="9" fill="{cyan}">CONTRIBUTIONS</text>
<text class="s" x="150" y="188" text-anchor="middle" font-size="13" fill="#c9c3ea">since {first_day.strftime("%b %Y")}</text>

<text x="450" y="62" text-anchor="middle" font-size="11" fill="{yellow}">CURRENT COMBO</text>
<text x="450" y="122" text-anchor="middle" font-size="44" fill="{yellow}" filter="url(#glow)">{cur_days}<animate attributeName="opacity" values="1;0.75;1" dur="1.6s" repeatCount="indefinite"/></text>
<text x="450" y="152" text-anchor="middle" font-size="9" fill="{yellow}">{"DAY" if cur_days == 1 else "DAYS"} · {status}</text>
{hearts}
<text class="s" x="450" y="224" text-anchor="middle" font-size="12" fill="#c9c3ea">{cur_sub} · {GRACE_DAYS} grace days, 1 heart each</text>

<text x="750" y="62" text-anchor="middle" font-size="11" fill="{pink}">HIGH SCORE</text>
<text x="750" y="122" text-anchor="middle" font-size="34" fill="#fff" filter="url(#glow)">{best_days}</text>
<text x="750" y="152" text-anchor="middle" font-size="9" fill="{pink}">DAY COMBO</text>
<text class="s" x="750" y="188" text-anchor="middle" font-size="13" fill="#c9c3ea">{best_sub}</text>
<text class="s" x="{w - 18}" y="{h - 12}" text-anchor="end" font-size="10" fill="#6d5fa0">updated {today:%Y-%m-%d}</text>
</svg>
"""


def main():
    login, out = sys.argv[1], Path(sys.argv[2])
    today = datetime.now(TZ).date()
    days = fetch_days(login, os.environ["GITHUB_TOKEN"], today)
    current, longest = streaks(days, today)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(render(sum(days.values()), min(days), current, longest, today), encoding="utf-8")
    print(f"total={sum(days.values())} current={current} longest={longest}")


if __name__ == "__main__":
    main()
