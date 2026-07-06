# CLI `users list` — flaga `--wide` (jak ops-monitor)

**Status:** `done`  
**Created:** 2026-07-06  
**Source:** [ops-monitor/backend/cli/commands/users.py](../../../ops-monitor/backend/cli/commands/users.py) (`users list`)  
**Backport:** [backport-progress.md](../../../backport-progress.md)

## Problem

`users delete` jest już zaktualizowany (soft/hard), ale `users list` nadal bez `--wide` i bez interaktywnych promptów jak w ops-monitor.

## Oczekiwane zachowanie

- `--wide/--no-wide/-w`
- interaktywne `typer.confirm` dla `detailed` i `wide` (gdy brak `--json`)
- `--detailed/--no-detailed` jako `bool | None`

## Zakres

- [x] `backend/cli/commands/users.py` — backport `list` z ops-monitor (zachować istniejące rozszerzenia create/delete)

## Weryfikacja

```bash
./exec.sh users list --wide --detailed
```
