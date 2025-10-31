"""Implementation of the `configure` subcommand."""

from __future__ import annotations

import questionary
import typer

from agentrules.config_service import PROVIDER_ENV_MAP

from ..bootstrap import bootstrap_runtime
from ..services import configuration as config_service
from ..ui import config_wizard


def register(app: typer.Typer) -> None:
    """Register the `configure` subcommand with the provided Typer app."""

    @app.command()
    def configure(  # type: ignore[func-returns-value]
        provider: str | None = typer.Option(
            None,
            "--provider",
            "-p",
            help="Limit configuration to a single provider.",
        ),
        models_only: bool = typer.Option(
            False,
            "--models",
            help="Configure model presets instead of API keys.",
        ),
        logging_only: bool = typer.Option(
            False,
            "--logging",
            help="Configure logging verbosity.",
        ),
    ) -> None:
        context = bootstrap_runtime()

        option_count = sum(
            1
            for flag in (
                provider is not None,
                models_only,
                logging_only,
            )
            if flag
        )
        if option_count > 1:
            raise typer.BadParameter("Choose only one of --provider, --models, or --logging.")

        if models_only:
            config_wizard.configure_models(context)
            return

        if logging_only:
            config_wizard.configure_logging(context)
            return

        if provider:
            if provider not in PROVIDER_ENV_MAP:
                raise typer.BadParameter(
                    f"Unknown provider '{provider}'. Options: {', '.join(PROVIDER_ENV_MAP.keys())}"
                )

            answer = questionary.password(f"{provider.title()} API key:", qmark="🔐").ask()
            if answer is None:
                context.console.print("[yellow]No changes made.[/]")
                return

            trimmed = answer.strip()
            config_service.save_provider_key(provider, trimmed or None)
            context.console.print(f"[green]{provider.title()} key updated.[/]")
            return

        config_wizard.configure_provider_keys(context)
