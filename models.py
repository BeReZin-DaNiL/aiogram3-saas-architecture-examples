from datetime import datetime, date
from enum import Enum as PyEnum
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import BigInteger, Integer, String, Float, Text, ForeignKey, func, DateTime, Enum, Date, JSON, Boolean
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

class Base(DeclarativeBase):
    pass

class Gender(str, PyEnum):
    MALE = 'Мужской'
    FEMALE = 'Женский'

class Goal(str, PyEnum):
    LOSE = 'Похудение'
    MAINTAIN = 'Поддержание'
    GAIN = 'Набор массы'

class TransactionType(str, PyEnum):
    PAYMENT = 'payment'
    BONUS = 'bonus'
    SUBSCRIPTION_SPEND = 'subscription_spend'

class TransactionStatus(str, PyEnum):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    username: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    full_name: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    
    # Limits & Tariff
    tariff_id: Mapped[str] = mapped_column(String, default="free", server_default="free")
    photos_used_today: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    text_used_today: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    plan_gens_today: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_usage_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Billing & Referrals
    is_premium: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    subscription_end_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    bonus_balance: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    auto_renewal: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false")
    referrer_id: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)

    # Relationship
    profile: Mapped["UserProfile"] = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    food_logs: Mapped[list["FoodLog"]] = relationship("FoodLog", back_populates="user", cascade="all, delete-orphan")
    meal_plans: Mapped[list["MealPlan"]] = relationship("MealPlan", back_populates="user", cascade="all, delete-orphan")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")

    def __str__(self):
        return self.full_name or self.username or f"User {self.id}"

class UserProfile(Base):
    __tablename__ = 'user_profiles'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    age: Mapped[int] = mapped_column(Integer)
    gender: Mapped[Gender] = mapped_column(Enum(Gender, name='gender_enum', native_enum=False))
    weight: Mapped[float] = mapped_column(Float)
    height: Mapped[int] = mapped_column(Integer)
    activity_level: Mapped[float] = mapped_column(Float)
    goal: Mapped[Goal] = mapped_column(Enum(Goal, name='goal_enum', native_enum=False))
    daily_calories: Mapped[int] = mapped_column(Integer)
    allergies: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship
    user: Mapped["User"] = relationship("User", back_populates="profile")

    def __str__(self):
        try:
            return f"Анкета: {self.user.full_name}"
        except:
            return f"Анкета профиля {self.id}"

class FoodLog(Base):
    __tablename__ = 'food_logs'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    product_name: Mapped[str] = mapped_column(String)
    weight_g: Mapped[int] = mapped_column(Integer, default=100)
    calories: Mapped[int] = mapped_column(Integer)
    proteins: Mapped[float] = mapped_column(Float)
    fats: Mapped[float] = mapped_column(Float)
    carbs: Mapped[float] = mapped_column(Float)
    ingredients: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    meal_type: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    photo_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())


    user: Mapped["User"] = relationship("User", back_populates="food_logs")

    def __str__(self):
        return f"{self.product_name} ({self.calories} ккал)"

class MealPlan(Base):
    __tablename__ = 'meal_plans'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    date: Mapped[date] = mapped_column(Date, default=func.current_date())
    content: Mapped[dict] = mapped_column(JSON)
    total_calories: Mapped[int] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

    
    user: Mapped["User"] = relationship("User", back_populates="meal_plans")

    def __str__(self):
        return f"План на {self.date}"

class Transaction(Base):
    __tablename__ = 'transactions'

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('users.id'))
    amount: Mapped[int] = mapped_column(Integer)
    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType, name='transaction_type_enum', native_enum=False))
    status: Mapped[TransactionStatus] = mapped_column(Enum(TransactionStatus, name='transaction_status_enum', native_enum=False))
    provider_id: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    description: Mapped[str] = mapped_column(String)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now())

 
    user: Mapped["User"] = relationship("User", back_populates="transactions")

    def __str__(self):
        return f"Транзакция {self.id} ({self.amount} руб.)"
