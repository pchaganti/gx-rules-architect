import os
import tempfile
import unittest
from importlib import reload
from pathlib import Path
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner


class CLITestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        os.environ["AGENTRULES_CONFIG_DIR"] = self.temp_dir.name
        from agentrules import config_service, model_config
        from config import agents as agents_module

        reload(config_service)
        reload(agents_module)
        reload(model_config)

        self.config_service = config_service
        self.model_config = model_config
        self.agents_module = agents_module

    def tearDown(self) -> None:
        if hasattr(self, "model_config"):
            self.model_config.apply_user_overrides({})
        self.temp_dir.cleanup()
        os.environ.pop("AGENTRULES_CONFIG_DIR", None)

    def test_analyze_command_offline(self) -> None:
        from agentrules import cli

        runner = CliRunner()

        with patch("agentrules.cli.commands.analyze.bootstrap_runtime") as mock_bootstrap, patch(
            "agentrules.cli.commands.analyze.run_pipeline"
        ) as mock_run_pipeline:
            context = MagicMock()
            mock_bootstrap.return_value = context
            result = runner.invoke(
                cli.app,
                ["analyze", str(Path.cwd()), "--offline"],
                env={"AGENTRULES_CONFIG_DIR": self.temp_dir.name},
            )

        self.assertEqual(result.exit_code, 0, msg=result.output)
        mock_bootstrap.assert_called_once()
        mock_run_pipeline.assert_called_once()
        call_args = mock_run_pipeline.call_args[0]
        self.assertEqual(call_args[0], Path.cwd())
        self.assertTrue(call_args[1])
        self.assertIs(call_args[2], context)
