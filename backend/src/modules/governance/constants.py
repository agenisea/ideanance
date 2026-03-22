"""Governance domain constants.

Single source of truth for framework, policy, and status identifiers.
StrEnums for type safety and autocomplete (Python 3.12+).
"""

from enum import StrEnum

# --- Governance State (unified lens + verdict vocabulary) ---


class GovernanceState(StrEnum):
    """Unified state for lens findings and synthesizer verdicts.

    Dominance order: BLOCKED > ESCALATE > PASS.
    PROCEED is synthesizer-only (all lenses passed).
    """

    PASS = "pass"
    ESCALATE = "escalate"
    BLOCKED = "blocked"
    PROCEED = "proceed"


# --- Severity ---


class Severity(StrEnum):
    REQUIRED = "required"
    WARNING = "warning"
    INFO = "info"


# --- Lens Names ---


class LensName(StrEnum):
    TRANSPARENCY = "transparency"
    PRIVACY = "privacy"
    DIGNITY = "dignity"
    ACCOUNTABILITY = "accountability"
    BOUNDARY = "boundary"


# --- EU AI Act Risk Levels ---


class EuRiskLevel(StrEnum):
    UNACCEPTABLE = "unacceptable"
    HIGH = "high"
    LIMITED = "limited"
    MINIMAL = "minimal"


# --- EU AI Act Categories ---


class EuCategory(StrEnum):
    PROHIBITED = "prohibited"
    HIGH_RISK = "high-risk"
    LIMITED = "limited"
    TRANSPARENCY = "transparency"


# --- Governance Defaults ---
DEFAULT_CONFIDENCE: float = 1.0


# --- Framework identifiers ---
FRAMEWORK_NIST_AI_RMF = "NIST AI RMF"
FRAMEWORK_ID_NIST_AI_RMF = "nist-ai-rmf"
FRAMEWORK_EU_AI_ACT = "EU AI Act"
FRAMEWORK_ID_EU_AI_ACT = "eu-ai-act"

# Policy categories (lowercase, matching YAML fixtures)
CATEGORY_GOVERN = "govern"
CATEGORY_MAP = "map"
CATEGORY_MEASURE = "measure"
CATEGORY_MANAGE = "manage"

# Well-known NIST AI RMF policy IDs (subset used in tests and fixtures)
NIST_GOVERN_1_1 = "nist-govern-1.1"
NIST_GOVERN_1_2 = "nist-govern-1.2"
NIST_GOVERN_1_3 = "nist-govern-1.3"
NIST_GOVERN_1_4 = "nist-govern-1.4"
NIST_MAP_1_1 = "nist-map-1.1"
NIST_MAP_1_5 = "nist-map-1.5"
NIST_MANAGE_2_1 = "nist-manage-2.1"
NIST_MEASURE_2_5 = "nist-measure-2.5"

# Total NIST AI RMF policies in fixtures
NIST_POLICY_COUNT = 20

# Well-known EU AI Act policy IDs
EU_ART5_1_SOCIAL_SCORING = "eu-art5-1-social-scoring"
EU_ART9_RISK_MANAGEMENT = "eu-art9-risk-management"
EU_ART14_HUMAN_OVERSIGHT = "eu-art14-human-oversight"
EU_ART50_1_CHATBOT_DISCLOSURE = "eu-art50-1-chatbot-disclosure"

# Total EU AI Act policies in fixtures
EU_POLICY_COUNT = 21

# --- Backward compatibility aliases (deprecated, remove after PLAN69) ---
STATUS_PASS = GovernanceState.PASS
STATUS_FAIL = GovernanceState.BLOCKED
STATUS_WARN = GovernanceState.ESCALATE
STATUS_NA = "na"
VERDICT_PROCEED = GovernanceState.PROCEED
VERDICT_ESCALATE = GovernanceState.ESCALATE
VERDICT_BLOCKED = GovernanceState.BLOCKED
SEVERITY_REQUIRED = Severity.REQUIRED
SEVERITY_WARNING = Severity.WARNING
SEVERITY_INFO = Severity.INFO
EU_RISK_UNACCEPTABLE = EuRiskLevel.UNACCEPTABLE
EU_RISK_HIGH = EuRiskLevel.HIGH
EU_RISK_LIMITED = EuRiskLevel.LIMITED
EU_RISK_MINIMAL = EuRiskLevel.MINIMAL
EU_CATEGORY_PROHIBITED = EuCategory.PROHIBITED
EU_CATEGORY_HIGH_RISK = EuCategory.HIGH_RISK
EU_CATEGORY_LIMITED = EuCategory.LIMITED
EU_CATEGORY_TRANSPARENCY = EuCategory.TRANSPARENCY
