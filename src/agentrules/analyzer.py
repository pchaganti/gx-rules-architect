"""Legacy compatibility wrapper for the refactored analysis pipeline."""

from __future__ import annotations

import asyncio
import json
import warnings
from pathlib import Path

from rich.console import Console

from agentrules.config.agents import MODEL_CONFIG
from agentrules.core.configuration import get_config_manager
from agentrules.core.pipeline import (
    AnalysisPipeline,
    EffectiveExclusions,
    PipelineOutputOptions,
    PipelineOutputWriter,
    PipelineResult,
    PipelineSettings,
    build_project_snapshot,
    create_default_pipeline,
)
from agentrules.core.utils.model_config_helper import get_model_config_name


class ProjectAnalyzer:
    """Deprecated interface maintained for backwards compatibility."""

    def __init__(self, directory: Path, console: Console | None = None):
        warnings.warn(
            "ProjectAnalyzer is deprecated; use the core.pipeline modules instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        self.directory = directory
        self.console = console or Console()
        self._config_manager = get_config_manager()
        self._settings: PipelineSettings | None = None
        self._result: PipelineResult | None = None

    def _build_settings(self) -> PipelineSettings:
        config_manager = self._config_manager
        exclusion_overrides = config_manager.get_exclusion_overrides()
        effective_dirs, effective_files, effective_exts = config_manager.get_effective_exclusions()
        return PipelineSettings(
            target_directory=self.directory,
            tree_max_depth=config_manager.get_tree_max_depth(),
            respect_gitignore=config_manager.should_respect_gitignore(),
            effective_exclusions=EffectiveExclusions(
                directories=frozenset(effective_dirs),
                files=frozenset(effective_files),
                extensions=frozenset(effective_exts),
            ),
            exclusion_overrides=exclusion_overrides,
        )

    def _build_pipeline(self) -> AnalysisPipeline:
        researcher_enabled = self._config_manager.is_researcher_enabled()
        return create_default_pipeline(researcher_enabled=researcher_enabled)

    async def analyze(self) -> str:
        settings = self._build_settings()
        pipeline = self._build_pipeline()
        snapshot = build_project_snapshot(settings)

        result = await pipeline.run(settings, snapshot)
        self._settings = settings
        self._result = result

        return self._format_report(result)

    def persist_outputs(self, metrics_start_time: float | None = None) -> None:
        if not self._result or not self._settings:
            raise RuntimeError("analyze() must be called before persist_outputs().")

        output_writer = PipelineOutputWriter()
        options = PipelineOutputOptions(
            rules_filename=self._config_manager.get_rules_filename(),
            generate_phase_outputs=self._config_manager.should_generate_phase_outputs(),
            generate_cursorignore=self._config_manager.should_generate_cursorignore(),
        )
        summary = output_writer.persist(self._result, self._settings, options)
        for message in summary.messages:
            self.console.print(message)

    def _format_report(self, result: PipelineResult) -> str:
        lines: list[str] = [
            f"Project Analysis Report for: {self.directory}",
            "=" * 50 + "\n",
            "## Project Structure\n",
        ]
        lines.extend(result.snapshot.tree_with_delimiters)
        lines.append("\n")

        phase1_model = get_model_config_name(MODEL_CONFIG["phase1"])
        phase2_model = get_model_config_name(MODEL_CONFIG["phase2"])
        phase3_model = get_model_config_name(MODEL_CONFIG["phase3"])
        phase4_model = get_model_config_name(MODEL_CONFIG["phase4"])
        phase5_model = get_model_config_name(MODEL_CONFIG["phase5"])
        final_model = get_model_config_name(MODEL_CONFIG["final"])

        elapsed = result.metrics.elapsed_seconds

        lines.extend(
            [
                f"Phase 1: Initial Discovery (Config: {phase1_model})",
                "-" * 30,
                json.dumps(result.phase1, indent=2),
                "\n",
                f"Phase 2: Methodical Planning (Config: {phase2_model})",
                "-" * 30,
                str(result.phase2.get("plan", "Error in planning phase")),
                "\n",
                f"Phase 3: Deep Analysis (Config: {phase3_model})",
                "-" * 30,
                json.dumps(result.phase3, indent=2),
                "\n",
                f"Phase 4: Synthesis (Config: {phase4_model})",
                "-" * 30,
                str(result.phase4.get("analysis", "Error in synthesis phase")),
                "\n",
                f"Phase 5: Consolidation (Config: {phase5_model})",
                "-" * 30,
                str(result.consolidated_report.get("report", "Error in consolidation phase")),
                "\n",
                f"Final Analysis (Config: {final_model})",
                "-" * 30,
                str(result.final_analysis.get("analysis", "Error in final analysis phase")),
                "\n",
                "Analysis Metrics",
                "-" * 30,
                f"Time taken: {elapsed:.2f} seconds",
            ]
        )
        return "\n".join(lines)


def run_analysis(directory: Path, console: Console | None = None) -> str:
    analyzer = ProjectAnalyzer(directory, console)
    loop = asyncio.new_event_loop()
    try:
        asyncio.set_event_loop(loop)
        return loop.run_until_complete(analyzer.analyze())
    finally:
        loop.close()
