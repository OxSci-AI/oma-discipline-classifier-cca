#!/usr/bin/env python3
"""
Test File for Discipline Classifier Agent
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from oxsci_oma_core.test_module import agent_test, run_tests_from_cli


@agent_test(
    verbose="stdout",
    framework="claude",
    task_input={
        "file_id": "08c6dfca-bf91-4361-a0c7-80c74b222494",  # PDF file ID to classify
    },
)
def test_discipline_classifier():
    """Test the discipline classifier agent - classify paper into disciplines (1-23)

    This agent implements:
    - Phase 1: Paper parsing and content extraction
    - Phase 2: Discipline classification (ID-based selection 1-23)

    Expected execution time: 3-5 minutes
    """
    from app.agents.discipline_classifier_cca import DisciplineClassifierCCA

    return DisciplineClassifierCCA


def main():
    """CLI entry point for running tests

    Usage:
        # Run the test
        poetry run python tests/test_agents.py --test classifier

        # Run all tests
        poetry run python tests/test_agents.py --all

        # Enable verbose logging
        poetry run python tests/test_agents.py --test classifier -v
    """
    # Define test map
    test_map = {
        "classifier": test_discipline_classifier,
    }

    # Run tests from CLI
    sys.exit(run_tests_from_cli(test_map))


if __name__ == "__main__":
    main()
