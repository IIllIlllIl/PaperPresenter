# Cross-Platform Policy

PaperPresenter Lite should be portable across macOS, Linux, and Windows.

The Lite implementation should stay pure Python unless there is a strong reason
to do otherwise.

## Current Repository Composition

The full repository still contains legacy shell scripts. These belong to the old
project workflow, not the Lite harness.

Tracked repository summary at the time of this policy:

- Python: 79 tracked `.py` files
- Shell: 8 tracked `.sh` files
- Markdown: 97 tracked `.md` files
- Lite package: 10 tracked `.py` files and no shell scripts

Shell scripts currently live under:

- `src/scripts/*.sh`
- `src/tools/*.sh`
- `src/tools/manual_tests/*.sh`

These should be treated as legacy utilities. New Lite functionality should not
depend on them.

## Lite Rules

- New Lite code should be Python.
- Use `pathlib.Path` for filesystem paths.
- Avoid shell-specific commands, glob behavior, pipes, and redirects in runtime
  code.
- Use Python libraries instead of shelling out for file copying, cleanup,
  JSON/YAML handling, and path discovery.
- If a subprocess is necessary, call a stable cross-platform executable with an
  argument list, not a shell command string.
- Keep local Codex access behind `LocalCodexRunner`.
- Tests should not require Bash, zsh, PowerShell, or platform-specific tools.

## Accepted External Executables

The Lite harness may call:

- `codex` through `LocalCodexRunner`

This is the intentional model boundary. Other executable dependencies should be
introduced only after documenting the cross-platform implications.

## Migration Guidance

Do not remove legacy shell scripts as part of Lite development unless a cleanup
task explicitly targets legacy archival. The immediate goal is to prevent new
Lite code from depending on them.

