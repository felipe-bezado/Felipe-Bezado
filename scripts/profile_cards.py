"""Render the arcade profile cards from the GitHub contribution calendar.

streak.svg: a streak survives up to GRACE_DAYS empty weekdays in a row (weekends are free); the next one breaks it.
snake.svg: a snake eats the contribution cells of the last year, grows one block per cell with no cap, never crosses itself, and shows STAGE CLEAR or GAME OVER when the run ends.
Usage: GITHUB_TOKEN=... python scripts/profile_cards.py <login> <out_dir>
"""
import base64
import json
import os
import sys
import urllib.request
from collections import deque
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


def is_weekend(d):
    return d.weekday() >= 5


def empty_workdays(after, before, days):
    """Weekdays strictly between two dates with no contributions; weekends never cost a heart."""
    d, n = after + timedelta(days=1), 0
    while d < before:
        if not is_weekend(d) and not days.get(d, 0):
            n += 1
        d += timedelta(days=1)
    return n


def streaks(days, today):
    """Split active days into streaks, where more than GRACE_DAYS empty weekdays in a row break one."""
    active = sorted(d for d, c in days.items() if c > 0 and d <= today)
    runs = []
    for d in active:
        if runs and empty_workdays(runs[-1][1], d, days) <= GRACE_DAYS:
            runs[-1][1] = d
            runs[-1][2] += 1
        else:
            runs.append([d, d, 1])
    current = None
    if runs:
        # Today is still playable, so an empty today does not cost a heart yet.
        lost = empty_workdays(runs[-1][1], today, days)
        if lost <= GRACE_DAYS:
            current = (*runs[-1], lost)
    longest = max(runs, key=lambda r: (combo_len(r, days), r[2], r[1]), default=None)
    return current, longest


def combo_len(run, days):
    """Days in the run, counting every weekday plus the weekend days that had contributions."""
    d, n = run[0], 0
    while d <= run[1]:
        if not is_weekend(d) or days.get(d, 0):
            n += 1
        d += timedelta(days=1)
    return n


def font_b64():
    return base64.b64encode(FONT_FILE.read_bytes()).decode()


def heart(x, y, px, fill):
    shape = [".XX.XX.", "XXXXXXX", "XXXXXXX", ".XXXXX.", "..XXX..", "...X..."]
    return "".join(
        f'<rect x="{x + c * px}" y="{y + r * px}" width="{px}" height="{px}" fill="{fill}"/>'
        for r, row in enumerate(shape)
        for c, ch in enumerate(row)
        if ch == "X"
    )


def render(total, first_day, current, longest, today, days):
    font = font_b64()
    pink, cyan, yellow, purple, dim = "#ff2a6d", "#05d9e8", "#f9f871", "#b967ff", "#3a2a5e"
    w, h = 900, 250
    cur_days = combo_len(current, days) if current else 0
    lives = GRACE_DAYS - current[3] if current else 0
    hearts = "".join(
        heart(450 - (GRACE_DAYS * 34 - 8) // 2 + i * 34, 176, 4, pink if i < lives else dim) for i in range(GRACE_DAYS)
    )
    cur_sub = f"since {current[0]:%b %d, %Y}" if current else "insert coin to start a combo"
    best_days = combo_len(longest, days) if longest else 0
    best_sub = f"{longest[0]:%b %d, %Y} - {longest[1]:%b %d, %Y}" if longest else "-"
    status = "COMBO ALIVE" if current and lives else ("LAST LIFE!" if current else "GAME OVER")
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
<defs>
  <style>@font-face{{font-family:'PS2P';src:url(data:font/woff2;base64,{font}) format('woff2');}}
  text{{font-family:'PS2P',monospace}}</style>
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
<text x="150" y="188" text-anchor="middle" font-size="9" fill="#c9c3ea">since {first_day.strftime("%b %Y")}</text>

<text x="450" y="62" text-anchor="middle" font-size="11" fill="{yellow}">CURRENT COMBO</text>
<text x="450" y="122" text-anchor="middle" font-size="44" fill="{yellow}" filter="url(#glow)">{cur_days}<animate attributeName="opacity" values="1;0.75;1" dur="1.6s" repeatCount="indefinite"/></text>
<text x="450" y="152" text-anchor="middle" font-size="9" fill="{yellow}">{"DAY" if cur_days == 1 else "DAYS"} · {status}</text>
{hearts}
<text x="450" y="226" text-anchor="middle" font-size="8" fill="#c9c3ea">{cur_sub} · {GRACE_DAYS} grace workdays · weekends free</text>

<text x="750" y="62" text-anchor="middle" font-size="11" fill="{pink}">HIGH SCORE</text>
<text x="750" y="122" text-anchor="middle" font-size="34" fill="#fff" filter="url(#glow)">{best_days}</text>
<text x="750" y="152" text-anchor="middle" font-size="9" fill="{pink}">DAY COMBO</text>
<text x="750" y="188" text-anchor="middle" font-size="9" fill="#c9c3ea">{best_sub}</text>
<text x="{w - 18}" y="{h - 10}" text-anchor="end" font-size="7" fill="#6d5fa0">updated {today:%Y-%m-%d}</text>
</svg>
"""


PITCH, CELL, WEEKS = 15, 11, 53
START_LEN, MAX_LEN, STEP_S, PAUSE_S, MAX_STEPS, MAX_RUN_S = 3, 10_000, 0.09, 2.5, 6000, 40
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


def neighbors(cell, board):
    c, r = cell
    for n in ((c + 1, r), (c - 1, r), (c, r + 1), (c, r - 1)):
        if n in board:
            yield n


def bfs(start, goals, blocked, board):
    """Shortest path (excluding start) from start to the nearest goal, avoiding blocked cells."""
    prev, queue = {start: None}, deque([start])
    while queue:
        cur = queue.popleft()
        if cur in goals and cur != start:
            path = []
            while cur != start:
                path.append(cur)
                cur = prev[cur]
            return path[::-1]
        for n in neighbors(cur, board):
            if n not in prev and n not in blocked:
                prev[n] = cur
                queue.append(n)
    return None


def reachable(start, blocked, board):
    seen, queue = {start}, deque([start])
    while queue:
        for n in neighbors(queue.popleft(), board):
            if n not in seen and n not in blocked:
                seen.add(n)
                queue.append(n)
    return len(seen)


def advance(body, cell, grow):
    body.append(cell)
    if not grow:
        body.popleft()


def route(grid):
    """Play real snake over the grid: never enter its own body, and only chase food it can escape from.

    Returns the head cell per step and the step at which each contribution cell is eaten.
    """
    board, targets = set(grid), {cell for cell, c in grid.items() if c}
    steps = [(-START_LEN + k, 0) for k in range(START_LEN + 1)]
    body = deque(steps[1:])
    eaten_at = {}
    if steps[-1] in targets:
        targets.discard(steps[-1])
        eaten_at[steps[-1]] = len(steps) - 1

    def eat_or_move(cell):
        grow = cell in targets and len(body) < MAX_LEN
        advance(body, cell, grow)
        steps.append(cell)
        if cell in targets:
            targets.discard(cell)
            eaten_at[cell] = len(steps) - 1

    def safe(path):
        sim = deque(body)
        for cell in path:
            advance(sim, cell, cell in targets and len(sim) < MAX_LEN)
        tail = sim[0]
        if tail not in board:  # still sliding onto the board
            return True
        return bfs(sim[-1], {tail}, set(sim) - {tail}, board) is not None

    while targets and len(steps) < MAX_STEPS:
        path = bfs(body[-1], targets, set(body), board)
        if path and safe(path):
            for cell in path:
                eat_or_move(cell)
            continue
        # No safe food: stall towards the move that keeps the most free space around the head.
        tail = body[0]
        options = [n for n in neighbors(body[-1], board) if n not in body or n == tail]
        if not options:
            break
        blocked = set(body) - {tail}
        eat_or_move(max(options, key=lambda n: (reachable(n, blocked, board), n == tail)))
    return steps, eaten_at


def collisions(steps, eaten_at):
    """Replay a route and return the steps where the head entered its own body (must be empty)."""
    body, hits = deque(steps[1:START_LEN + 1]), []
    eat_steps = set(eaten_at.values())
    for i in range(START_LEN + 1, len(steps)):
        tail = body[0]
        if steps[i] in body and steps[i] != tail:
            hits.append(i)
        advance(body, steps[i], i in eat_steps and len(body) < MAX_LEN)
    return hits


def render_snake(days, today, start_offset=0.0):
    w, h = 900, 175
    x0, y0 = (w - WEEKS * PITCH) // 2, 38
    grid = calendar_grid(days, today)
    counts = [c for c in grid.values() if c]
    steps, eaten_at = route(grid)
    n = len(steps) - 1
    run_s = n * min(STEP_S, MAX_RUN_S / max(n, 1))
    total_s = run_s + PAUSE_S
    end_frac = run_s / total_s
    begin = f"-{start_offset:.2f}s" if start_offset else "0s"

    def cx(c):
        return x0 + c * PITCH + CELL / 2

    def cy(r):
        return y0 + r * PITCH + CELL / 2

    food = sum(1 for c in grid.values() if c)
    cleared = len(eaten_at) == food
    end_msg = f"STAGE CLEAR · {food}/{food}" if cleared else f"GAME OVER · SCORE {len(eaten_at)}/{food}"
    end_col = "#39ff14" if cleared else "#ff2a6d"
    path = "M" + " L".join(f"{cx(c):.1f} {cy(r):.1f}" for c, r in steps)
    gap = n * PITCH + 2000
    eat_steps = sorted(eaten_at.values())
    key_times, offsets, arrays, heads = [], [], [], []
    eaten = 0
    for i in range(START_LEN, n + 1):
        while eaten < len(eat_steps) and eat_steps[eaten] <= i:
            eaten += 1
        # A little shorter than the body so the tail never visually touches the head.
        length = PITCH * (min(START_LEN + eaten, MAX_LEN) - 0.6)
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
  <style>@font-face{{font-family:'PS2P';src:url(data:font/woff2;base64,{font_b64()}) format('woff2');}} text{{font-family:'PS2P',monospace}}</style>
  <linearGradient id="bg" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#0d0221"/><stop offset="1" stop-color="#241056"/></linearGradient>
  <filter id="glow" x="-10%" y="-30%" width="120%" height="160%"><feGaussianBlur stdDeviation="2.5" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <clipPath id="board"><rect x="{x0 - 6}" y="{y0 - 6}" width="{WEEKS * PITCH + 8}" height="{7 * PITCH + 8}"/></clipPath>
</defs>
<rect width="{w}" height="{h}" rx="14" fill="url(#bg)"/>
<rect x="1.5" y="1.5" width="{w - 3}" height="{h - 3}" rx="13" fill="none" stroke="#b967ff" stroke-opacity="0.55" stroke-width="3"/>
<text x="{x0}" y="25" font-size="10" fill="#05d9e8">SNAKE.EXE · {food} BLOCKS TO EAT · GROWS +1 PER BLOCK</text>
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
<g opacity="0">
  <animate attributeName="opacity" values="0;0;1;1" keyTimes="0;{end_frac:.5f};{min(end_frac + 0.01, 1):.5f};1" dur="{total_s:.2f}s" begin="{begin}" repeatCount="indefinite"/>
  <rect x="{w / 2 - 190}" y="{h / 2 - 26}" width="380" height="44" rx="6" fill="#0d0221" fill-opacity="0.85" stroke="{end_col}" stroke-width="2"/>
  <text x="{w / 2}" y="{h / 2 + 3}" text-anchor="middle" font-size="14" fill="{end_col}">{end_msg}</text>
</g>
<text x="{w - 18}" y="{h - 10}" text-anchor="end" font-size="7" fill="#6d5fa0">last 12 months · updated {today:%Y-%m-%d}</text>
</svg>
"""


def main():
    login, out_dir = sys.argv[1], Path(sys.argv[2])
    today = datetime.now(TZ).date()
    days = fetch_days(login, os.environ["GITHUB_TOKEN"], today)
    current, longest = streaks(days, today)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "streak.svg").write_text(render(sum(days.values()), min(days), current, longest, today, days), encoding="utf-8")
    (out_dir / "snake.svg").write_text(render_snake(days, today), encoding="utf-8")
    print(f"total={sum(days.values())} current={current} longest={longest}")


if __name__ == "__main__":
    main()
