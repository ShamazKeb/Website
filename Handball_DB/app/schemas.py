from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional, Set, Dict
from datetime import datetime
from app.models import Role, Category, MeasurementType

from .models import Player, Coach # Import Player and Coach models directly


class UserBase(BaseModel):
    email: str
    role: Role


class UserCreate(UserBase):
    password: str


class User(UserBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(UserBase):
    email: Optional[str] = None
    role: Optional[Role] = None
    password: Optional[str] = None # Admin can reset passwords

class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(UserBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    birth_year: Optional[int] = None


class PlayerCreate(PlayerBase):
    pass


class Player(PlayerBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CoachBase(BaseModel):
    first_name: str
    last_name: str


class CoachCreate(CoachBase):
    pass


class Coach(CoachBase):
    id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamBase(BaseModel):
    name: str
    season: str


class TeamCreate(TeamBase):
    pass


class TeamUpdate(TeamBase):
    name: Optional[str] = None
    season: Optional[str] = None


class Team(TeamBase):
    id: int
    created_at: datetime
    is_active: bool = True
    players: List["Player"] = []
    coaches: List["Coach"] = []
    model_config = ConfigDict(from_attributes=True)


class TeamPlayerAssignment(BaseModel):
    player_id: int


class TeamCoachAssignment(BaseModel):
    coach_id: int


# --- Exercise Management Schemas ---

class ExerciseMeasurementTypeCreate(BaseModel):
    measurement_type: MeasurementType
    is_required: bool = True

class ExerciseBase(BaseModel):
    name: str
    description: Optional[str] = None
    categories: Optional[Set[Category]] = Field(default_factory=set)
    measurement_types: Optional[List[ExerciseMeasurementTypeCreate]] = Field(default_factory=list)


class ExerciseCreate(ExerciseBase):
    pass


class ExerciseUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    categories: Optional[Set[Category]] = None
    is_active: Optional[bool] = None # For soft delete


class ExerciseMeasurementTypeResponse(BaseModel):
    measurement_type: MeasurementType
    is_required: bool

    model_config = ConfigDict(from_attributes=True)

class Exercise(ExerciseBase):
    id: int
    owner_coach_id: int
    is_active: bool
    created_at: datetime
    categories: Set[Category] = Field(default_factory=set) # Override to ensure it's loaded
    measurement_types: List[ExerciseMeasurementTypeResponse] = Field(default_factory=list) # Override to ensure it's loaded


    model_config = ConfigDict(from_attributes=True)

# Schemas for listing available enums
class CategoryResponse(BaseModel):
    name: Category
    description: str


class MeasurementTypeResponse(BaseModel):
    name: MeasurementType
    description: str

# --- Player Measurement Schemas ---

class MeasurementValueSchema(BaseModel):
    measurement_type: MeasurementType
    value: str

    model_config = ConfigDict(from_attributes=True)


class PlayerMeasurementCreate(BaseModel):
    player_id: int
    exercise_id: int
    recorded_at: datetime = Field(default_factory=datetime.now)
    notes: Optional[str] = None
    values: List[MeasurementValueSchema] = Field(default_factory=list)


class PlayerMeasurementUpdate(BaseModel):
    recorded_at: Optional[datetime] = None
    notes: Optional[str] = None
    values: Optional[List[MeasurementValueSchema]] = None


class PlayerMeasurementResponse(BaseModel):
    id: int
    player_id: int
    exercise_id: int
    recorded_at: datetime
    notes: Optional[str] = None
    created_by_user_id: int
    values: List[MeasurementValueSchema] = Field(default_factory=list)

    model_config = ConfigDict(from_attributes=True)


# --- Statistics Schemas ---

class MeasurementStatsResponse(BaseModel):
    average: Optional[float] = None
    best: Optional[float] = None
    trend: Optional[str] = None  # e.g., "improving", "worsening", "stable"
    count: int

class LeaderboardEntryResponse(BaseModel):
    player_id: int
    best_value: float
    recorded_at: datetime

class ExerciseStatsResponse(BaseModel):
    exercise_name: str
    measurement_type_stats: Dict[str, MeasurementStatsResponse] = Field(default_factory=dict)


class PlayerStatsAcrossExercisesResponse(BaseModel):
    player_id: int
    stats_by_exercise: Dict[int, ExerciseStatsResponse] = Field(default_factory=dict)


# --- Activity Log Schemas ---
from app.models import ActionType # Import the ActionType enum

class ActivityLogBase(BaseModel):
    action_type: ActionType
    user_id: int
    target_player_id: Optional[int] = None
    target_exercise_id: Optional[int] = None
    target_team_id: Optional[int] = None
    description: Optional[str] = None


class ActivityLogCreate(ActivityLogBase):
    pass


class ActivityLogResponse(ActivityLogBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
