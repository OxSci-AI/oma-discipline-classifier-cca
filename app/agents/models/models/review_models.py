#!/usr/bin/env python3
"""
Data models for Paper Review Pipeline

Defines typed data structures for paper content, discipline classification,
review reports, and evaluation entries.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


# ============================================================================
# Enums
# ============================================================================


class ReviewRecommendation(Enum):
    """Review recommendation types"""

    ACCEPT = "Accept"
    MINOR_REVISION = "Minor Revision"
    MAJOR_REVISION = "Major Revision"
    REJECT = "Reject"


# ============================================================================
# Paper Content Models (Phase 1 Output)
# ============================================================================


@dataclass
class PaperSection:
    """A section of the academic paper"""

    section_id: str
    section_name: str
    section_type: str  # "introduction", "methods", "results", "discussion", etc.
    content: str  # Markdown content
    section_order: int


@dataclass
class PaperContent:
    """Parsed paper content from Phase 1"""

    # Basic information
    title: str
    abstract: str
    keywords: List[str]

    # Section content
    sections: List[PaperSection]

    # Extracted features for discipline classification
    methodology_terms: List[str]
    domain_terms: List[str]
    potential_disciplines: List[str]

    # Metadata
    structured_content_overview_id: str
    original_file_id: Optional[str] = None

    def get_full_text(self) -> str:
        """Get full paper text for analysis"""
        parts = [
            f"# {self.title}",
            "",
            "## Abstract",
            self.abstract,
            "",
            f"**Keywords**: {', '.join(self.keywords)}" if self.keywords else "",
            "",
        ]
        for section in sorted(self.sections, key=lambda s: s.section_order):
            parts.append(f"## {section.section_name}")
            parts.append(section.content)
            parts.append("")
        return "\n".join(parts)


# ============================================================================
# Discipline Classification Models (Phase 2 Output)
# ============================================================================


@dataclass
class DisciplineResult:
    """A single discipline classification result"""

    discipline_id: int  # 1-23
    name: str
    relevance_score: float  # 0.0-1.0
    evidence: str = ""  # Supporting evidence from paper


@dataclass
class DisciplineClassification:
    """Complete discipline classification output"""

    disciplines: List[DisciplineResult]  # Max 3 disciplines
    confidence_score: float  # Overall confidence 0.0-1.0
    classification_reasoning: str
    discipline_classification_id: str  # MCP analysis ID

    def get_primary_discipline(self) -> Optional[DisciplineResult]:
        """Get the primary (highest score) discipline"""
        if not self.disciplines:
            return None
        return max(self.disciplines, key=lambda d: d.relevance_score)

    def get_discipline_names(self) -> List[str]:
        """Get list of discipline names"""
        return [d.name for d in self.disciplines]


# ============================================================================
# Review Report Models (Phase 3 Output)
# ============================================================================


@dataclass
class MajorConcern:
    """A major concern in the review"""

    category: str  # Category title (e.g., "Conceptual Issues")
    description: str  # Detailed description
    subconcerns: List[str] = field(default_factory=list)  # Sub-points
    evidence: List[str] = field(default_factory=list)  # Supporting evidence


@dataclass
class MinorIssue:
    """A minor issue in the review"""

    description: str
    location: Optional[str] = None  # Reference to paper section/page


@dataclass
class LiteratureIssue:
    """Missing or incompletely integrated literature"""

    issue_type: str  # "missing" or "incomplete_integration"
    description: str
    suggested_references: List[str] = field(default_factory=list)


@dataclass
class ReviewReport:
    """A single expert review report (Stage 3.1 output)"""

    report_id: str  # e.g., "report_1", "report_2"
    expert_role: str  # e.g., "Causal Inference Expert"
    expert_focus: str  # What this expert focuses on

    # Report content
    summary: str
    assessment: str  # Balanced evaluation
    major_concerns: List[MajorConcern]
    minor_issues: List[MinorIssue]
    literature_issues: List[LiteratureIssue]
    conclusion: str
    recommendation: ReviewRecommendation

    # Metadata
    word_count: int = 0
    model_used: str = "sonnet"  # Model used for generation


@dataclass
class EvaluationEntry:
    """An entry in the evaluation CSV (Stage 3.2 output)"""

    ref_id: str  # e.g., "Report_1-M1", "Report_2-Mi3"
    key_point: str  # Summary of the feedback point
    evaluation: bool  # True = Yes (valid), False = No (invalid)
    ai_analysis: str  # Brief explanation
    user_decision: Optional[bool] = None  # For future user override
    user_comments: Optional[str] = None


@dataclass
class FinalReviewReport:
    """Final consolidated review report (Stage 3.3 output)"""

    paper_title: str
    recommendation: ReviewRecommendation

    # Report content
    summary: str
    major_concern_categories: List[MajorConcern]  # 3 categories
    minor_issues: List[MinorIssue]
    literature_issues: List[LiteratureIssue]
    conclusion: str

    # Metadata
    disciplines: List[DisciplineResult]
    expert_roles_used: List[str]
    total_individual_reports: int
    valid_points_included: int
    total_points_evaluated: int
    generation_timestamp: str

    # Markdown output
    markdown_content: str = ""

    def to_markdown(self) -> str:
        """Convert to formatted markdown"""
        if self.markdown_content:
            return self.markdown_content

        lines = [
            f"# Peer Review Report: {self.paper_title}",
            "",
            "## Summary and Recommendation",
            self.summary,
            "",
            f"**Recommendation**: {self.recommendation.value}",
            "",
        ]

        # Major concerns
        for i, concern in enumerate(self.major_concern_categories, 1):
            lines.append(f"## Major Concern Category {i}: {concern.category}")
            lines.append(concern.description)
            if concern.subconcerns:
                for j, sub in enumerate(concern.subconcerns, 1):
                    lines.append(f"### {i}.{j} {sub}")
            lines.append("")

        # Minor issues
        lines.append("## Minor Issues")
        for i, issue in enumerate(self.minor_issues, 1):
            loc = f" [{issue.location}]" if issue.location else ""
            lines.append(f"{i}. {issue.description}{loc}")
        lines.append("")

        # Literature issues
        if self.literature_issues:
            lines.append("## Missing Literature and Incomplete Integration")
            missing = [li for li in self.literature_issues if li.issue_type == "missing"]
            incomplete = [
                li for li in self.literature_issues if li.issue_type == "incomplete_integration"
            ]
            if missing:
                lines.append("### Missing Literature")
                for li in missing:
                    lines.append(f"- {li.description}")
            if incomplete:
                lines.append("### Incomplete Integration")
                for li in incomplete:
                    lines.append(f"- {li.description}")
            lines.append("")

        # Conclusion
        lines.append("## Conclusion")
        lines.append(self.conclusion)
        lines.append("")

        # Metadata
        lines.append("---")
        lines.append("")
        lines.append("*Report generated by AI Peer Review System*")
        lines.append("")
        lines.append(f"*Disciplines: {', '.join(d.name for d in self.disciplines)}*")
        lines.append("")
        lines.append(f"*Generation Date: {self.generation_timestamp}*")

        return "\n".join(lines)


# ============================================================================
# Pipeline Result Model
# ============================================================================


@dataclass
class PaperReviewResult:
    """Complete paper review pipeline result"""

    # Phase 1 output
    paper_content: PaperContent

    # Phase 2 output
    discipline_classification: DisciplineClassification

    # Phase 3 output
    individual_reports: List[ReviewReport]
    evaluation_entries: List[EvaluationEntry]
    final_report: FinalReviewReport
    evaluation_csv: str  # Raw CSV content

    # Phase 4 output
    paper_review_id: str
    web_view_url: str

    # Statistics
    statistics: Dict[str, Any] = field(default_factory=dict)


# ============================================================================
# Configuration Models
# ============================================================================


@dataclass
class ExpertConfig:
    """Configuration for an expert reviewer"""

    name: str
    focus: str
    model: str = "sonnet"  # "opus", "sonnet", "haiku"
    is_dynamic: bool = False  # Whether role adapts based on discipline


@dataclass
class ModelStrategy:
    """Model selection strategy for different stages"""

    report_1: str = "sonnet"
    report_2: str = "sonnet"
    report_3: str = "sonnet"
    report_4: str = "haiku"
    report_5: str = "haiku"
    evaluation: str = "haiku"
    final_report: str = "sonnet"

    def get_model_for_report(self, report_num: int) -> str:
        """Get model for a specific report number"""
        return getattr(self, f"report_{report_num}", "sonnet")


@dataclass
class PipelineConfig:
    """Configuration for the review pipeline"""

    num_reports: int = 5
    model_strategy: ModelStrategy = field(default_factory=ModelStrategy)
    expert_configs: Dict[int, ExpertConfig] = field(default_factory=dict)
    word_limit_individual: int = 3000
    word_limit_final: int = 4000
    timeout_per_report: int = 300  # seconds
    timeout_total: int = 1800  # seconds
