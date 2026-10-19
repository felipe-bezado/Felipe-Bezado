<p align="center">
  <img src="assets/banner.svg" alt="Felipe Bezado, Data Engineer, arcade title screen" width="100%"/>
</p>

<p align="center">
  <a href="https://github.com/felipe-bezado">
    <img src="https://readme-typing-svg.demolab.com?font=Press+Start+2P&size=14&duration=2800&pause=900&color=05D9E8&center=true&vCenter=true&width=760&height=40&lines=%3E+loading+data+pipelines...;%3E+summoning+Claude+into+production...;%3E+turning+spreadsheets+into+BigQuery+tables...;%3E+defeating+bugs+before+the+6PM+deploy...;%3E+READY+PLAYER+ONE" alt="typing intro"/>
  </a>
</p>

<p align="center">
  <a href="https://www.linkedin.com/in/felipe-bezado/"><img src="https://img.shields.io/badge/LinkedIn-PLAYER_2%3F_JOIN_IN-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&labelColor=0d0221"/></a>
  <img src="https://hits.sh/github.com/felipe-bezado.svg?style=for-the-badge&label=VISITORS&color=ff2a6d&labelColor=0d0221" alt="visitors"/>
</p>

---

<p align="center">
  <img src="assets/character.svg" alt="Character sheet: Python 95, SQL/BigQuery 93, GCP/Cloud Run 90, AI/LLM Ops 92, Dashboards 85, Bash/Linux 80" width="100%"/>
</p>

## 🎮 Choose your level

<details open>
<summary><b>🗺️ WORLD 1: The Data Realm</b> <i>(click to collapse)</i></summary>
<br/>

I'm a **Data Engineer** at a Brazilian retail-intelligence company. My realm: a fleet of **~100 Cloud Run jobs and services** (59 of them shipped or rebuilt by me) that move data from retailers, ERPs, e-commerce platforms and inboxes into **BigQuery**, then out again as dashboards, alerts and AI answers.

| Zone | What lives there |
|---|---|
| 📦 **Sellout Plains** | retailer spreadsheets of every shape → AI-assisted parsing → audited BigQuery loads |
| 💸 **Pricing Peaks** | competitor price mapping: official API first, plain scraping second, LLM last |
| 🚚 **Logistics Docks** | carrier tracking, freight-quote inbox readers, delivery alerts |
| 📊 **Dashboard City** | a hub of internal FastAPI dashboards behind one SSO, each with its own Claude chat |
| 🧮 **Cost Control Tower** | GCP billing export, daily cost digest, scale-to-zero rotation for idle apps |

</details>

<details>
<summary><b>📜 QUEST LOG</b> <i>(click to open)</i></summary>
<br/>

**⚔️ Current quest**
- [ ] Retire the last no-code automations and rebuild them as tested Cloud Run jobs
- [ ] Self-healing sellout chain: every load proves itself before it says "done"

**✅ Main quests completed**
- [x] **Data Center**: one hub, one login, many dashboards, relay-JWT auth with per-card access control
- [x] **AI-in-the-loop email reader**: Gmail → 2 AI judges + 1 arbiter → a daily freight close nobody types by hand
- [x] **Dashboard chat**: Claude with tools over BigQuery, streaming answers and HTML reports
- [x] **Shared dev kit**: one Python library for secrets, BigQuery, auth and telemetry across every job
- [x] **Homemade PR quality gate**: lint + changed-line coverage + a review bot, 90% coverage house rule

**🧩 Side quests**
- [x] Internal **Claude Code plugin marketplace** for the team (deploy, debug, QA, design skills)
- [x] An **Obsidian second brain** wired to Claude's memory, so context survives between sessions
- [x] Slack alerts for failed jobs, a morning health check, and a "check jobs" report on demand

</details>

<details>
<summary><b>🐉 BOSSES DEFEATED</b> <i>(click to open)</i></summary>
<br/>

| Boss | Attack | How it fell | Loot |
|---|---|---|---|
| 🐉 **The Expiration Dragon** | a 60-day dataset default silently ate tables overnight | audit + explicit expiration policy | *never trust a default* |
| 🐍 **The Duplicate Hydra** | cut one load, two copies grow back | idempotent writes keyed per period | *rerun-safe pipelines* |
| ⏰ **The UTC Goblin** | cron fired 3 hours late | schedules pinned to local time, timestamps stored in UTC | *timezone armor* |
| 🕷️ **The Schema Drift Spider** | an API quietly renamed its fields | never append a raw API frame, never delete before write | *contract tests* |
| 🧟 **The Un-awaited DML Zombie** | a query that "finished" before it ran | always `.result()` before the next write | *race immunity* |
| 👻 **The Cold Start Specter** | idle apps burning money all night | telemetry-ranked warm rotation, scale-to-zero after hours | **-55% idle cost** |

</details>

---

## 🎒 Inventory

<p align="center">
  <img src="https://skillicons.dev/icons?i=py,gcp,docker,githubactions,fastapi,postgres,bash,linux&perline=8" alt="main tools"/>
  <br/>
  <img src="https://skillicons.dev/icons?i=git,html,js,css,vscode,obsidian,md,claude&perline=8" alt="more tools"/>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/BigQuery-669DF6?style=for-the-badge&logo=googlebigquery&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Cloud_Run-4285F4?style=for-the-badge&logo=googlecloud&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Claude_API-D97757?style=for-the-badge&logo=anthropic&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Claude_Code-D97757?style=for-the-badge&logo=claude&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Poetry-60A5FA?style=for-the-badge&logo=poetry&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/LightGBM-2E7D32?style=for-the-badge&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Playwright-2EAD33?style=for-the-badge&logo=playwright&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/SAP_HANA-0FAAFF?style=for-the-badge&logo=sap&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/VTEX-F71963?style=for-the-badge&logo=vtex&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Shopify-7AB55C?style=for-the-badge&logo=shopify&logoColor=white&labelColor=0d0221"/>
  <img src="https://img.shields.io/badge/Slack_API-4A154B?style=for-the-badge&logo=slack&logoColor=white&labelColor=0d0221"/>
</p>

<details>
<summary><b>🔍 Inspect items</b></summary>
<br/>

| Item | Rarity | Effect |
|---|---|---|
| 🐍 Python + Poetry | ⭐⭐⭐⭐⭐ Legendary | every job, every service, locked dependencies |
| 🔷 BigQuery | ⭐⭐⭐⭐⭐ Legendary | the save file of the whole realm |
| ☁️ Cloud Run | ⭐⭐⭐⭐ Epic | jobs on a schedule, services that sleep when nobody looks |
| 🤖 Claude API | ⭐⭐⭐⭐ Epic | parsing, judging, summarizing, chatting with data |
| ⚙️ GitHub Actions | ⭐⭐⭐ Rare | CI, quality gate, deploy on merge |
| 🎭 Playwright | ⭐⭐⭐ Rare | headless QA for every dashboard before it ships |

</details>

---

<p align="center">
  <img src="assets/achievements.svg" alt="Achievements: Thousand PR Club, Cloud Tamer, AI Whisperer, 90% Club, Penny Pincher, Gatekeeper, Toolsmith, Second Brain" width="100%"/>
</p>

## 🐍 Bonus stage: the snake eats my contributions

<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/felipe-bezado/Felipe-Bezado/output/github-snake-dark.svg"/>
    <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/felipe-bezado/Felipe-Bezado/output/github-snake.svg"/>
    <img alt="snake eating the contribution graph" src="https://raw.githubusercontent.com/felipe-bezado/Felipe-Bezado/output/github-snake-dark.svg"/>
  </picture>
</p>

<p align="center">
  <img src="https://streak-stats.demolab.com?user=felipe-bezado&theme=radical&hide_border=true&background=0d0221" alt="streak stats"/>
</p>

<details>
<summary><b>🔒 ↑ ↑ ↓ ↓ ← → ← → B A</b></summary>
<br/>

```text
CHEAT CODE ACCEPTED
+30 lives granted
> SELECT * FROM bugs WHERE fixed = FALSE;
0 rows returned.
(for now)
```

</details>

<p align="center">
  <img src="https://img.shields.io/badge/SAVE_POINT-São_Paulo,_BR_·_UTC--3-ff2a6d?style=flat-square&labelColor=0d0221"/>
  <br/><sub>GAME OVER? Never. INSERT COIN TO CONTINUE 🪙</sub>
</p>
