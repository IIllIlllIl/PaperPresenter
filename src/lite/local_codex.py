"""Local Codex CLI adapter for PaperPresenter Lite."""

from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional


class LocalCodexError(RuntimeError):
    """Raised when a local Codex invocation fails."""


class LocalCodexRunner:
    """
    Thin wrapper around `codex exec`.

    This keeps model access outside the harness core. Provider classes pass a
    prompt, optional images, and an optional JSON schema; Codex returns the final
    message as a string.
    """

    def __init__(
        self,
        codex_bin: str = "codex",
        model: Optional[str] = None,
        sandbox: str = "read-only",
        cwd: str | Path = ".",
        timeout_seconds: int = 600,
    ):
        self.codex_bin = codex_bin
        self.model = model
        self.sandbox = sandbox
        self.cwd = Path(cwd)
        self.timeout_seconds = timeout_seconds

    def run(
        self,
        prompt: str,
        images: Optional[List[str | Path]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> str:
        images = images or []

        with tempfile.TemporaryDirectory(prefix="paperpresenter-codex-") as tmpdir:
            tmpdir_path = Path(tmpdir)
            output_path = tmpdir_path / "last_message.txt"
            schema_path = None
            if output_schema is not None:
                schema_path = tmpdir_path / "schema.json"
                schema_path.write_text(json.dumps(output_schema, indent=2), encoding="utf-8")

            cmd = [
                self.codex_bin,
                "exec",
                "--cd",
                str(self.cwd),
                "--sandbox",
                self.sandbox,
                "--output-last-message",
                str(output_path),
            ]
            if self.model:
                cmd.extend(["--model", self.model])
            if schema_path is not None:
                cmd.extend(["--output-schema", str(schema_path)])
            for image in images:
                cmd.extend(["--image", str(image)])
            cmd.append("-")

            completed = subprocess.run(
                cmd,
                cwd=str(self.cwd),
                input=prompt,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds,
                check=False,
            )

            if completed.returncode != 0:
                raise LocalCodexError(
                    "codex exec failed with exit code "
                    f"{completed.returncode}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
                )
            if not output_path.exists():
                raise LocalCodexError("codex exec did not write an output-last-message file")
            return output_path.read_text(encoding="utf-8").strip()

    def run_json(
        self,
        prompt: str,
        images: Optional[List[str | Path]] = None,
        output_schema: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        raw = self.run(prompt=prompt, images=images, output_schema=output_schema)
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise LocalCodexError(f"Codex returned non-JSON output: {raw[:500]}") from exc
