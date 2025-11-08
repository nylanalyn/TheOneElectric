# Repository Guidelines

## Project Structure & Module Organization
`pymotion_bot.py` houses the IRC client, plugin loader, and runtime entrypoint, so edits there impact connection handling and the shared Plugin base class. Self-contained behaviors belong in `plugins/*.py`; give guard-rail plugins (e.g., `shutup`) the highest `priority`, and keep modules idempotent so `{botnick} reload` hot-loads safely. Ops helpers such as `pymotion.service`, `requirements.txt`, `flake.nix`, and `CLAUDE.md` stay at the root for deployment and architecture notes.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate` — create an isolated Python 3.13+ environment before installing extras.
- `pip install -r requirements.txt` — installs aiofiles and any transient plugin dependencies.
- `python pymotion_bot.py` — launches the bot, auto-creating `pymotion.json`; pass `python pymotion_bot.py myconfig.json` when testing alternate setups.

## Coding Style & Naming Conventions
Use 4-space indentation, type hints, and dataclasses for shared state (match `UserState`/`ChannelState`). Keep modules lint-friendly: no bare prints, prefer `logging` with contextual strings. Plugins are snake_case filenames with PascalCase classes exposing `handle_message`, returning True when they consume a line.

## Testing Guidelines
No formal suite exists yet, so add focused `tests/` modules with `pytest` and `pytest-asyncio` when touching complex parsing or plugin logic. Mock IRC events (e.g., PRIVMSG chains) and assert plugin short-circuiting. Name tests `test_<plugin>_<behavior>` for clarity. Run `pytest -q` before publishing; for smoke checks, run the bot against a local InspIRCd container and verify joins, reloads, and admin commands.

## Commit & Pull Request Guidelines
Recent history favors short, descriptive titles ("Fix bot responsiveness"), so keep commits atomic, imperative, and scoped to one feature or bug. Reference issues or context in the body ("Refs #42") and note config updates or new admin commands explicitly. PRs should outline behavior changes, include reproduction steps or sample IRC transcripts, call out manual test logs, and confirm `{botnick} reload` succeeds.

## Configuration & Security Notes
`pymotion.json` stores secrets—never check in real server credentials. Copy it to a bespoke file (e.g., `pymotion.libera.json`) for experiments and pass that path to the launcher. When deploying with `pymotion.service`, keep ownership restricted to the bot user, rotate SASL tokens regularly, and remove debug logging before opening a PR to avoid leaking channel data.
