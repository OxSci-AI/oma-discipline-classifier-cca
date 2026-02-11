#!/usr/bin/env python3
"""
Discipline Models for Paper Review Pipeline

Defines the 23 academic discipline categories and their mappings to expert roles.
Based on the specification in PAPER_REVIEW_PIPELINE_SPEC.md.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


# ============================================================================
# Discipline Definitions (23 Categories)
# ============================================================================


@dataclass
class DisciplineDefinition:
    """Definition of an academic discipline"""

    id: int
    name: str
    keywords: List[str]  # Keywords that indicate this discipline
    description: str = ""


# Complete list of 23 disciplines with ID-based selection
DISCIPLINES: Dict[int, DisciplineDefinition] = {
    1: DisciplineDefinition(
        id=1,
        name="Computer Science",
        keywords=[
            "AI", "ML", "machine learning", "neural network", "deep learning",
            "algorithm", "software", "programming", "NLP", "computer vision",
            "data mining", "artificial intelligence", "computing", "database",
        ],
        description="Artificial intelligence, machine learning, algorithms, software engineering",
    ),
    2: DisciplineDefinition(
        id=2,
        name="Medicine",
        keywords=[
            "clinical", "diagnosis", "treatment", "patient", "medical",
            "disease", "therapy", "hospital", "physician", "healthcare",
            "surgical", "pharmaceutical", "pathology", "oncology",
        ],
        description="Clinical research, diagnostics, therapeutics, patient care",
    ),
    3: DisciplineDefinition(
        id=3,
        name="Chemistry",
        keywords=[
            "compound", "reaction", "synthesis", "molecule", "chemical",
            "catalyst", "polymer", "organic", "inorganic", "spectroscopy",
            "electrochemistry", "biochemistry", "analytical",
        ],
        description="Chemical compounds, reactions, synthesis, molecular analysis",
    ),
    4: DisciplineDefinition(
        id=4,
        name="Biology",
        keywords=[
            "gene", "cell", "evolution", "bioinformatics", "protein",
            "DNA", "RNA", "genome", "species", "organism", "molecular",
            "ecology", "genetics", "microbiology", "neuroscience",
        ],
        description="Genetics, cellular biology, evolution, bioinformatics",
    ),
    5: DisciplineDefinition(
        id=5,
        name="Materials Science",
        keywords=[
            "nanomaterial", "crystal", "alloy", "polymer", "semiconductor",
            "ceramic", "composite", "thin film", "surface", "nanoparticle",
            "graphene", "superconductor", "biomaterial",
        ],
        description="Nanomaterials, crystals, alloys, material properties",
    ),
    6: DisciplineDefinition(
        id=6,
        name="Physics",
        keywords=[
            "quantum", "particle", "thermodynamics", "mechanics", "optics",
            "electromagnetic", "relativity", "condensed matter", "nuclear",
            "astrophysics", "photon", "wave", "energy",
        ],
        description="Quantum mechanics, particle physics, thermodynamics",
    ),
    7: DisciplineDefinition(
        id=7,
        name="Geology",
        keywords=[
            "rock", "mineral", "tectonic", "sediment", "volcanic",
            "earthquake", "geochemistry", "stratigraphy", "paleontology",
            "hydrology", "geophysics", "geological",
        ],
        description="Rocks, minerals, tectonics, geological processes",
    ),
    8: DisciplineDefinition(
        id=8,
        name="Psychology",
        keywords=[
            "behavior", "cognitive", "psychological", "mental", "emotion",
            "perception", "memory", "personality", "therapy", "disorder",
            "consciousness", "developmental", "social psychology",
        ],
        description="Behavior, cognition, mental processes, psychological research",
    ),
    9: DisciplineDefinition(
        id=9,
        name="Art",
        keywords=[
            "visual art", "music", "aesthetic", "artistic", "painting",
            "sculpture", "performance", "design", "creative", "museum",
            "cultural heritage", "art history",
        ],
        description="Visual arts, music, aesthetics, artistic expression",
    ),
    10: DisciplineDefinition(
        id=10,
        name="History",
        keywords=[
            "historical", "era", "civilization", "ancient", "medieval",
            "modern history", "archaeology", "archive", "heritage",
            "historiography", "historical event", "dynasty",
        ],
        description="Historical events, eras, civilizations, historiography",
    ),
    11: DisciplineDefinition(
        id=11,
        name="Geography",
        keywords=[
            "spatial", "regional", "climate", "landscape", "urban",
            "GIS", "cartography", "territory", "migration", "population",
            "geospatial", "environmental geography",
        ],
        description="Spatial analysis, regional studies, climate, landscapes",
    ),
    12: DisciplineDefinition(
        id=12,
        name="Sociology",
        keywords=[
            "social", "culture", "institution", "community", "inequality",
            "class", "gender", "race", "ethnicity", "social structure",
            "sociological", "social change", "social behavior",
        ],
        description="Social structures, culture, institutions, social behavior",
    ),
    13: DisciplineDefinition(
        id=13,
        name="Business",
        keywords=[
            "management", "marketing", "finance", "entrepreneurship",
            "strategy", "organization", "corporate", "MBA", "leadership",
            "innovation", "business model", "supply chain",
        ],
        description="Management, marketing, finance, business strategy",
    ),
    14: DisciplineDefinition(
        id=14,
        name="Political Science",
        keywords=[
            "government", "policy", "political", "democracy", "election",
            "parliament", "legislation", "diplomacy", "international relations",
            "political party", "voting", "governance",
        ],
        description="Government, policy, political systems, international relations",
    ),
    15: DisciplineDefinition(
        id=15,
        name="Economics",
        keywords=[
            "market", "equilibrium", "financial", "monetary", "fiscal",
            "trade", "GDP", "inflation", "microeconomics", "macroeconomics",
            "econometric", "price", "demand", "supply",
        ],
        description="Markets, economic theory, financial systems, trade",
    ),
    16: DisciplineDefinition(
        id=16,
        name="Philosophy",
        keywords=[
            "ethics", "logic", "metaphysics", "epistemology", "ontology",
            "moral", "philosophical", "reasoning", "existential",
            "phenomenology", "aesthetics philosophy", "mind",
        ],
        description="Ethics, logic, metaphysics, epistemology, philosophical reasoning",
    ),
    17: DisciplineDefinition(
        id=17,
        name="Mathematics",
        keywords=[
            "theorem", "proof", "equation", "algebra", "calculus",
            "topology", "number theory", "statistics", "probability",
            "differential", "integral", "mathematical",
        ],
        description="Theorems, proofs, equations, mathematical analysis",
    ),
    18: DisciplineDefinition(
        id=18,
        name="Engineering",
        keywords=[
            "design", "system", "optimization", "mechanical", "electrical",
            "civil", "structural", "control", "robotics", "manufacturing",
            "engineering", "prototype", "simulation",
        ],
        description="Engineering design, systems, optimization, technical implementation",
    ),
    19: DisciplineDefinition(
        id=19,
        name="Environmental Science",
        keywords=[
            "ecology", "pollution", "climate change", "sustainability",
            "biodiversity", "conservation", "ecosystem", "carbon",
            "environmental impact", "renewable", "green",
        ],
        description="Ecology, pollution, climate change, sustainability",
    ),
    20: DisciplineDefinition(
        id=20,
        name="Agricultural and Food Sciences",
        keywords=[
            "crop", "food technology", "agriculture", "livestock", "soil",
            "irrigation", "harvest", "nutrition", "food safety",
            "agronomy", "horticulture", "aquaculture",
        ],
        description="Crops, food technology, agriculture, nutrition",
    ),
    21: DisciplineDefinition(
        id=21,
        name="Education",
        keywords=[
            "pedagogy", "curriculum", "learning", "teaching", "student",
            "classroom", "educational", "assessment", "literacy",
            "higher education", "school", "instruction",
        ],
        description="Pedagogy, curriculum, learning, teaching methods",
    ),
    22: DisciplineDefinition(
        id=22,
        name="Law",
        keywords=[
            "legal", "regulation", "case", "court", "statute",
            "contract", "liability", "criminal", "constitutional",
            "jurisdiction", "litigation", "judicial",
        ],
        description="Legal systems, regulations, case law, jurisprudence",
    ),
    23: DisciplineDefinition(
        id=23,
        name="Linguistics",
        keywords=[
            "language", "syntax", "semantics", "phonology", "morphology",
            "discourse", "linguistic", "grammar", "translation",
            "sociolinguistics", "pragmatics", "corpus",
        ],
        description="Language, syntax, semantics, linguistic analysis",
    ),
}


# ============================================================================
# Discipline → Expert Role Mapping
# ============================================================================


# Mapping from discipline to suggested expert roles
# For each discipline, provide 5 expert roles in order of priority
DISCIPLINE_TO_EXPERT_MAPPING: Dict[str, List[str]] = {
    # STEM Sciences
    "Computer Science": [
        "Algorithm & Complexity Expert",      # Technical depth
        "Experimental Design Expert",          # Benchmark, ablation, baseline
        "Systems & Implementation Expert",     # Reproducibility, engineering
        "Related Work & Novelty Expert",       # Literature, contribution
        "Clarity & Presentation Expert",       # Writing quality
    ],
    "Mathematics": ["Statistical Methodologist", "Formal Methods Expert"],
    "Physics": ["Theoretical Physicist", "Experimental Methodologist"],
    "Engineering": ["Systems Engineering Expert", "Technical Reviewer"],
    "Chemistry": ["Analytical Chemistry Expert", "Experimental Methodologist"],
    "Biology": ["Molecular Biology Expert", "Bioinformatics Specialist"],
    "Materials Science": ["Materials Characterization Expert", "Experimental Methodologist"],

    # Medical/Life Sciences
    "Medicine": ["Clinical Research Expert", "Biostatistician"],
    "Environmental Science": ["Environmental Impact Assessor", "Ecological Methodologist"],
    "Agricultural and Food Sciences": ["Agricultural Research Expert", "Food Safety Specialist"],

    # Social Sciences
    "Economics": ["Empirical Economics Scholar", "Causal Inference Expert"],
    "Business": ["Management Research Expert", "Quantitative Finance Specialist"],
    "Psychology": ["Experimental Psychology Expert", "Statistical Methodologist"],
    "Sociology": ["Qualitative Research Expert", "Social Statistics Specialist"],
    "Political Science": ["Policy Analysis Expert", "Comparative Politics Scholar"],
    "Education": ["Educational Research Methodologist", "Assessment Specialist"],

    # Humanities
    "Philosophy": ["Philosophical Argumentation Expert", "Logic Specialist"],
    "History": ["Historical Research Methodologist", "Archival Expert"],
    "Art": ["Art Criticism Expert", "Aesthetic Theory Specialist"],
    "Linguistics": ["Linguistic Analysis Expert", "Corpus Linguistics Specialist"],
    "Law": ["Legal Research Expert", "Case Analysis Specialist"],
    "Geography": ["Spatial Analysis Expert", "GIS Methodologist"],
    "Geology": ["Geological Analysis Expert", "Field Methods Specialist"],
}


# Default expert roles when no discipline-specific mapping exists
DEFAULT_EXPERT_ROLES: List[str] = [
    "Methodology Expert",
    "Domain Expert",
    "Statistical Reviewer",
    "Literature Expert",
    "Integration Specialist",
]


# ============================================================================
# Expert Role Configuration
# ============================================================================


@dataclass
class ExpertRole:
    """Configuration for an expert reviewer role"""

    id: int
    name: str
    focus: str
    model: str = "sonnet"  # "opus", "sonnet", "haiku"
    is_dynamic: bool = False  # Whether this role adapts based on discipline


# Default expert roles for the 5-report pipeline (generic fallback)
DEFAULT_EXPERT_CONFIGS: Dict[int, ExpertRole] = {
    1: ExpertRole(
        id=1,
        name="Methodology Expert",
        focus="Research methodology, experimental design, validity of approach",
        model="sonnet",
        is_dynamic=True,
    ),
    2: ExpertRole(
        id=2,
        name="Technical Expert",
        focus="Technical soundness, implementation details, reproducibility",
        model="sonnet",
        is_dynamic=True,
    ),
    3: ExpertRole(
        id=3,
        name="Domain Expert",
        focus="Domain knowledge, literature integration, theoretical foundation",
        model="sonnet",
        is_dynamic=True,
    ),
    4: ExpertRole(
        id=4,
        name="Related Work Expert",
        focus="Literature coverage, novelty assessment, positioning",
        model="haiku",
        is_dynamic=True,
    ),
    5: ExpertRole(
        id=5,
        name="Presentation Expert",
        focus="Clarity, logical coherence, writing quality",
        model="haiku",
        is_dynamic=True,
    ),
}


# Discipline-specific expert focus descriptions
DISCIPLINE_EXPERT_FOCUS: Dict[str, Dict[str, str]] = {
    "Computer Science": {
        "Algorithm & Complexity Expert": "Algorithm correctness, computational complexity, theoretical analysis, proof validity",
        "Experimental Design Expert": "Benchmark selection, baseline fairness, ablation studies, hyperparameter sensitivity, statistical significance",
        "Systems & Implementation Expert": "Code quality, reproducibility, scalability, engineering practices, open-source availability",
        "Related Work & Novelty Expert": "Literature coverage, novelty claims, fair comparison with prior work, contribution clarity",
        "Clarity & Presentation Expert": "Writing quality, figure clarity, notation consistency, logical flow",
    },
    "Engineering": {
        "Systems Engineering Expert": "System design, architecture validity, integration aspects",
        "Technical Reviewer": "Implementation feasibility, engineering constraints, practical applicability",
        "Domain Expert": "Domain-specific requirements, standards compliance",
        "Experimental Methodologist": "Testing methodology, validation procedures, measurement accuracy",
        "Integration Specialist": "Overall coherence, cross-system compatibility",
    },
}


# ============================================================================
# Helper Functions
# ============================================================================


def get_discipline_by_id(discipline_id: int) -> Optional[DisciplineDefinition]:
    """Get discipline definition by ID"""
    return DISCIPLINES.get(discipline_id)


def get_discipline_by_name(name: str) -> Optional[DisciplineDefinition]:
    """Get discipline definition by name (case-insensitive)"""
    name_lower = name.lower()
    for disc in DISCIPLINES.values():
        if disc.name.lower() == name_lower:
            return disc
    return None


def get_all_discipline_names() -> List[str]:
    """Get list of all discipline names"""
    return [d.name for d in DISCIPLINES.values()]


def get_discipline_list_for_prompt() -> str:
    """Generate formatted discipline list for prompts"""
    lines = ["| ID | Discipline | Description |", "|----|-----------:|-------------|"]
    for disc in DISCIPLINES.values():
        lines.append(f"| {disc.id} | {disc.name} | {disc.description} |")
    return "\n".join(lines)


def get_keyword_section_for_prompt() -> str:
    """Generate keyword → ID mapping section for prompts"""
    lines = []
    for disc in DISCIPLINES.values():
        keywords_str = ", ".join(disc.keywords[:5])  # Top 5 keywords
        lines.append(f"- **ID {disc.id} ({disc.name})**: {keywords_str}")
    return "\n".join(lines)


def get_expert_roles_for_disciplines(
    discipline_names: List[str],
    num_experts: int = 5
) -> List[ExpertRole]:
    """
    Get expert roles based on identified disciplines.

    For disciplines with custom expert mappings (like Computer Science),
    all 5 expert roles are replaced with discipline-specific roles.

    Args:
        discipline_names: List of identified discipline names
        num_experts: Number of expert roles needed

    Returns:
        List of ExpertRole configurations
    """
    # If no disciplines identified, return defaults
    if not discipline_names:
        return list(DEFAULT_EXPERT_CONFIGS.values())[:num_experts]

    # Get primary discipline
    primary = discipline_names[0]

    # Check if we have discipline-specific expert mapping
    suggested = DISCIPLINE_TO_EXPERT_MAPPING.get(primary, [])
    focus_mapping = DISCIPLINE_EXPERT_FOCUS.get(primary, {})

    # If discipline has custom expert mapping with 5 roles, use all of them
    if len(suggested) >= 5:
        experts = []
        models = ["sonnet", "sonnet", "sonnet", "haiku", "haiku"]  # Model distribution
        for i, expert_name in enumerate(suggested[:num_experts]):
            focus = focus_mapping.get(
                expert_name,
                f"Expert analysis from {expert_name} perspective for {primary}"
            )
            experts.append(ExpertRole(
                id=i + 1,
                name=expert_name,
                focus=focus,
                model=models[i] if i < len(models) else "haiku",
                is_dynamic=True,
            ))
        return experts

    # Otherwise, use default configuration with partial updates
    experts = list(DEFAULT_EXPERT_CONFIGS.values())

    # Update dynamic roles if we have some suggestions
    if len(suggested) >= 1:
        experts[2] = ExpertRole(
            id=3,
            name=suggested[0],
            focus=f"Domain expertise in {primary}",
            model="sonnet",
            is_dynamic=True,
        )
    if len(suggested) >= 2:
        experts[3] = ExpertRole(
            id=4,
            name=suggested[1],
            focus=f"Technical expertise related to {primary}",
            model="haiku",
            is_dynamic=True,
        )

    return experts[:num_experts]
