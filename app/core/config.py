"""
Configuration Management
"""

from typing import Optional
from oxsci_shared_core.config import BaseConfig


class Config(BaseConfig):
    """
    Application configuration

    MCP server configuration is now managed through JSON config files:
    - app/config/mcp/base.json - Base configuration
    - app/config/mcp/dev.json - Local development overrides
    - app/config/mcp/test.json - Test environment overrides
    - app/config/mcp/prod.json - Production environment overrides
    """

    # ========================================================================
    # Service Configuration
    # ========================================================================

    # Agent service always use port 8080
    SERVICE_PORT: int = 8080

    # MCP environment configuration
    # Do not set these here, use .env to set MCP_ENV to "dev" for local dev
    MCP_ENV: str = ""
    MCP_PROXY_URL: str = ""
    PROXY_API_KEY: str = ""

    # ========================================================================
    # Claude Code Integration
    # ========================================================================

    # Claude Code integration mode: "cli" or "sdk"
    # - cli: Use subprocess-based CLI (default, production-ready)
    # - sdk: Use Python SDK (experimental, better API but tighter coupling)
    CLAUDE_CODE_MODE: str = "sdk"

    # ========================================================================
    # Model Selection
    # ========================================================================

    OPUS_MODEL: str = "sonnet"
    SONNET_MODEL: str = "sonnet"

    # Timeout settings (in seconds)
    GLOBAL_ANALYSIS_TIMEOUT: int = 1200

    # ========================================================================
    # File Management
    # ========================================================================

    # Temporary file settings
    CLEAN_TMP_FILE: bool = True
    TMP_PATH: str = "/tmp"

    # ========================================================================
    # Discipline Classifier Configuration
    # ========================================================================

    # Debug phases for classifier pipeline
    # Valid values: ["parser", "classifier"]
    # - parser: Phase 1 - Paper Parsing
    # - classifier: Phase 2 - Discipline Classification
    CLASSIFIER_DEBUG_PHASES: Optional[str] = None


# Global config instance
config = Config()
