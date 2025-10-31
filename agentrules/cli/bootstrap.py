"""Shared bootstrap helpers for CLI commands."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv
from rich.console import Console

from agentrules import model_config
from agentrules.config_service import apply_config_to_environment, resolve_log_level
from agentrules.logging_setup import configure_logging

from .context import CliContext


def _load_env_files() -> None:
    env_path = Path(".env")
    if env_path.exists():
        load_dotenv(env_path)


def bootstrap_runtime() -> CliContext:
    """Configure logging, load configuration, and return a CLI context."""

    log_level = resolve_log_level()
    configure_logging(level=log_level)
    apply_config_to_environment()
    _load_env_files()
    model_config.apply_user_overrides()

    console = Console()
    return CliContext(console=console)
