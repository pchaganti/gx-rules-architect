.
├── __init__.py                # Package initializer for the agentrules CLI.
├── analyzer.py                # Core orchestration logic for the multi-phase project analysis pipeline.
├── cli/                       # Modular Typer CLI broken into composable components.
│   ├── __init__.py            # Exposes the Typer app factory for external entry points.
│   ├── app.py                 # Builds the Typer app and wires shared callback behaviour.
│   ├── bootstrap.py           # Prepares logging, environment, and returns a CLI context object.
│   ├── context.py             # Defines lightweight CLI context helpers and masking utilities.
│   ├── commands/              # Thin Typer command handlers.
│   │   ├── __init__.py        # Marks the commands package.
│   │   ├── analyze.py         # Implements the `analyze` subcommand.
│   │   ├── configure.py       # Implements the `configure` subcommand.
│   │   └── keys.py            # Implements the `keys` subcommand.
│   ├── services/              # Stateless services backing CLI flows.
│   │   ├── __init__.py        # Marks the services package.
│   │   ├── configuration.py   # Wraps configuration persistence and preset helpers.
│   │   └── pipeline_runner.py # Coordinates execution of the analysis pipeline.
│   └── ui/                    # Interactive UI flows built on Questionary.
│       ├── __init__.py        # Marks the UI package.
│       ├── config_wizard.py   # Provider and model configuration wizards.
│       └── main_menu.py       # Interactive main menu for common tasks.
├── config_service.py          # Manages user configuration for API keys and model presets via a TOML file.
├── logging_setup.py           # Sets up Rich-based logging and filters for consistent CLI output.
├── model_config.py            # Manages and applies model presets based on user configuration.
