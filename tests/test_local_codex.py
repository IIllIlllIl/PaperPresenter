import json
import subprocess
from pathlib import Path

from src.lite.local_codex import LocalCodexRunner


def test_local_codex_runner_builds_exec_command(monkeypatch, tmp_path: Path):
    captured = {}

    def fake_run(cmd, cwd, capture_output, text, timeout, check):
        captured["cmd"] = cmd
        output_path = Path(cmd[cmd.index("--output-last-message") + 1])
        output_path.write_text('{"ok": true}', encoding="utf-8")
        return subprocess.CompletedProcess(cmd, 0, stdout="", stderr="")

    monkeypatch.setattr(subprocess, "run", fake_run)

    runner = LocalCodexRunner(codex_bin="codex", model="gpt-test", cwd=tmp_path)
    result = runner.run_json(
        prompt="Return JSON",
        images=[tmp_path / "page.png"],
        output_schema={"type": "object"},
    )

    assert result == {"ok": True}
    assert captured["cmd"][:2] == ["codex", "exec"]
    assert "--image" in captured["cmd"]
    assert "--output-schema" in captured["cmd"]
    assert "--model" in captured["cmd"]

