from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # App
    environment: str = "development"
    log_level: str = "info"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_cors_origins: list[str] = Field(default=["http://localhost:3000"])

    # Database
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/hiring_copilot"
    )
    database_pool_size: int = 10
    database_max_overflow: int = 20

    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl_ai: int = 86400  # 24h for AI responses
    redis_cache_ttl_search: int = 120  # 2min for search results

    # JWT
    jwt_secret_key: str = Field(default="change-me-in-production")
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_days: int = 7

    # OpenAI
    openai_api_key: str = Field(default="")
    openai_llm_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-large"
    openai_embedding_dimensions: int = 3072

    # Anthropic (fallback)
    anthropic_api_key: str = Field(default="")
    anthropic_llm_model: str = "claude-3-5-sonnet-20241022"

    # Pinecone
    pinecone_api_key: str = Field(default="")
    pinecone_index_name: str = "ai-hiring-copilot"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # Namespaces
    pinecone_namespace_resumes: str = "resumes"
    pinecone_namespace_jobs: str = "jobs"

    # AWS
    aws_region: str = "us-east-1"
    aws_access_key_id: str = Field(default="")
    aws_secret_access_key: str = Field(default="")
    aws_s3_bucket_name: str = "ai-hiring-copilot-resumes"
    aws_sqs_queue_url: str = Field(default="")
    aws_sqs_dlq_url: str = Field(default="")

    # File upload
    max_upload_size_mb: int = 10
    allowed_mime_types: list[str] = ["application/pdf", "application/vnd.openxmlformats-officedocument.wordprocessingml.document"]

    # Scoring weights
    score_weight_skills: float = 0.35
    score_weight_experience: float = 0.30
    score_weight_domain: float = 0.20
    score_weight_education: float = 0.10
    score_weight_certifications: float = 0.05

    # Rate limiting
    rate_limit_ai_per_minute: int = 60
    rate_limit_upload_per_minute: int = 10
    rate_limit_search_per_minute: int = 30
    rate_limit_chat_per_minute: int = 20

    @field_validator("api_cors_origins", mode="before")
    @classmethod
    def parse_cors(cls, v: str | list[str]) -> list[str]:
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @property
    def is_development(self) -> bool:
        return self.environment == "development"

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_upload_size_mb * 1024 * 1024


@lru_cache
def get_settings() -> Settings:
    return Settings()
