"""Governance domain constants.

Single source of truth for framework, policy, and status identifiers.
"""

# Framework identifiers
FRAMEWORK_NIST_AI_RMF = "NIST AI RMF"
FRAMEWORK_ID_NIST_AI_RMF = "nist-ai-rmf"

# Policy categories (lowercase, matching YAML fixtures)
CATEGORY_GOVERN = "govern"
CATEGORY_MAP = "map"
CATEGORY_MEASURE = "measure"
CATEGORY_MANAGE = "manage"

# Evaluation status values
STATUS_PASS = "pass"
STATUS_FAIL = "fail"
STATUS_WARN = "warn"
STATUS_NA = "na"

# Governance verdict states (from synthesizer)
VERDICT_PROCEED = "proceed"
VERDICT_ESCALATE = "escalate"
VERDICT_BLOCKED = "blocked"

# Severity levels
SEVERITY_REQUIRED = "required"
SEVERITY_WARNING = "warning"
SEVERITY_INFO = "info"

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

# EU AI Act framework identifiers
FRAMEWORK_EU_AI_ACT = "EU AI Act"
FRAMEWORK_ID_EU_AI_ACT = "eu-ai-act"

# EU AI Act risk levels
EU_RISK_UNACCEPTABLE = "unacceptable"
EU_RISK_HIGH = "high"
EU_RISK_LIMITED = "limited"
EU_RISK_MINIMAL = "minimal"

# EU AI Act categories
EU_CATEGORY_PROHIBITED = "prohibited"
EU_CATEGORY_HIGH_RISK = "high-risk"
EU_CATEGORY_LIMITED = "limited"
EU_CATEGORY_TRANSPARENCY = "transparency"

# Well-known EU AI Act policy IDs
EU_ART5_1_SOCIAL_SCORING = "eu-art5-1-social-scoring"
EU_ART9_RISK_MANAGEMENT = "eu-art9-risk-management"
EU_ART14_HUMAN_OVERSIGHT = "eu-art14-human-oversight"
EU_ART50_1_CHATBOT_DISCLOSURE = "eu-art50-1-chatbot-disclosure"

# Total EU AI Act policies in fixtures
EU_POLICY_COUNT = 21
