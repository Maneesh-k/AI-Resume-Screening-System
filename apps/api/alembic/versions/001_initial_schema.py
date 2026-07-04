"""Initial schema

Revision ID: 001
Revises:
Create Date: 2026-07-04
"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = "001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # users
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="recruiter"),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("is_active", sa.Boolean, nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    # jobs
    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("department", sa.String(255)),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("required_skills", postgresql.JSONB, server_default="[]"),
        sa.Column("preferred_skills", postgresql.JSONB, server_default="[]"),
        sa.Column("experience_min", sa.Integer),
        sa.Column("experience_max", sa.Integer),
        sa.Column("location", sa.String(255)),
        sa.Column("salary_min", sa.Integer),
        sa.Column("salary_max", sa.Integer),
        sa.Column("currency", sa.String(10), server_default="USD"),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("pinecone_vector_id", sa.String(255)),
        sa.Column("created_by", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_jobs_status", "jobs", ["status"])

    # candidates
    op.create_table(
        "candidates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE")),
        sa.Column("name", sa.String(255)),
        sa.Column("email", sa.String(255)),
        sa.Column("phone", sa.String(50)),
        sa.Column("resume_s3_key", sa.String(500), nullable=False),
        sa.Column("resume_text", sa.Text),
        sa.Column("parsed_data", postgresql.JSONB),
        sa.Column("experience_years", sa.Float),
        sa.Column("current_title", sa.String(255)),
        sa.Column("current_company", sa.String(255)),
        sa.Column("certifications", postgresql.JSONB, server_default="[]"),
        sa.Column("processing_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("processing_error", sa.Text),
        sa.Column("pinecone_vector_id", sa.String(255)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_candidates_job_id", "candidates", ["job_id"])
    op.create_index("ix_candidates_processing_status", "candidates", ["processing_status"])

    # candidate_skills
    op.create_table(
        "candidate_skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE")),
        sa.Column("skill_name", sa.String(255), nullable=False),
        sa.Column("proficiency", sa.String(50)),
        sa.Column("years", sa.Float),
    )
    op.create_index("ix_candidate_skills_candidate_id", "candidate_skills", ["candidate_id"])
    op.create_index("ix_candidate_skills_skill_name", "candidate_skills", ["skill_name"])

    # candidate_experience
    op.create_table(
        "candidate_experience",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE")),
        sa.Column("company", sa.String(255)),
        sa.Column("title", sa.String(255)),
        sa.Column("start_date", sa.String(20)),
        sa.Column("end_date", sa.String(20)),
        sa.Column("is_current", sa.Boolean, server_default="false"),
        sa.Column("description", sa.Text),
        sa.Column("duration_months", sa.Integer),
    )
    op.create_index("ix_candidate_experience_candidate_id", "candidate_experience", ["candidate_id"])

    # candidate_education
    op.create_table(
        "candidate_education",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE")),
        sa.Column("institution", sa.String(255)),
        sa.Column("degree", sa.String(255)),
        sa.Column("field", sa.String(255)),
        sa.Column("graduation_year", sa.Integer),
        sa.Column("gpa", sa.Float),
    )

    # candidate_scores
    op.create_table(
        "candidate_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE")),
        sa.Column("overall_score", sa.Float, nullable=False),
        sa.Column("skill_score", sa.Float),
        sa.Column("experience_score", sa.Float),
        sa.Column("domain_score", sa.Float),
        sa.Column("education_score", sa.Float),
        sa.Column("certification_score", sa.Float),
        sa.Column("ai_confidence", sa.Float),
        sa.Column("ai_summary", sa.Text),
        sa.Column("skill_gaps", postgresql.JSONB, server_default="[]"),
        sa.Column("score_justification", sa.Text),
        sa.Column("recommendation", sa.String(100)),
        sa.Column("model_version", sa.String(100)),
        sa.Column("scored_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint("candidate_id", "job_id", name="uq_candidate_job_score"),
    )
    op.create_index("ix_candidate_scores_job_id", "candidate_scores", ["job_id"])
    op.create_index("ix_candidate_scores_overall", "candidate_scores", ["overall_score"])

    # interview_questions
    op.create_table(
        "interview_questions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("candidate_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("candidates.id", ondelete="CASCADE")),
        sa.Column("job_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("jobs.id", ondelete="CASCADE")),
        sa.Column("question_type", sa.String(50), nullable=False),
        sa.Column("question_text", sa.Text, nullable=False),
        sa.Column("rationale", sa.Text),
        sa.Column("difficulty", sa.String(20)),
        sa.Column("generated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # chat_sessions
    op.create_table(
        "chat_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )

    # chat_messages
    op.create_table(
        "chat_messages",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("session_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("chat_sessions.id", ondelete="CASCADE")),
        sa.Column("role", sa.String(20), nullable=False),
        sa.Column("content", sa.Text, nullable=False),
        sa.Column("metadata", postgresql.JSONB),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])

    # audit_logs
    op.create_table(
        "audit_logs",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id")),
        sa.Column("action", sa.String(255), nullable=False),
        sa.Column("entity_type", sa.String(100)),
        sa.Column("entity_id", postgresql.UUID(as_uuid=True)),
        sa.Column("metadata", postgresql.JSONB),
        sa.Column("ip_address", sa.String(50)),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("chat_messages")
    op.drop_table("chat_sessions")
    op.drop_table("interview_questions")
    op.drop_table("candidate_scores")
    op.drop_table("candidate_education")
    op.drop_table("candidate_experience")
    op.drop_table("candidate_skills")
    op.drop_table("candidates")
    op.drop_table("jobs")
    op.drop_table("users")
