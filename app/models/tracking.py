import uuid
from datetime import datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserPreference(Base):
    __tablename__ = "user_preferences"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True, nullable=False)
    birthday: Mapped[str | None] = mapped_column(Date, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(10), nullable=True)
    height: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    weight: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    goal_weight: Mapped[float | None] = mapped_column(Numeric(5, 1), nullable=True)
    diet_type: Mapped[str | None] = mapped_column(String(30), nullable=True)
    allergens: Mapped[dict] = mapped_column(JSONB, server_default="'[]'::jsonb")
    dislikes: Mapped[dict] = mapped_column(JSONB, server_default="'[]'::jsonb")
    target_calories: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_protein_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_carbs_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    target_fat_g: Mapped[int | None] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class MealLog(Base):
    __tablename__ = "meal_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    date: Mapped[str] = mapped_column(Date, nullable=False)
    meal_type: Mapped[str] = mapped_column(String(20), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Favorite(Base):
    __tablename__ = "favorites"
    __table_args__ = (
        UniqueConstraint("user_id", "combo_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    combo_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False)
    food_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("foods.id"), nullable=True)
    recommendation_snapshot: Mapped[dict] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class MealLogItem(Base):
    __tablename__ = "meal_log_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    meal_log_id: Mapped[int] = mapped_column(Integer, ForeignKey("meal_logs.id"), nullable=False)
    food_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("foods.id"), nullable=True)
    food_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[float] = mapped_column(Numeric(5, 2), server_default="1")
    calories: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_protein: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_carbs: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_fat: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    source: Mapped[str] = mapped_column(String(20), nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
