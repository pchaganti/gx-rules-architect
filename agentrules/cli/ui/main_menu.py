"""Interactive main menu for the agentrules CLI."""

from __future__ import annotations

from pathlib import Path
from textwrap import dedent

import questionary

from ..context import CliContext
from ..services.pipeline_runner import run_pipeline
from . import config_wizard


def run_main_menu(context: CliContext) -> None:
    console = context.console
    banner = dedent(
        """
        [bold cyan]
         █████╗  ██████╗ ███████╗███╗   ██╗████████╗██████╗ ██╗   ██╗██╗     ███████╗███████╗
        ██╔══██╗██╔════╝ ██╔════╝████╗  ██║╚══██╔══╝██╔══██╗██║   ██║██║     ██╔════╝██╔════╝
        ███████║██║  ███╗█████╗  ██╔██╗ ██║   ██║   ██████╔╝██║   ██║██║     ███████╗█████╗
        ██╔══██║██║   ██║██╔══╝  ██║╚██╗██║   ██║   ██╔══██╗██║   ██║██║     ╚════██║██╔══╝
        ██║  ██║╚██████╔╝███████╗██║ ╚████║   ██║   ██║  ██║╚██████╔╝███████╗███████║███████╗
        ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚══════╝╚══════╝╚══════╝
        [/bold cyan]
        """
    )
    console.print(banner)

    menu_choices = {
        "Analyze current directory": "analyze_current",
        "Analyze another path": "analyze_other",
        "Configure provider API keys": "configure_keys",
        "Configure models per phase": "configure_models",
        "Show configured providers": "show_keys",
        "Exit": "exit",
    }

    while True:
        choice = questionary.select(
            "What would you like to do?",
            choices=list(menu_choices.keys()),
            qmark="🤖",
        ).ask()

        if choice is None or menu_choices[choice] == "exit":
            console.print("Goodbye!")
            return

        action = menu_choices[choice]
        if action == "analyze_current":
            run_pipeline(Path.cwd(), offline=False, context=context)
        elif action == "analyze_other":
            path_answer = questionary.path("Target project directory:", only_directories=True).ask()
            if not path_answer:
                continue
            target = Path(path_answer).expanduser().resolve()
            if not target.exists() or not target.is_dir():
                console.print(f"[red]Invalid directory: {target}[/]")
                continue
            run_pipeline(target, offline=False, context=context)
        elif action == "configure_keys":
            config_wizard.configure_provider_keys(context)
        elif action == "configure_models":
            config_wizard.configure_models(context)
        elif action == "show_keys":
            config_wizard.show_provider_summary(context)
