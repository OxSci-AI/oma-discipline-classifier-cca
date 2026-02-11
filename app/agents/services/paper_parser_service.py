#!/usr/bin/env python3
"""
Paper Parser Service - Phase 1 of Paper Review Pipeline

This service is responsible for:
1. Parsing paper content from PDF or structured content
2. Extracting title, abstract, keywords, and sections
3. Identifying methodology terms and domain terms for discipline classification
4. Saving parsed content to local files for subsequent phases

Author: OMA Framework
Version: 1.0.0
Date: 2026-01-23
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List

from oxsci_oma_core import OMAContext
from oxsci_oma_core.tools.registry import tool_registry

from app.core.config import config
from app.agents.models.review_models import PaperContent, PaperSection
from app.agents.prompt_manager import PromptManager

# Import execute_claude_code based on config mode
if config.CLAUDE_CODE_MODE == "sdk":
    from oxsci_oma_core.core.claude_code_agent_sdk import execute_claude_code
else:
    from oxsci_oma_core.core.claude_code_agent import execute_claude_code


class PaperParserService:
    """Service for parsing academic paper content - Phase 1"""

    def __init__(
        self,
        context: OMAContext,
        logger,
        temp_dir: Path,
        temp_files: List[str],
        prompt_manager: PromptManager,
    ):
        """
        Initialize the service.

        Args:
            context: OMA context for accessing MCP tools
            logger: Logger instance
            temp_dir: Directory for temporary files
            temp_files: List to track temporary files for cleanup
            prompt_manager: Prompt manager for loading templates
        """
        self.context = context
        self.logger = logger
        self.temp_dir = temp_dir
        self.temp_files = temp_files
        self.prompt_manager = prompt_manager

    async def parse_paper(
        self,
        file_id: Optional[str] = None,
        structured_content_overview_id: Optional[str] = None,
    ) -> PaperContent:
        """
        Parse paper content from PDF or structured content.

        Priority: structured_content_overview_id > file_id

        Args:
            file_id: PDF file ID (optional)
            structured_content_overview_id: Already parsed structured content ID (optional)

        Returns:
            PaperContent: Parsed paper content with extracted features

        Raises:
            ValueError: If neither file_id nor structured_content_overview_id is provided
        """
        if not file_id and not structured_content_overview_id:
            raise ValueError(
                "At least one of file_id or structured_content_overview_id must be provided"
            )

        self.logger.info("📖 Phase 1: Parsing paper content")

        # Priority 1: Use structured content if available
        if structured_content_overview_id:
            self.logger.info(
                f"  Using structured_content_overview_id: {structured_content_overview_id}"
            )
            sections = await self._parse_from_structured_content(
                structured_content_overview_id
            )
            content_id = structured_content_overview_id
        # Priority 2: Parse from PDF and create MCP storage
        elif file_id:
            self.logger.info(f"  Parsing from PDF file_id: {file_id}")
            # Use new method that creates MCP structured content
            sections, overview_id = await self._parse_from_pdf_with_mcp_storage(file_id)
            content_id = overview_id
            structured_content_overview_id = overview_id  # Set this for later use
        else:
            raise ValueError("No valid input source")

        # Build full paper markdown
        paper_markdown = self._build_paper_markdown(sections)

        # Save raw paper content
        paper_file = self.temp_dir / "paper_content.md"
        paper_file.write_text(paper_markdown, encoding="utf-8")
        self.temp_files.append(str(paper_file))
        self.logger.info(f"  Saved paper content to {paper_file}")

        # Extract structured information using LLM
        extracted = await self._extract_paper_features(paper_markdown)

        # Build PaperContent object
        paper_content = PaperContent(
            title=extracted.get("title", "Untitled Paper"),
            abstract=extracted.get("abstract", ""),
            keywords=extracted.get("keywords", []),
            sections=sections,
            methodology_terms=extracted.get("methodology_terms", []),
            domain_terms=extracted.get("domain_terms", []),
            potential_disciplines=extracted.get("potential_disciplines", []),
            structured_content_overview_id=structured_content_overview_id or "",
            original_file_id=file_id,
        )

        # Save parsed content as JSON
        json_file = self.temp_dir / "paper_content.json"
        json_file.write_text(
            json.dumps(self._paper_content_to_dict(paper_content), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        self.temp_files.append(str(json_file))
        self.logger.info(f"  Saved parsed content to {json_file}")

        return paper_content

    async def _parse_from_structured_content(
        self, structured_content_overview_id: str
    ) -> List[PaperSection]:
        """Parse paper content from structured content sections."""
        [list_sections_tool] = tool_registry.get_tools(
            self.context, ["get_content_section_list"]
        )
        [get_section_detail_tool] = tool_registry.get_tools(
            self.context, ["get_content_section_detail"]
        )

        # List sections
        sections_result = await list_sections_tool.execute()
        if sections_result.status != "success":
            raise ValueError(f"Failed to list content sections: {sections_result.message}")

        sections_data = (
            sections_result.output.get("sections", [])
            if isinstance(sections_result.output, dict)
            else []
        )

        if not sections_data:
            raise ValueError(
                f"No content sections found for ID={structured_content_overview_id}"
            )

        self.logger.info(f"  Found {len(sections_data)} sections")

        # Build PaperSection list
        paper_sections: List[PaperSection] = []
        for idx, section in enumerate(sections_data):
            section_id = section.get("id") or section.get("section_id", "")
            section_name = section.get("name") or section.get("section_name", "")
            section_type = section.get("type") or section.get("section_type", "content")
            section_order = section.get("order") or section.get("section_order", idx + 1)

            # Get section detail
            detail_result = await get_section_detail_tool.execute(section_id=section_id)
            if detail_result.status != "success":
                self.logger.warning(f"  Failed to get section {section_id}: {detail_result.message}")
                continue

            content_data = detail_result.output.get("content", {}) if detail_result.output else {}
            content = self._extract_content_text(content_data)

            paper_sections.append(
                PaperSection(
                    section_id=section_id,
                    section_name=section_name,
                    section_type=self._infer_section_type(section_name, section_type),
                    content=content,
                    section_order=section_order,
                )
            )

        return sorted(paper_sections, key=lambda s: s.section_order)

    async def _parse_from_pdf(self, file_id: str) -> List[PaperSection]:
        """Parse paper content from PDF file."""
        [get_pdf_pages_tool] = tool_registry.get_tools(self.context, ["get_pdf_pages"])

        # Get total pages
        result = await get_pdf_pages_tool.execute(file_id=file_id, start=1, end=1)
        if result.status != "success":
            raise ValueError(f"Failed to get PDF pages: {result.message}")

        output_data = getattr(result, "output", {}) or {}
        total_pages = output_data.get("total_pages", 1) if isinstance(output_data, dict) else 1

        # Fetch all pages
        if total_pages > 1:
            result = await get_pdf_pages_tool.execute(
                file_id=file_id, start=1, end=total_pages
            )
            output_data = getattr(result, "output", {}) or {}

        content_array = output_data.get("content", []) if isinstance(output_data, dict) else []
        self.logger.info(f"  Retrieved {len(content_array)} pages from PDF")

        if not content_array:
            raise ValueError(f"No pages data retrieved for file_id={file_id}")

        # Build sections from pages (simplified - one section per logical part)
        # In reality, you'd want more sophisticated PDF parsing
        all_content = "\n\n".join(content_array)

        paper_sections = [
            PaperSection(
                section_id="full_paper",
                section_name="Full Paper",
                section_type="content",
                content=all_content,
                section_order=1,
            )
        ]

        return paper_sections

    async def _parse_from_pdf_with_mcp_storage(
        self, file_id: str
    ) -> tuple[List[PaperSection], str]:
        """
        Parse PDF and store to MCP, return sections and overview_id.

        This method:
        1. Creates MCP content overview
        2. Parses PDF content into sections
        3. Stores each section to MCP
        4. Returns sections and the created overview_id

        Args:
            file_id: PDF file ID

        Returns:
            Tuple of (sections, overview_id)
        """
        self.logger.info("  📦 Creating MCP structured content storage...")

        # 1. Get MCP tools
        tools = tool_registry.get_tools(self.context, [
            "create_content_overview",
            "create_content_section",
        ])
        create_overview_tool, create_section_tool = tools

        # 2. Create MCP content overview
        overview_result = await create_overview_tool.execute()
        if overview_result.status != "success":
            raise ValueError(f"Failed to create content overview: {overview_result.message}")

        overview_id = overview_result.output.get("id") if overview_result.output else None
        if not overview_id:
            raise ValueError("No overview ID returned from create_content_overview")

        self.logger.info(f"  ✓ Created MCP overview: {overview_id}")

        # 3. Parse PDF content (reuse existing method)
        sections = await self._parse_from_pdf(file_id)

        # 4. Store each section to MCP
        for idx, section in enumerate(sections):
            # Prepare content JSON
            content_json = {
                "text": section.content,
                "section_id": section.section_id,
                "section_type": section.section_type,
            }

            # Create section in MCP
            section_result = await create_section_tool.execute(
                section_type=section.section_type,
                title=section.section_name,
                content_json=content_json,
                section_order=section.section_order or (idx + 1),
            )

            if section_result.status != "success":
                self.logger.warning(
                    f"  Failed to store section '{section.section_name}': {section_result.message}"
                )
                continue

            # Update section_id with MCP section ID
            mcp_section_id = section_result.output.get("id") if section_result.output else None
            if mcp_section_id:
                section.section_id = mcp_section_id

        self.logger.info(f"  ✓ Stored {len(sections)} section(s) to MCP")

        return sections, overview_id

    async def _extract_paper_features(self, paper_markdown: str) -> dict:
        """Extract structured features from paper using LLM."""
        output_file = self.temp_dir / "extracted_features.json"

        # Get extraction prompt
        prompt = self.prompt_manager.get_prompt(
            "paper_content_extraction",
            paper_sections=paper_markdown[:50000],  # Limit length
            output_file=str(output_file),
        )

        # Execute LLM extraction
        await execute_claude_code(
            prompt=prompt,
            context=self.context,
            use_mcp_tools=False,
            model=config.SONNET_MODEL,
        )

        # Read extracted features
        if output_file.exists():
            try:
                extracted = json.loads(output_file.read_text(encoding="utf-8"))
                self.temp_files.append(str(output_file))
                return extracted
            except json.JSONDecodeError:
                self.logger.warning("Failed to parse extracted features JSON")

        # Fallback - basic extraction without LLM
        return self._basic_extraction(paper_markdown)

    def _basic_extraction(self, paper_markdown: str) -> dict:
        """Basic feature extraction without LLM."""
        lines = paper_markdown.split("\n")
        title = ""
        abstract = ""

        for line in lines:
            line = line.strip()
            if line.startswith("# ") and not title:
                title = line[2:].strip()
            elif "abstract" in line.lower() and not abstract:
                # Try to get abstract content
                idx = lines.index(line)
                if idx + 1 < len(lines):
                    abstract_lines = []
                    for j in range(idx + 1, min(idx + 20, len(lines))):
                        if lines[j].startswith("#"):
                            break
                        abstract_lines.append(lines[j])
                    abstract = "\n".join(abstract_lines).strip()
                break

        return {
            "title": title or "Untitled Paper",
            "abstract": abstract,
            "keywords": [],
            "methodology_terms": [],
            "domain_terms": [],
            "potential_disciplines": [],
        }

    def _build_paper_markdown(self, sections: List[PaperSection]) -> str:
        """Build full paper markdown from sections."""
        lines = []
        for section in sorted(sections, key=lambda s: s.section_order):
            lines.append(f"## {section.section_name}")
            lines.append("")
            lines.append(section.content)
            lines.append("")
        return "\n".join(lines)

    def _extract_content_text(self, content_data: dict) -> str:
        """Extract text content from content data dictionary."""
        if isinstance(content_data, str):
            return content_data

        # Priority: markdown > text > value > raw_content
        for key in ["markdown", "text", "value", "raw_content", "paragraph"]:
            if key in content_data:
                return str(content_data[key])

        # Fallback: join all values
        parts = []
        for key, value in content_data.items():
            if not key.startswith("_"):
                parts.append(f"**{key}**: {value}")
        return "\n".join(parts)

    def _infer_section_type(self, section_name: str, default_type: str) -> str:
        """Infer section type from section name."""
        name_lower = section_name.lower()

        type_mappings = {
            "introduction": ["introduction", "intro", "background"],
            "methods": ["method", "methodology", "approach", "materials and methods"],
            "results": ["result", "finding", "experiment"],
            "discussion": ["discussion", "analysis"],
            "conclusion": ["conclusion", "summary", "concluding"],
            "abstract": ["abstract"],
            "references": ["reference", "bibliography", "citation"],
            "appendix": ["appendix", "supplementary"],
        }

        for section_type, keywords in type_mappings.items():
            for keyword in keywords:
                if keyword in name_lower:
                    return section_type

        return default_type or "content"

    def _paper_content_to_dict(self, paper_content: PaperContent) -> dict:
        """Convert PaperContent to dictionary for JSON serialization."""
        return {
            "title": paper_content.title,
            "abstract": paper_content.abstract,
            "keywords": paper_content.keywords,
            "sections": [
                {
                    "section_id": s.section_id,
                    "section_name": s.section_name,
                    "section_type": s.section_type,
                    "section_order": s.section_order,
                    "content_length": len(s.content),
                }
                for s in paper_content.sections
            ],
            "methodology_terms": paper_content.methodology_terms,
            "domain_terms": paper_content.domain_terms,
            "potential_disciplines": paper_content.potential_disciplines,
            "structured_content_overview_id": paper_content.structured_content_overview_id,
            "original_file_id": paper_content.original_file_id,
        }
