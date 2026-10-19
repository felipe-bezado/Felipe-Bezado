"""Render the arcade profile cards from the GitHub contribution calendar.

streak.svg: a streak survives up to GRACE_DAYS empty days in a row; the next empty day breaks it.
snake.svg: a snake eats every contribution cell of the last year and grows one block per cell.
Usage: GITHUB_TOKEN=... python scripts/profile_cards.py <login> <out_dir>
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


PITCH, CELL, WEEKS = 15, 11, 53
START_LEN, MAX_LEN, STEP_S, PAUSE_S = 3, 60, 0.09, 2.5
LEVELS = ["#1b0f3b", "#4a1a6b", "#8a1f7a", "#c2185b", "#ff2a6d"]


def calendar_grid(days, today):
    """Last 53 weeks as {(col, row): count}, Sunday-first like GitHub's graph."""
    first = today - timedelta(days=(today.weekday() + 1) % 7 + 7 * (WEEKS - 1))
    grid = {}
    d = first
    while d <= today:
        grid[((d - first).days // 7, (d - first).days % 7)] = days.get(d, 0)
        d += timedelta(days=1)
    return grid


def level(count, counts):
    if not count:
        return 0
    ranked = sorted(counts)
    q = sum(c <= count for c in ranked) / len(ranked)
    return 1 + min(int(q * 4 - 1e-9), 3)


def route(grid):
    """Greedy nearest-target walk over the grid; returns head cells per step and the step each target is eaten."""
    targets = {cell for cell, c in grid.items() if c}
    pos, steps, eaten_at = (-START_LEN, 0), [], {}
    for k in range(START_LEN + 1):
        steps.append((-START_LEN + k, 0))
    pos = steps[-1]
    while targets:
        nxt = min(targets, key=lambda t: (abs(t[0] - pos[0]) + abs(t[1] - pos[1]), t))
        while pos[0] != nxt[0]:
            pos = (pos[0] + (1 if nxt[0] > pos[0] else -1), pos[1])
            steps.append(pos)
            if pos in targets:
                targets.discard(pos)
                eaten_at[pos] = len(steps) - 1
        while pos[1] != nxt[1]:
            pos = (pos[0], pos[1] + (1 if nxt[1] > pos[1] else -1))
            steps.append(pos)
            if pos in targets:
                targets.discard(pos)
                eaten_at[pos] = len(steps) - 1
    while pos[0] < WEEKS + START_LEN + 1 and len(eaten_at) == 0:
        pos = (pos[0] + 1, pos[1])
        steps.append(pos)
    return steps, eaten_at


def render_snake(days, today, start_offset=0.0):
    w, h = 900, 175
    x0, y0 = (w - WEEKS * PITCH) // 2, 38
    grid = calendar_grid(days, today)
    counts = [c for c in grid.values() if c]
    steps, eaten_at = route(grid)
    n = len(steps) - 1
    run_s = n * STEP_S
    total_s = run_s + PAUSE_S
    end_frac = run_s / total_s
    begin = f"-{start_offset:.2f}s" if start_offset else "0s"

    def cx(c):
        return x0 + c * PITCH + CELL / 2

    def cy(r):
        return y0 + r * PITCH + CELL / 2

    path = "M" + " L".join(f"{cx(c):.1f} {cy(r):.1f}" for c, r in steps)
    gap = n * PITCH + 2000
    eat_steps = sorted(eaten_at.values())
    key_times, offsets, arrays, heads = [], [], [], []
    eaten = 0
    for i in range(START_LEN, n + 1):
        while eaten < len(eat_steps) and eat_steps[eaten] <= i:
            eaten += 1
        length = PITCH * min(START_LEN + eaten, MAX_LEN)
        dist = i * PITCH
        key_times.append((i - START_LEN) / (n - START_LEN) * end_frac if n > START_LEN else 0)
        offsets.append(f"{length - dist:.1f}")
        arrays.append(f"{length:.1f} {gap}")
        heads.append(f"{-dist:.1f}")
    key_times.append(1)
    offsets.append(offsets[-1])
    arrays.append(arrays[-1])
    heads.append(heads[-1])
    kt = ";".join(f"{t:.5f}" for t in key_times)
    anim = f'dur="{total_s:.2f}s" begin="{begin}" repeatCount="indefinite" keyTimes="{kt}"'

    cells = []
    for (c, r), count in sorted(grid.items()):
        col = LEVELS[level(count, counts)]
        rect = f'<rect x="{x0 + c * PITCH}" y="{y0 + r * PITCH}" width="{CELL}" height="{CELL}" rx="2" fill="{col}"'
        if (c, r) in eaten_at:
            te = (eaten_at[(c, r)] - START_LEN) / (n - START_LEN) * end_frac
            rect += (
                f'><animate attributeName="fill" values="{col};{LEVELS[0]};{LEVELS[0]}" '
                f'keyTimes="0;{te:.5f};1" calcMode="discrete" dur="{total_s:.2f}s" begin="{begin}" '
                'repeatCount="indefinite"/></rect>'
            )
        else:
            rect += "/>"
        cells.append(rect)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset="1" stop-color="#241056"/></linearGradient>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="board"><rect x="{x0 - 6}" y="{y0 - 6}" width="{WEEKS * PITCH + 8}" height="{7 * PITCH + 8}"/></clipPath>
</defs>
<rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="13" fill="none" stroke="#b967ff" stroke-opacity="0.55" stroke-width="3"/>
<text x="{x0}" y="24" font-family="'Courier New',monospace" font-weight="bold" font-size="13" fill="#05d9e8">SNAKE.EXE · {len(eaten_at)} BLOCKS TO EAT · GROWS +1 PER BLOCK</text>
{''.join(cells)}
<g clip-path="url(#board)" fill="none" stroke-linecap="round" stroke-linejoin="round">
  <path d="{path}" stroke="#05d9e8" stroke-width="9" stroke-dasharray="{arrays[0]}" stroke-dashoffset="{offsets[0]}" filter="url(#glow)">
    <animate attributeName="stroke-dashoffset" values="{';'.join(offsets)}" {anim}/>
    <animate attributeName="stroke-dasharray" values="{';'.join(arrays)}" {anim}/>
  </path>
  <path d="{path}" stroke="#f9f871" stroke-width="11" stroke-dasharray="0.01 {gap}" stroke-dashoffset="{heads[0]}">
    <animate attributeName="stroke-dashoffset" values="{';'.join(heads)}" {anim}/>
  </path>
</g>
<text x="{w - 18}" y="{h - 12}" text-anchor="end" font-family="'Courier New',monospace" font-size="10" fill="#6d5fa0">last 12 months · updated {today:%Y-%m-%d}</text>
</svg>
"""


def main():
    login, out_dir = sys.argv[1], Path(sys.argv[2])
    today = datetime.now(TZ).date()
    days = fetch_days(login, os.environ["GITHUB_TOKEN"], today)
    current, longest = streaks(days, today)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "streak.svg").write_text(render(sum(days.values()), min(days), current, longest, today), encoding="utf-8")
    (out_dir / "snake.svg").write_text(render_snake(days, today), encoding="utf-8")
    print(f"total={sum(days.values())} current={current} longest={longest}")


if __name__ == "__main__":
    main()
