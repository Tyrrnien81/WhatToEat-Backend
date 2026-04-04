from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_restaurant_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)


class MealType(Base):
    __tablename__ = "meal_types"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_meal_type_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(50), nullable=False)


class Food(Base):
    __tablename__ = "foods"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_food_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    food_category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    ingredients: Mapped[str | None] = mapped_column(Text, nullable=True)
    serving_size_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)
    serving_size_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)


class FoodNutrition(Base):
    __tablename__ = "food_nutrition"

    food_id: Mapped[int] = mapped_column(Integer, ForeignKey("foods.id"), primary_key=True)
    calories: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_fat: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_saturated_fat: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_trans_fat: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mg_cholesterol: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_carbs: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_added_sugar: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_sugar: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mg_potassium: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mg_sodium: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_fiber: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    g_protein: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mg_iron: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mg_calcium: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mg_vitamin_c: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    iu_vitamin_a: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    re_vitamin_a: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mcg_vitamin_a: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mg_vitamin_d: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    mcg_vitamin_d: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)


class FoodIcon(Base):
    __tablename__ = "food_icons"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    external_icon_id: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False)
    icon_type: Mapped[int] = mapped_column(Integer, nullable=False)
    behavior: Mapped[int] = mapped_column(Integer, nullable=False)
    is_filter: Mapped[bool] = mapped_column(Boolean, nullable=False)
    is_highlight: Mapped[bool] = mapped_column(Boolean, nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False)


class FoodIconAssignment(Base):
    __tablename__ = "food_icon_assignments"

    food_id: Mapped[int] = mapped_column(Integer, ForeignKey("foods.id"), primary_key=True)
    icon_id: Mapped[int] = mapped_column(Integer, ForeignKey("food_icons.id"), primary_key=True)


class MenuSnapshot(Base):
    __tablename__ = "menu_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    restaurant_id: Mapped[int] = mapped_column(Integer, ForeignKey("restaurants.id"), nullable=False)
    meal_type_id: Mapped[int] = mapped_column(Integer, ForeignKey("meal_types.id"), nullable=False)
    service_date: Mapped[str] = mapped_column(Date, nullable=False)
    exported_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)


class MenuSection(Base):
    __tablename__ = "menu_sections"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    snapshot_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu_snapshots.id"), nullable=False)
    external_menu_id: Mapped[int] = mapped_column(Integer, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)


class MenuSectionItem(Base):
    __tablename__ = "menu_section_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    section_id: Mapped[int] = mapped_column(Integer, ForeignKey("menu_sections.id"), nullable=False)
    food_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("foods.id"), nullable=True)
    external_menu_item_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    food_variation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    station_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)
    price: Mapped[float | None] = mapped_column(Numeric(10, 2), nullable=True)
    serving_size_amount: Mapped[str | None] = mapped_column(String(20), nullable=True)
    serving_size_unit: Mapped[str | None] = mapped_column(String(50), nullable=True)
