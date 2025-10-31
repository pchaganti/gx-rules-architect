.
├── __init__.py                # Top-level package for core functionality.
├── agent_tools/               # Contains tools that AI agents can use, like web search.
│   ├── tool_manager.py        # Manages and converts tool schemas for different LLM providers.
│   └── web_search/            # Sub-package for web search tools.
│       ├── __init__.py        # Exposes the Tavily search tool and schema.
│       └── tavily.py          # Implements the Tavily web search tool.
├── agents/                    # Contains agent implementations for various LLM providers.
│   ├── __init__.py            # Exposes a shortcut to the agent factory function.
│   ├── anthropic.py           # Implements the architect class for Anthropic's Claude models.
│   ├── base.py                # Defines the abstract base class and core enums for all agents.
│   ├── deepseek.py            # Implements the architect class for DeepSeek models.
│   ├── factory/               # Contains the factory for creating agent instances.
│   │   ├── __init__.py        # Exposes the factory function.
│   │   └── factory.py         # Implements the architect factory for creating agents from config.
│   ├── gemini.py              # Implements the architect class for Google's Gemini models.
│   └── openai/                # Sub-package for OpenAI-specific agent logic.
│       ├── __init__.py        # Exposes the main OpenAI architect and a legacy agent.
│       ├── architect.py       # Implements the primary architect class for OpenAI models.
│       ├── client.py          # Manages the shared OpenAI SDK client.
│       ├── compat.py          # Provides a backward-compatible shim for a legacy agent class.
│       ├── config.py          # Defines default configurations for various OpenAI models.
│       ├── request_builder.py # Constructs request payloads for OpenAI APIs.
│       └── response_parser.py # Parses and normalizes responses from OpenAI APIs.
├── analysis/                  # Contains the logic for each distinct phase of the analysis pipeline.
│   ├── __init__.py            # Exposes all phase analysis classes for easy importing.
│   ├── final_analysis.py      # Implements the final analysis phase to generate cursor rules.
│   ├── phase_1.py             # Implements Phase 1: Initial project discovery and research.
│   ├── phase_2.py             # Implements Phase 2: Creates a methodical plan for deep analysis.
│   ├── phase_3.py             # Implements Phase 3: Executes deep analysis using specialized agents.
│   ├── phase_4.py             # Implements Phase 4: Synthesizes findings from the deep analysis.
│   └── phase_5.py             # Implements Phase 5: Consolidates all findings into a final report.
├── types/                     # Contains custom type definitions used across the project.
│   ├── __init__.py            # Exposes key type definitions for the package.
│   ├── agent_config.py        # Defines a TypedDict for agent configurations.
│   ├── models.py              # Defines the ModelConfig type and various predefined model setups.
│   └── tool_config.py         # Defines types for agent tool configurations.
└── utils/                     # Contains utility functions and helper modules.
    ├── file_creation/         # Utilities related to creating output files.
    │   ├── cursorignore.py    # Manages the creation and modification of .cursorignore files.
    │   └── phases_output.py   # Saves the output of each analysis phase to markdown files.
    ├── file_system/           # Utilities for interacting with the file system.
    │   ├── __init__.py        # Exposes file system utility functions.
    │   ├── file_retriever.py  # Retrieves and formats file contents from a project.
    │   └── tree_generator.py  # Generates an ASCII tree representation of a directory structure.
    ├── formatters/            # Utilities for formatting files.
    │   ├── __init__.py        # Exposes the cursorrules cleaner function.
    │   └── clean_cursorrules.py # Cleans up the final .cursorrules file for proper formatting.
    ├── model_config_helper.py # Helper to get human-readable names for model configurations.
    ├── offline.py             # Provides dummy architect classes for offline testing.
    └── parsers/               # Utilities for parsing model outputs.
        ├── __init__.py        # Exposes key parser functions.
        └── agent_parser.py    # Parses agent definitions from Phase 2's output text.