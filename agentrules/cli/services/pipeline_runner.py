"""Utilities for executing the project analysis pipeline."""

from __future__ import annotations

import asyncio
import os
import time
from pathlib import Path

from agentrules.analyzer import ProjectAnalyzer

from ..context import CliContext


def _activate_offline_mode(context: CliContext) -> None:
    if os.getenv("OFFLINE", "0") != "1":
        return

    try:
        from core.utils.offline import patch_factory_offline

        patch_factory_offline()
        context.console.print("[yellow]OFFLINE=1 detected: using DummyArchitects (no network calls).[/]")
    except Exception as error:  # pragma: no cover - defensive logging
        context.console.print(f"[red]Failed to enable OFFLINE mode: {error}[/]")


def run_pipeline(path: Path, offline: bool, context: CliContext) -> None:
    """Execute the analysis pipeline for the given path."""

    if offline:
        os.environ["OFFLINE"] = "1"

    _activate_offline_mode(context)

    analyzer = ProjectAnalyzer(path, context.console)
    start_time = time.time()

    try:
        asyncio.run(analyzer.analyze())
    except RuntimeError:
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(analyzer.analyze())
        finally:
            loop.close()

    analyzer.persist_outputs(start_time)
    context.console.print(f"\n[green]Analysis finished for:[/] {path}")
