#!/usr/bin/env python3
"""
Discipline Classifier Service - Phase 2 of Paper Review Pipeline

This service is responsible for:
1. Classifying papers into academic disciplines (1-23)
2. Using ID-based selection mechanism for reliability
3. Returning max 3 disciplines with relevance scores
4. Optionally storing classification results to MCP

Author: OMA Framework
Version: 1.0.0
Date: 2026-01-23
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional
import uuid
from datetime import datetime

from oxsci_oma_core import OMAContext
from oxsci_oma_core.tools.registry import tool_registry

from app.core.config import config
from app.agents.models.review_models import (
    PaperContent,
    DisciplineResult,
    DisciplineClassification,
)
from app.agents.models.discipline_models import (
    DISCIPLINES,
    get_discipline_by_id,
    get_discipline_list_for_prompt,
    get_keyword_section_for_prompt,
)
from app.agents.prompt_manager import PromptManager

# Import execute_claude_code based on config mode
if config.CLAUDE_CODE_MODE == "sdk":
    from oxsci_oma_core.core.claude_code_agent_sdk import execute_claude_code
else:
    from oxsci_oma_core.core.claude_code_agent import execute_claude_code


class DisciplineClassifierService:
    """Service for classifying papers into academic disciplines - Phase 2"""

    # Analysis type for storing classification results
    ANALYSIS_TYPE = "discipline_classification"

    def __init__(
        self,
        context: OMAContext,
        logger,
        temp_dir: Path,
        prompt_manager: PromptManager,
        store_to_mcp: bool = True,
    ):
        """
        Initialize the service.

        Args:
            context: OMA context for accessing MCP tools
            logger: Logger instance
            temp_dir: Directory for temporary files
            prompt_manager: Prompt manager for loading templates
            store_to_mcp: Whether to store classification results to MCP
        """
        self.context = context
        self.logger = logger
        self.temp_dir = temp_dir
        self.prompt_manager = prompt_manager
        self.store_to_mcp = store_to_mcp

    async def classify_paper(
        self,
        paper_content: PaperContent,
    ) -> DisciplineClassification:
        """
        Classify paper into academic disciplines.

        Uses ID-based selection mechanism (1-23) for reliable classification.
        Returns max 3 disciplines with relevance scores >= 0.4.

        Args:
            paper_content: Parsed paper content from Phase 1

        Returns:
            DisciplineClassification: Classification result with disciplines and confidence
        """
        self.logger.info("🎯 Phase 2: Classifying paper disciplines")

        # Prepare output file
        output_file = self.temp_dir / "discipline_classification.json"

        # Build prompt with discipline list and keyword mappings
        prompt = self.prompt_manager.get_prompt(
            "discipline_classifier",
            discipline_list=get_discipline_list_for_prompt(),
            keyword_section=get_keyword_section_for_prompt(),
            paper_title=paper_content.title,
            paper_abstract=paper_content.abstract,
            paper_keywords=", ".join(paper_content.keywords) if paper_content.keywords else "Not specified",
            methodology_terms=", ".join(paper_content.methodology_terms) if paper_content.methodology_terms else "Not extracted",
            domain_terms=", ".join(paper_content.domain_terms) if paper_content.domain_terms else "Not extracted",
            potential_disciplines=", ".join(paper_content.potential_disciplines) if paper_content.potential_disciplines else "Not identified",
            output_file=str(output_file),
        )

        # Execute LLM classification
        await execute_claude_code(
            prompt=prompt,
            context=self.context,
            use_mcp_tools=False,
            model=config.SONNET_MODEL,
        )

        # Parse classification result
        classification = await self._parse_classification_result(output_file)

        # Validate and correct discipline names
        classification = self._validate_disciplines(classification)

        self.logger.info(
            f"  Classified into {len(classification.disciplines)} disciplines: "
            f"{', '.join(d.name for d in classification.disciplines)}"
        )
        self.logger.info(f"  Confidence: {classification.confidence_score:.2f}")

        # Optionally store to MCP (requires structured_content_overview_id)
        if self.store_to_mcp and paper_content.structured_content_overview_id:
            classification_id = await self._store_classification_to_mcp(
                paper_content, classification
            )
            classification.discipline_classification_id = classification_id
        else:
            if self.store_to_mcp and not paper_content.structured_content_overview_id:
                self.logger.info("  Skipping MCP storage (no structured_content_overview_id)")
            classification.discipline_classification_id = str(uuid.uuid4())

        # Save classification result
        result_file = self.temp_dir / "discipline_result.json"
        result_file.write_text(
            json.dumps(self._classification_to_dict(classification), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

        return classification

    async def _parse_classification_result(
        self, output_file: Path
    ) -> DisciplineClassification:
        """Parse classification result from LLM output file."""
        if not output_file.exists():
            self.logger.warning("Classification output file not found, using fallback")
            return self._fallback_classification()

        try:
            data = json.loads(output_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse classification JSON, using fallback")
            return self._fallback_classification()

        # Parse disciplines
        disciplines: List[DisciplineResult] = []
        for disc_data in data.get("disciplines", []):
            disc_id = disc_data.get("id", 0)
            disc_name = disc_data.get("name", "")
            score = disc_data.get("score", 0.0)
            evidence = disc_data.get("evidence", "")

            # Get discipline by ID for validation
            disc_def = get_discipline_by_id(disc_id)
            if disc_def:
                disciplines.append(
                    DisciplineResult(
                        discipline_id=disc_id,
                        name=disc_def.name,  # Use canonical name
                        relevance_score=min(1.0, max(0.0, score)),
                        evidence=evidence,
                    )
                )

        # Ensure we have at least one discipline
        if not disciplines:
            disciplines = [
                DisciplineResult(
                    discipline_id=1,
                    name="Computer Science",
                    relevance_score=0.5,
                    evidence="Default classification",
                )
            ]

        # Sort by relevance score and take top 3
        disciplines = sorted(disciplines, key=lambda d: d.relevance_score, reverse=True)[:3]

        return DisciplineClassification(
            disciplines=disciplines,
            confidence_score=min(1.0, max(0.0, data.get("confidence", 0.7))),
            classification_reasoning=data.get("reasoning", ""),
            discipline_classification_id="",  # Will be set after MCP storage
        )

    def _validate_disciplines(
        self, classification: DisciplineClassification
    ) -> DisciplineClassification:
        """Validate and correct discipline information."""
        validated_disciplines = []

        for disc in classification.disciplines:
            # Validate discipline ID
            disc_def = get_discipline_by_id(disc.discipline_id)
            if disc_def:
                # Use canonical name from definition
                validated_disciplines.append(
                    DisciplineResult(
                        discipline_id=disc.discipline_id,
                        name=disc_def.name,
                        relevance_score=disc.relevance_score,
                        evidence=disc.evidence,
                    )
                )
            else:
                self.logger.warning(f"  Invalid discipline ID: {disc.discipline_id}")

        # Ensure at least one valid discipline
        if not validated_disciplines:
            validated_disciplines = [
                DisciplineResult(
                    discipline_id=1,
                    name="Computer Science",
                    relevance_score=0.5,
                    evidence="Fallback classification",
                )
            ]

        return DisciplineClassification(
            disciplines=validated_disciplines,
            confidence_score=classification.confidence_score,
            classification_reasoning=classification.classification_reasoning,
            discipline_classification_id=classification.discipline_classification_id,
        )

    def _fallback_classification(self) -> DisciplineClassification:
        """Return fallback classification when LLM fails."""
        return DisciplineClassification(
            disciplines=[
                DisciplineResult(
                    discipline_id=1,
                    name="Computer Science",
                    relevance_score=0.5,
                    evidence="Fallback due to classification failure",
                )
            ],
            confidence_score=0.3,
            classification_reasoning="Fallback classification due to processing error",
            discipline_classification_id="",
        )

    async def _store_classification_to_mcp(
        self,
        paper_content: PaperContent,
        classification: DisciplineClassification,
    ) -> str:
        """Store classification result to MCP as an analysis."""
        self.logger.info("  Storing classification to MCP")

        # Get MCP tools
        [create_overview_tool] = tool_registry.get_tools(
            self.context, ["create_analysis_overview"]
        )
        [create_section_tool] = tool_registry.get_tools(
            self.context, ["create_analysis_section"]
        )
        [complete_overview_tool] = tool_registry.get_tools(
            self.context, ["complete_analysis_overview"]
        )

        # Create analysis overview
        create_result = await create_overview_tool.execute(
            analysis_type=self.ANALYSIS_TYPE,
            title=f"Discipline Classification: {paper_content.title[:100]}",
            description="AI-generated discipline classification for academic paper",
            structured_content_overview_id=paper_content.structured_content_overview_id,
        )

        if create_result.status != "success":
            raise ValueError(f"Failed to create analysis overview: {create_result.message}")

        # Store classification section
        classification_content = {
            "disciplines": [
                {
                    "id": d.discipline_id,
                    "name": d.name,
                    "relevance_score": d.relevance_score,
                    "evidence": d.evidence,
                }
                for d in classification.disciplines
            ],
            "confidence_score": classification.confidence_score,
            "reasoning": classification.classification_reasoning,
            "paper_title": paper_content.title,
            "timestamp": datetime.now().isoformat(),
        }

        await create_section_tool.execute(
            analysis_type=self.ANALYSIS_TYPE,
            section_type="classification_result",
            section_name="Discipline Classification",
            section_order=1,
            content=classification_content,
        )

        # Complete the analysis
        complete_result = await complete_overview_tool.execute()

        if complete_result.status != "success":
            self.logger.warning(f"Failed to complete analysis: {complete_result.message}")

        # Get the analysis ID
        analysis_id = ""
        if create_result.output and isinstance(create_result.output, dict):
            analysis_id = create_result.output.get("analysis_id", "")

        self.logger.info(f"  Stored classification with ID: {analysis_id}")
        return analysis_id

    def _classification_to_dict(self, classification: DisciplineClassification) -> dict:
        """Convert classification to dictionary for JSON serialization."""
        return {
            "disciplines": [
                {
                    "discipline_id": d.discipline_id,
                    "name": d.name,
                    "relevance_score": d.relevance_score,
                    "evidence": d.evidence,
                }
                for d in classification.disciplines
            ],
            "confidence_score": classification.confidence_score,
            "classification_reasoning": classification.classification_reasoning,
            "discipline_classification_id": classification.discipline_classification_id,
        }
