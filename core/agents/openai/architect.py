"""Implementation of the OpenAI architect."""

from __future__ import annotations

import json
import logging
from typing import Any

from config.prompts.final_analysis_prompt import format_final_analysis_prompt
from config.prompts.phase_2_prompts import format_phase2_prompt
from config.prompts.phase_4_prompts import format_phase4_prompt
from core.agents.base import BaseArchitect, ModelProvider, ReasoningMode

from .client import execute_request
from .config import resolve_model_defaults
from .request_builder import PreparedRequest, prepare_request
from .response_parser import parse_response

logger = logging.getLogger("project_extractor")


class OpenAIArchitect(BaseArchitect):
    """
    Architect implementation backed by OpenAI's chat and responses APIs.

    The class coordinates prompt preparation, request construction, SDK dispatch,
    and response normalisation via the helper modules housed in this package.
    """

    def __init__(
        self,
        model_name: str = "o3",
        reasoning: ReasoningMode | None = None,
        temperature: float | None = None,
        name: str | None = None,
        role: str | None = None,
        responsibilities: list[str] | None = None,
        prompt_template: str | None = None,
        tools_config: dict | None = None,
        text_verbosity: str | None = None,
    ):
        defaults = resolve_model_defaults(model_name)
        effective_reasoning = reasoning or defaults.default_reasoning

        effective_temperature = temperature
        if (
            effective_temperature is None
            and defaults.default_temperature is not None
            and effective_reasoning == ReasoningMode.TEMPERATURE
        ):
            effective_temperature = defaults.default_temperature

        super().__init__(
            provider=ModelProvider.OPENAI,
            model_name=model_name,
            reasoning=effective_reasoning,
            temperature=effective_temperature,
            name=name,
            role=role,
            responsibilities=responsibilities,
            tools_config=tools_config,
        )

        self.prompt_template = prompt_template or self._get_default_prompt_template()
        self.text_verbosity = text_verbosity
        self._use_responses_api = defaults.use_responses_api

    @staticmethod
    def _get_default_prompt_template() -> str:
        """Default prompt template applied when none is provided."""
        return """You are {agent_name}, responsible for {agent_role}.

Your specific responsibilities are:
{agent_responsibilities}

Analyze this project context and provide a detailed report focused on your domain:

{context}

Format your response as a structured report with clear sections and findings."""

    def format_prompt(self, context: dict) -> str:
        """
        Fill the prompt template with the agent metadata and analysis context.

        Args:
            context: Dictionary containing the context for analysis

        Returns:
            Formatted prompt string
        """
        responsibilities_str = (
            "\n".join(f"- {r}" for r in self.responsibilities) if self.responsibilities else ""
        )
        context_str = json.dumps(context, indent=2) if isinstance(context, dict) else str(context)

        return self.prompt_template.format(
            agent_name=self.name or "OpenAI Architect",
            agent_role=self.role or "analyzing the project",
            agent_responsibilities=responsibilities_str,
            context=context_str,
        )

    async def analyze(self, context: dict, tools: list[Any] | None = None) -> dict:
        """
        Run analysis using the OpenAI model, potentially using tools.

        Args:
            context: Dictionary containing the context for analysis
            tools: Optional list of tools the model can use.
                   Follows OpenAI's tool definition format.

        Returns:
            Dictionary containing the analysis results, potential tool calls, or error information
        """
        try:
            content = context.get("formatted_prompt") or self.format_prompt(context)

            final_tools = self._resolve_tools(tools)
            prepared = self._prepare_request(content, final_tools)

            from core.utils.model_config_helper import get_model_config_name

            model_config_name = get_model_config_name(self)
            agent_name = self.name or "OpenAI Architect"
            detail_suffix = " with tools enabled" if final_tools else ""
            api_label = "Responses API" if prepared.api == "responses" else "Chat Completions API"

            logger.info(
                f"[bold blue]{agent_name}:[/bold blue] Sending request to {self.model_name} "
                f"via {api_label} (Config: {model_config_name}){detail_suffix}"
            )

            response = execute_request(prepared)

            logger.info(
                f"[bold green]{agent_name}:[/bold green] Received response from {self.model_name}"
            )

            parsed = parse_response(response, prepared.api)
            results = {
                "agent": agent_name,
                "findings": parsed.findings,
                "tool_calls": parsed.tool_calls,
            }

            if parsed.tool_calls:
                logger.info(f"[bold blue]{agent_name}:[/bold blue] Model requested tool call(s).")

            return results
        except Exception as exc:  # pragma: no cover - defensive logging
            agent_name = self.name or "OpenAI Architect"
            logger.error(f"[bold red]Error in {agent_name}:[/bold red] {str(exc)}")
            return {
                "agent": agent_name,
                "error": str(exc),
            }

    async def create_analysis_plan(self, phase1_results: dict, prompt: str | None = None) -> dict:
        """Create an analysis plan based on Phase 1 results."""
        return await self._run_simple_request(
            prompt or format_phase2_prompt(phase1_results),
            result_key="plan",
            empty_value="No plan generated",
        )

    async def synthesize_findings(self, phase3_results: dict, prompt: str | None = None) -> dict:
        """Synthesize findings from Phase 3."""
        return await self._run_simple_request(
            prompt or format_phase4_prompt(phase3_results),
            result_key="analysis",
            empty_value="No synthesis generated",
        )

    async def final_analysis(self, consolidated_report: dict, prompt: str | None = None) -> dict:
        """Perform final analysis on the consolidated report."""
        return await self._run_simple_request(
            prompt or format_final_analysis_prompt(consolidated_report),
            result_key="analysis",
            empty_value="No final analysis generated",
        )

    async def consolidate_results(self, all_results: dict, prompt: str | None = None) -> dict:
        """Consolidate results from all previous phases."""
        default_prompt = (
            "Consolidate these results into a comprehensive report:\n\n"
            f"{json.dumps(all_results, indent=2)}"
        )

        response = await self._run_simple_request(
            prompt or default_prompt,
            result_key="report",
            empty_value="No report generated",
            include_phase=True,
        )
        response.setdefault("phase", "Consolidation")
        return response

    def _prepare_request(
        self,
        content: str,
        tools: list[Any] | None = None,
    ) -> PreparedRequest:
        return prepare_request(
            model_name=self.model_name,
            content=content,
            reasoning=self.reasoning,
            temperature=self.temperature,
            tools=tools,
            text_verbosity=self.text_verbosity,
            use_responses_api=self._use_responses_api,
        )

    def _resolve_tools(self, tools: list[Any] | None) -> list[Any] | None:
        if not tools and not (self.tools_config and self.tools_config.get("enabled", False)):
            return None

        tool_list = tools or self.tools_config.get("tools", [])
        if not tool_list:
            return None

        from core.agent_tools.tool_manager import ToolManager

        return ToolManager.get_provider_tools(tool_list, ModelProvider.OPENAI)

    async def _run_simple_request(
        self,
        content: str,
        *,
        result_key: str,
        empty_value: str,
        include_phase: bool = False,
    ) -> dict:
        try:
            prepared = self._prepare_request(content)
            response = execute_request(prepared)
            parsed = parse_response(response, prepared.api)

            result: dict[str, Any] = {result_key: parsed.findings or empty_value}
            if parsed.tool_calls:
                result["tool_calls"] = parsed.tool_calls

            if include_phase:
                result["phase"] = "Consolidation"

            return result
        except Exception as exc:  # pragma: no cover - defensive logging
            logger.error(f"Error during OpenAI request: {str(exc)}")
            response: dict[str, Any] = {"error": str(exc)}
            if include_phase:
                response["phase"] = "Consolidation"
            return response


__all__ = ["OpenAIArchitect"]
