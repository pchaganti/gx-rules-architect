.
├── __init__.py                # Top-level package initializer and warning filter.
├── analyzer.py                # Core logic for orchestrating the multi-phase analysis pipeline.
├── cli/                       # Contains all Command-Line Interface logic.
│   ├── __init__.py            # Exports the main Typer application object.
│   ├── app.py                 # Defines the main Typer application and registers subcommands.
│   ├── bootstrap.py           # Handles common runtime setup for CLI commands (logging, config).
│   ├── commands/              # Implements the specific CLI subcommands.
│   │   ├── __init__.py        # Package initializer for CLI commands.
│   │   ├── analyze.py         # Defines the `analyze` subcommand to run the analysis pipeline.
│   │   ├── configure.py       # Defines the `configure` subcommand for settings management.
│   │   ├── keys.py            # Defines the `keys` subcommand to display provider API key status.
│   ├── context.py             # Defines a shared context object for CLI state and helpers.
│   ├── services/              # Business logic abstractions for the CLI.
│   │   ├── __init__.py        # Package initializer for the services module.
│   │   ├── configuration.py   # Service layer for managing provider and model configurations.
│   │   ├── pipeline_runner.py # Service for executing the analysis pipeline from the CLI.
│   └── ui/                    # Modules for user interaction and terminal rendering.
│       ├── __init__.py        # Package initializer for the UI module.
│       ├── analysis_view.py   # Renders real-time analysis progress using the Rich library.
│       ├── settings/            # Interactive settings flows (providers, models, exclusions).
│       │   ├── __init__.py      # Public entry points for settings menus.
│       │   ├── menu.py          # Top-level settings navigation.
│       │   ├── providers.py     # Provider API key summary and editor.
│       │   ├── logging.py       # Logging verbosity configuration.
│       │   ├── outputs.py       # Output preferences configuration.
│       │   ├── exclusions/      # Exclusion summary rendering and editing helpers.
│       │   │   ├── __init__.py
│       │   │   ├── editor.py
│       │   │   └── summary.py
│       │   └── models/          # Model preset selection flows.
│       │       ├── __init__.py
│       │       ├── researcher.py
│       │       └── utils.py
│       └── main_menu.py       # Implements the interactive main menu for the CLI.
├── config_service.py          # Manages loading and saving of user configuration from a TOML file.
├── logging_setup.py           # Configures application-wide logging using Rich.
└── model_config.py            # Manages AI model presets and applies user overrides.
