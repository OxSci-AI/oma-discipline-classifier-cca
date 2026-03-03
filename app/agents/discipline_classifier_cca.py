#!/usr/bin/env python3
"""
Discipline Classifier CCA Agent

A standalone agent that classifies academic papers into disciplines (1-23).
Implements Phase 1 (Paper Parsing) and Phase 2 (Discipline Classification) only.

Based on the Universal Paper Review Pipeline but extracts only the classification flow.
"""

from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import json

from pydantic import Field

from oxsci_oma_core import ITaskExecutor, OMAContext, AgentConfig
from oxsci_shared_core.logging import logger

from app.core.config import config
from app.agents.prompt_manager import PromptManager
from app.agents.services.paper_parser_service import PaperParserService
from app.agents.services.discipline_classifier_service import DisciplineClassifierService
from app.agents.models.review_models import PaperContent, DisciplineClassification


class DisciplineClassifierCCA(ITaskExecutor):
    """
    Discipline Classifier Agent

    Classifies academic papers into 1-3 disciplines from 23 predefined categories.

    Pipeline:
    - Phase 1: Parse paper content (PDF or structured content)
    - Phase 2: Classify into disciplines with ID-based selection (1-23)

    Input:
    - file_id OR structured_content_overview_id (required, one of)

    Output:
    - discipline_classification_id: MCP analysis ID
    - disciplines: List of disciplines with relevance scores
    - confidence_score: Overall classification confidence
    - classification_reasoning: Explanation
    """

    # Agent configuration
    agent_role = "discipline_classifier"
    timeout = 600  # 10 minutes
    retry_count = 1
    estimated_tools_count = 20

    # Resource configuration for ECS
    ecs_cpu = 1024
    ecs_memory = 2048

    # Input/output schema
    class Input(AgentConfig.InputBase):
        file_id: Optional[str] = Field(None, description="PDF file ID of the research paper")
        manuscript_id: Optional[str] = Field(None, description="Manuscript ID for tracking context")
        structured_content_overview_id: Optional[str] = Field(
            None, description="Already parsed structured content ID (skips PDF parsing)"
        )

    class Output(AgentConfig.OutputBase):
        discipline_classification_id: str = Field(..., description="MCP analysis ID for classification")
        discipline_codes: list = Field(..., description="List of discipline codes (numeric IDs 1-23)")
        disciplines: list = Field(..., description="List of classified disciplines with details")
        confidence_score: float = Field(..., description="Overall classification confidence (0.0-1.0)")
        classification_reasoning: str = Field(..., description="Explanation of classification")
        paper_title: str = Field(..., description="Paper title")
        paper_sections: int = Field(..., description="Number of paper sections")

    def __init__(self, context: OMAContext):
        """Initialize the agent"""
        super().__init__(context)
        self.context = context
        self.workspace_dir = Path(context.workspace_dir)

        # Debug phases
        self.debug_phases = self._parse_debug_phases(config.CLASSIFIER_DEBUG_PHASES)

        # Track temp files for cleanup
        self.temp_files: List[str] = []

        # Initialize services
        self.prompt_manager = PromptManager()
        self.paper_parser_service = PaperParserService(
            context=context,
            logger=logger,
            temp_dir=self.workspace_dir,
            temp_files=self.temp_files,
            prompt_manager=self.prompt_manager,
        )
        self.discipline_classifier_service = DisciplineClassifierService(
            context=context,
            logger=logger,
            temp_dir=self.workspace_dir,
            prompt_manager=self.prompt_manager,
            store_to_mcp=True,
        )

    def _parse_debug_phases(self, debug_phases_str: Optional[str]) -> set:
        """Parse debug phases from config string"""
        if not debug_phases_str:
            return set()
        return {p.strip().lower() for p in debug_phases_str.split(",")}

    async def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the discipline classification pipeline"""
        try:
            logger.info("=" * 80)
            logger.info("DISCIPLINE CLASSIFIER CCA AGENT")
            logger.info("=" * 80)

            # Extract input parameters
            file_id = kwargs.get("file_id")
            manuscript_id = kwargs.get("manuscript_id")
            structured_content_overview_id = kwargs.get("structured_content_overview_id")

            if not file_id and not structured_content_overview_id:
                raise ValueError("Either file_id or structured_content_overview_id must be provided")

            if manuscript_id:
                logger.info(f"  Manuscript ID: {manuscript_id}")
            if file_id:
                logger.info(f"  File ID: {file_id}")

            # Phase 1: Paper Parsing
            if self.debug_phases and "parser" not in self.debug_phases:
                logger.info("Skipping Phase 1 (parser) - loading from workspace")
                paper_content = self._load_parser_output()
            else:
                logger.info("Phase 1: Paper Parsing")
                paper_content = await self.paper_parser_service.parse_paper(
                    file_id=file_id,
                    structured_content_overview_id=structured_content_overview_id,
                )
                logger.info(f"  Parsed paper: {paper_content.title}")
                logger.info(f"  Sections: {len(paper_content.sections)}")

                # Save parser output for debugging
                self._save_parser_output(paper_content)

            # Phase 2: Discipline Classification
            if self.debug_phases and "classifier" not in self.debug_phases:
                logger.info("Skipping Phase 2 (classifier) - loading from workspace")
                classification = self._load_classifier_output()
            else:
                logger.info("Phase 2: Discipline Classification")
                classification = await self.discipline_classifier_service.classify_paper(
                    paper_content=paper_content
                )
                logger.info(f"  Classified into {len(classification.disciplines)} disciplines")
                logger.info(f"  Confidence: {classification.confidence_score:.2f}")
                for disc in classification.disciplines:
                    logger.info(f"    - [{disc.discipline_id}] {disc.name} (score: {disc.relevance_score:.2f})")

                # Save classifier output for debugging
                self._save_classifier_output(classification)

            # Build output
            result = {
                "discipline_classification_id": classification.discipline_classification_id,
                "discipline_codes": [d.discipline_id for d in classification.disciplines],
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
                "paper_title": paper_content.title,
                "paper_sections": len(paper_content.sections),
                "manuscript_id": manuscript_id,
                "agent_role": self.agent_role,
                "pipeline_version": "1.0.0",
            }

            logger.info("=" * 80)
            logger.info("CLASSIFICATION COMPLETE")
            logger.info(f"  Discipline codes: {result['discipline_codes']}")
            logger.info("=" * 80)

            return {"status": "success", "result": result}

        except Exception as e:
            logger.error(f"Agent execution failed: {e}", exc_info=True)
            return {
                "status": "error",
                "result": {
                    "error": str(e),
                    "agent_role": self.agent_role,
                },
            }
        finally:
            self._cleanup_temp_files()

    # ========================================================================
    # Debug helpers (save/load intermediate results)
    # ========================================================================

    def _save_parser_output(self, paper_content: PaperContent) -> None:
        """Save parser output for debugging"""
        output_file = self.workspace_dir / "paper_content.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(paper_content), f, indent=2, ensure_ascii=False)
        logger.debug(f"  Saved parser output: {output_file}")

    def _load_parser_output(self) -> PaperContent:
        """Load parser output from workspace"""
        output_file = self.workspace_dir / "paper_content.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Parser output not found: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Reconstruct PaperSection objects from dicts
        from app.agents.models.review_models import PaperSection
        if "sections" in data and data["sections"]:
            data["sections"] = [PaperSection(**s) for s in data["sections"]]
        return PaperContent(**data)

    def _save_classifier_output(self, classification: DisciplineClassification) -> None:
        """Save classifier output for debugging"""
        output_file = self.workspace_dir / "classification.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(classification), f, indent=2, ensure_ascii=False)
        logger.debug(f"  Saved classifier output: {output_file}")

    def _load_classifier_output(self) -> DisciplineClassification:
        """Load classifier output from workspace"""
        output_file = self.workspace_dir / "classification.json"
        if not output_file.exists():
            raise FileNotFoundError(f"Classifier output not found: {output_file}")
        with open(output_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Reconstruct DisciplineResult objects from dicts
        from app.agents.models.review_models import DisciplineResult
        if "disciplines" in data and data["disciplines"]:
            data["disciplines"] = [DisciplineResult(**d) for d in data["disciplines"]]
        return DisciplineClassification(**data)

    def _cleanup_temp_files(self) -> None:
        """Clean up temporary files"""
        if not config.CLEAN_TMP_FILE:
            return
        for file_path in self.temp_files:
            try:
                Path(file_path).unlink(missing_ok=True)
            except Exception:
                pass
        self.temp_files.clear()
