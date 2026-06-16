# Common scoring and GenAI constants for ArchLens
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

COMPLIANCE_SCORE = {
  "Yes": 1.0,
  "Partial": 0.5,
  "No": 0.0,
  "NotApplicable": None
}

WEIGHT_MAP = {
    "Catastrophic": 1.0,
    "Major": 0.75,
    "Moderate": 0.5,
    "Minor": 0.25,
    "Negligible": 0.1
}

# Trade-off decision rules
TRADEOFF_RULES = {
    "Event-driven aggregation & sampling at Operations": {
    "description": "Reduces control chatter and mitigates the O(n²) pressure but adds failure modes.",
    "impacts": {
      "Scalability": 0.20,
      "Performance": 0.10,
      "Reliability": -0.02,
    }
  },
    "Tenant-scoped tokens & egress guardrails": {
    "description": "Improves isolation; some overhead from checks.",
    "impacts": {
      "Security": 0.25,
      "Performance": -0.03
    }
  },
  "Parallelized operation workers": {
    "description": "Parallelized operation workers.",
    "impacts": {
      "Scalability": 0.10,
      "Performance": 0.15
    }
  },
  "runtime_adaptation": {
    "description": "Single deployable artifact supporting multiple clients and deployment targets through configuration, feature flags, and environment variables.",
    "impacts": {
      "Maintainability": 0.12,
      "Modifiability": 0.15,
      "Deployability": 0.15,
      "Portability": 0.12,
      "Scalability": 0.05,
      "Testability": -0.05,
      "Security": -0.03,
      "Operability": 0.08
    }
  },
  "build_time_adaptation": {
    "description": "Separate deployment artifacts generated for each client or platform target.",
    "impacts": {
      "Maintainability": -0.10,
      "Modifiability": -0.08,
      "Deployability": -0.12,
      "Portability": -0.10,
      "Scalability": -0.03,
      "Testability": 0.08,
      "Security": 0.10,
      "Operability": -0.05
    }
  }
}

# Utility: RAG rating
def get_rag(overall: float) -> str:
    if overall >= 0.75:
        return "GOOD"
    elif overall > 0.5:
        return "AVERAGE"
    else:
        return "POOR"

# Utility: Score calculation
def calculate_scores(questions, multipliers=None):
  """
  Calculate attribute and overall scores.

  questions: iterable of AssessmentQuestion-like rows with fields
    - compliance, weight_label, quality_attribute, question_key
  multipliers: optional dict mapping question_key -> multiplier (>0). When provided,
    we treat multiplier as an additional weight scalar: w' = w * multiplier.
    This enables tree-weighted scoring where question weights are amplified by
    normalized importance from the Utility Tree / scenarios.
  """
  multipliers = multipliers or {}
  attr_scores, attr_weights = {}, {}
  for q in questions:
    score = COMPLIANCE_SCORE.get(q.compliance)
    base_w = WEIGHT_MAP.get(q.weight_label, 1.0)
    if score is None:
      continue
    # Apply optional multiplier derived from tree/scenario importance
    m = float(multipliers.get(getattr(q, "question_key", None), 1.0) or 1.0)
    w = base_w * m
    attr = q.quality_attribute
    attr_scores.setdefault(attr, 0.0)
    attr_weights.setdefault(attr, 0.0)
    attr_scores[attr] += score * w
    attr_weights[attr] += w
  attribute_results = {attr: (attr_scores[attr] / attr_weights[attr]) if attr_weights[attr] else 0.0 for attr in attr_scores}
  overall = sum(attribute_results.values()) / len(attribute_results) if attribute_results else 0.0
  rag = get_rag(overall)
  return attribute_results, overall, rag
