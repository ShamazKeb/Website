import enum
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    ForeignKey,
    Enum,
    Table,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Role(enum.Enum):
    admin = "admin"
    coach = "coach"
    player = "player"


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(Enum(Role), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    player = relationship("Player", back_populates="user", uselist=False)
    coach = relationship("Coach", back_populates="user", uselist=False)


class Player(Base):
    __tablename__ = "players"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    birth_year = Column(Integer)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="player")
    teams = relationship("Team", secondary="team_players", back_populates="players")


class Coach(Base):
    __tablename__ = "coaches"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="coach")
    teams = relationship("Team", secondary="team_coaches", back_populates="coaches")
    exercises = relationship("Exercise", back_populates="owner_coach")


class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    season = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    players = relationship("Player", secondary="team_players", back_populates="teams")
    coaches = relationship("Coach", secondary="team_coaches", back_populates="teams")


team_players = Table(
    "team_players",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("player_id", Integer, ForeignKey("players.id"), primary_key=True),
)

team_coaches = Table(
    "team_coaches",
    Base.metadata,
    Column("team_id", Integer, ForeignKey("teams.id"), primary_key=True),
    Column("coach_id", Integer, ForeignKey("coaches.id"), primary_key=True),
)


class Category(enum.Enum):
    schnelligkeit = "schnelligkeit"
    maximalkraft = "maximalkraft"
    ausdauer = "ausdauer"
    koordination = "koordination"


class MeasurementType(enum.Enum):
    seconds = "seconds"
    repetitions = "repetitions"
    kilograms = "kilograms"
    meters = "meters"
    centimeters = "centimeters"


class Exercise(Base):
    __tablename__ = "exercises"
    id = Column(Integer, primary_key=True, index=True)
    owner_coach_id = Column(Integer, ForeignKey("coaches.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    owner_coach = relationship("Coach", back_populates="exercises")
    category_links = relationship("ExerciseCategoryLink", back_populates="exercise", cascade="all, delete-orphan")
    measurement_type_links = relationship("MeasurementTypeLink", back_populates="exercise", cascade="all, delete-orphan")

    @hybrid_property
    def categories(self):
        return {link.category for link in self.category_links}

    @hybrid_property
    def measurement_types(self):
        # This will be a list of ExerciseMeasurementTypeResponse compatible dicts
        return [
            {"measurement_type": link.measurement_type, "is_required": link.is_required}
            for link in self.measurement_type_links
        ]


class ExerciseCategoryLink(Base):
    __tablename__ = "exercise_categories"
    exercise_id = Column(Integer, ForeignKey("exercises.id"), primary_key=True)
    category = Column(Enum(Category), primary_key=True)

    exercise = relationship("Exercise", back_populates="category_links")


class MeasurementTypeLink(Base):
    __tablename__ = 'exercise_measurements'
    exercise_id = Column(Integer, ForeignKey('exercises.id'), primary_key=True)
    measurement_type = Column(Enum(MeasurementType), primary_key=True)
    is_required = Column(Boolean, default=True)
    exercise = relationship("Exercise", back_populates="measurement_type_links")


class PlayerMeasurement(Base):
    __tablename__ = "player_measurements"
    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"), nullable=False)
    exercise_id = Column(Integer, ForeignKey("exercises.id"), nullable=False)
    recorded_at = Column(DateTime(timezone=True), nullable=False)
    notes = Column(String)
    created_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    player = relationship("Player")
    exercise = relationship("Exercise")
    created_by_user = relationship("User")
    values = relationship("MeasurementValue", back_populates="player_measurement", cascade="all, delete-orphan")
    is_active = Column(Boolean, default=True)


class MeasurementValue(Base):
    __tablename__ = "measurement_values"
    id = Column(Integer, primary_key=True, index=True)
    player_measurement_id = Column(Integer, ForeignKey("player_measurements.id"), nullable=False)
    measurement_type = Column(Enum(MeasurementType), nullable=False)
    value = Column(String, nullable=False) # Store as string for flexibility

    player_measurement = relationship("PlayerMeasurement", back_populates="values")


class ActionType(enum.Enum):
    player_entry = "player_entry"
    coach_add_measurement = "coach_add_measurement"
    coach_edit_measurement = "coach_edit_measurement"
    coach_create_player = "coach_create_player"
    coach_deactivate_player = "coach_deactivate_player"
    coach_edit_exercise = "coach_edit_exercise"
    admin_action = "admin_action"


class ActivityLog(Base):
    __tablename__ = "activity_logs"
    id = Column(Integer, primary_key=True, index=True)
    action_type = Column(Enum(ActionType), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_player_id = Column(Integer, ForeignKey("players.id"))
    target_exercise_id = Column(Integer, ForeignKey("exercises.id"))
    target_team_id = Column(Integer, ForeignKey("teams.id"))
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User")
    target_player = relationship("Player")
    target_exercise = relationship("Exercise")
    target_team = relationship("Team")
