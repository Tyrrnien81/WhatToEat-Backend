from sqlalchemy import Column, Integer, String, Numeric, Date, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy import TIMESTAMP

from app.database import Base


class MealLog(Base):
    __tablename__ = "meal_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    date = Column(Date, nullable=False)
    meal_type = Column(String, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class MealLogItem(Base):
    __tablename__ = "meal_log_items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    meal_log_id = Column(Integer, ForeignKey("meal_logs.id"), nullable=False)
    food_id = Column(Integer, ForeignKey("foods.id"), nullable=True)
    food_name = Column(String, nullable=False)
    quantity = Column(Numeric, default=1)
    calories = Column(Numeric, nullable=True)
    g_protein = Column(Numeric, nullable=True)
    g_carbs = Column(Numeric, nullable=True)
    g_fat = Column(Numeric, nullable=True)
    source = Column(String, nullable=False)
    logged_at = Column(TIMESTAMP(timezone=True), server_default=func.now())