"""Query rewriter for improved governance retrieval.

Expands abbreviations and maps framework-specific terminology.
Pure function — no I/O, no database access.
"""

from __future__ import annotations

import structlog

log = structlog.get_logger()

# Governance-specific abbreviation expansions
ABBREVIATION_MAP: dict[str, str] = {
    "TEVV": "test evaluation verification validation",
    "RMF": "risk management framework",
    "AI RMF": "artificial intelligence risk management framework",
    "FRIA": "fundamental rights impact assessment",
    "RBI": "remote biometric identification",
    "QMS": "quality management system",
    "GPAI": "general purpose artificial intelligence",
    "DPIA": "data protection impact assessment",
    "PII": "personally identifiable information",
    "MLOps": "machine learning operations",
}

# Cross-framework terminology mapping
TERMINOLOGY_MAP: dict[str, dict[str, list[str]]] = {
    "risk management": {
        "NIST AI RMF": ["govern", "risk assessment", "risk identification"],
        "EU AI Act": ["article 9", "risk management system"],
    },
    "transparency": {
        "NIST AI RMF": ["govern", "transparency", "documentation"],
        "EU AI Act": ["article 13", "article 50", "disclosure"],
    },
    "human oversight": {
        "NIST AI RMF": ["manage", "human-in-the-loop", "oversight"],
        "EU AI Act": ["article 14", "human oversight", "override"],
    },
    "bias": {
        "NIST AI RMF": ["measure", "fairness", "bias metrics"],
        "EU AI Act": ["article 10", "data governance", "non-discrimination"],
    },
    "data governance": {
        "NIST AI RMF": ["map", "data quality", "training data"],
        "EU AI Act": ["article 10", "data governance", "quality criteria"],
    },
}


class QueryRewriter:
    """Expand and rewrite queries for better retrieval.

    Handles:
    - Abbreviation expansion ("TEVV" -> "test, evaluation, verification, validation")
    - Framework-specific terminology mapping
    - Query decomposition for complex multi-part questions
    """

    def rewrite(self, query: str, frameworks: list[str]) -> list[str]:
        """Return expanded queries for multi-framework search.

        Always includes the original query. Adds expanded variants
        for better recall without sacrificing precision.
        """
        log.info(
            "query_rewriter.rewriting",
            framework_count=len(frameworks),
        )
        queries = [query]

        # Expand abbreviations
        expanded = self._expand_abbreviations(query)
        if expanded != query:
            queries.append(expanded)

        # Add framework-specific terms
        for topic, fw_terms in TERMINOLOGY_MAP.items():
            if topic.lower() in query.lower():
                for fw in frameworks:
                    if fw in fw_terms:
                        extra_terms = " ".join(fw_terms[fw])
                        queries.append(f"{query} {extra_terms}")

        return queries

    def _expand_abbreviations(self, query: str) -> str:
        """Replace known abbreviations with expanded forms."""
        result = query
        for abbr, expansion in ABBREVIATION_MAP.items():
            if abbr in result:
                result = result.replace(abbr, expansion)
        return result
