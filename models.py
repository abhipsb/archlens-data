from sqlalchemy import Column, Integer, String, ForeignKey, Numeric, Text, TIMESTAMP, Float, Boolean, UniqueConstraint
from sqlalchemy.sql import func
from db import Base

class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    domain = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())

class Assessment(Base):
    __tablename__ = "assessments"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    description = Column(Text)
    status = Column(String)
    overall_score = Column(Numeric)
    overall_rag = Column(String)
    created_at = Column(TIMESTAMP, server_default=func.now())
    attested_by = Column(String)

class QuestionTemplate(Base):
    __tablename__ = "question_templates"
    id = Column(Integer, primary_key=True)
    question_key = Column(String, unique=True)
    text = Column(Text)
    quality_attribute = Column(String)
    weight_label = Column(String)
    category = Column(String)

class AssessmentQuestion(Base):
    __tablename__ = "assessment_questions"
    __table_args__ = (UniqueConstraint('assessment_id', 'question_key', name='uq_assessment_question'),)
    
    id = Column(Integer, primary_key=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    question_key = Column(String)
    quality_attribute = Column(String)
    weight_label = Column(String)
    compliance = Column(String)
    rationale = Column(Text)
    numeric_score = Column(Float)
    category = Column(String)

class Artifact(Base):
    __tablename__ = "artifacts"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    filename = Column(String)
    object_key = Column(String)
    extracted_text = Column(Text)

class ATAMScenarioTemplate(Base):
    __tablename__ = "atam_scenario_templates"
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String, unique=True)
    scenario_desc = Column(Text)
    quality_attribute = Column(String)
    importance = Column(Float)
    acceptance_criteria = Column(Text)

class AssessmentATAMScenario(Base):
    __tablename__ = "assessment_atam_scenarios"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    scenario_id = Column(String, ForeignKey("atam_scenario_templates.scenario_id"))
    tolerance = Column(Float)
    measured_exposure = Column(Float)
    importance = Column(Float)  # Assessment-specific importance override
    selected = Column(Boolean, default=False)  # Whether selected for this assessment

class ScenarioQuestionMapping(Base):
    __tablename__ = "scenario_question_mappings"
    id = Column(Integer, primary_key=True, index=True)
    scenario_id = Column(String, ForeignKey("atam_scenario_templates.scenario_id"))
    question_key = Column(String, ForeignKey("question_templates.question_key"))
    tag = Column(String)
    weight = Column(Float)

class BusinessDriver(Base):
    __tablename__ = "business_drivers"
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"))
    name = Column(String)
    description = Column(Text)

class UtilityTreeNode(Base):
    __tablename__ = "utility_tree_nodes"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"))
    parent_id = Column(Integer, ForeignKey("utility_tree_nodes.id"), nullable=True)
    node_type = Column(String)  # 'driver', 'scenario', 'attribute'
    name = Column(String)
    scenario_id = Column(String, ForeignKey("atam_scenario_templates.scenario_id"), nullable=True)
    importance = Column(Float)

class BusinessDriverScenario(Base):
    __tablename__ = "business_driver_scenarios"
    id = Column(Integer, primary_key=True, index=True)
    assessment_scenario_id = Column(Integer, ForeignKey("assessment_atam_scenarios.id"))
    business_driver_id = Column(Integer, ForeignKey("business_drivers.id"))
    rationale = Column(Text)

class AssessmentScenarioQuestion(Base):
    __tablename__ = "assessment_scenario_questions"
    id = Column(Integer, primary_key=True, index=True)
    assessment_scenario_id = Column(Integer, ForeignKey("assessment_atam_scenarios.id", ondelete="CASCADE"))
    question_key = Column(String, ForeignKey("question_templates.question_key", ondelete="CASCADE"))
    # Association of a scenario instance within an assessment to a question template
    __table_args__ = (UniqueConstraint('assessment_scenario_id', 'question_key', name='uq_assessment_scenario_question'),)

class AiInsight(Base):
    __tablename__ = "ai_insights"
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), index=True)
    kind = Column(String)  # 'tree' | 'tradeoff'
    content = Column(Text)  # LLM result (markdown/text)
    context_json = Column(Text)  # optional context used
    state_json = Column(Text)  # snapshot of state (tree/scenarios or decisions)
    state_hash = Column(String, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
