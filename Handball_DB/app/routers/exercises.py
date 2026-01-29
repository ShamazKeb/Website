from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from typing import List, Set

from app import models, schemas
from app.database import get_db
from app.security import get_current_admin, get_current_coach_or_admin, get_current_coach, get_current_user
from app.crud.activity_logs import create_activity_log
from app.schemas import ActivityLogCreate
from app.models import ActionType


router = APIRouter(prefix="/exercises", tags=["exercises"])


# Dependency to get an exercise by ID
async def get_exercise_by_id(exercise_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(models.Exercise)
        .options(
            selectinload(models.Exercise.category_links),
            selectinload(models.Exercise.measurement_type_links)
        )
        .filter(models.Exercise.id == exercise_id, models.Exercise.is_active == True)
    )
    exercise = result.scalars().first()
    if not exercise:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Exercise not found")
    return exercise


@router.get("/categories", response_model=List[str])
async def get_all_categories():
    """
    List all available exercise categories.
    """
    return [category.value for category in models.Category]


@router.get("/measurement-types", response_model=List[str])
async def get_all_measurement_types():
    """
    List all available measurement types.
    """
    return [mt.value for mt in models.MeasurementType]


@router.post("/", response_model=schemas.Exercise, status_code=status.HTTP_201_CREATED)
async def create_exercise(
    exercise: schemas.ExerciseCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Create a new exercise (Coach or Admin).
    """
    if current_user.role == models.Role.coach:
        owner_coach_id = current_user.coach.id
    elif current_user.role == models.Role.admin:
        # Fallback for Admin
        if current_user.coach:
            owner_coach_id = current_user.coach.id
        else:
            result = await db.execute(select(models.Coach).limit(1))
            first_coach = result.scalars().first()
            
            if first_coach:
                owner_coach_id = first_coach.id
            else:
                 raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="No coaches found in the system. Create a coach first before creating exercises as Admin."
                )
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only coaches and admins can create exercises.")

    if not exercise.measurement_types:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="An exercise must have at least one measurement type.")

    db_exercise = models.Exercise(
        owner_coach_id=owner_coach_id,
        name=exercise.name,
        description=exercise.description,
    )
    db.add(db_exercise)
    await db.flush()

    for category_enum in exercise.categories:
        db.add(models.ExerciseCategoryLink(exercise_id=db_exercise.id, category=category_enum))

    for mt_create in exercise.measurement_types:
        db.add(models.MeasurementTypeLink(
            exercise_id=db_exercise.id,
            measurement_type=mt_create.measurement_type,
            is_required=mt_create.is_required
        ))

    await db.commit()
    await db.refresh(db_exercise)
    db_exercise = await get_exercise_by_id(db_exercise.id, db)
    return db_exercise


@router.get("/", response_model=List[schemas.Exercise])
async def read_exercises(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user), # Allow any authenticated user
):
    """
    Retrieve all active exercises.
    """
    result = await db.execute(
        select(models.Exercise)
        .options(
            selectinload(models.Exercise.category_links),
            selectinload(models.Exercise.measurement_type_links)
        )
        .filter(models.Exercise.is_active == True)
    )
    exercises = result.scalars().all()
    return exercises


@router.get("/{exercise_id}", response_model=schemas.Exercise)
async def read_exercise(
    exercise: models.Exercise = Depends(get_exercise_by_id),
    current_user: models.User = Depends(models.User), # Placeholder
):
    """
    Retrieve specific exercise details.
    """
    return exercise


@router.put("/{exercise_id}", response_model=schemas.Exercise)
async def update_exercise(
    exercise_update: schemas.ExerciseUpdate,
    exercise: models.Exercise = Depends(get_exercise_by_id),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Update exercise name, description, categories, and active status (Owner Coach or Admin).
    Cannot remove measurement types that have data (handled at a lower level or through a separate endpoint).
    """
    if current_user.role == models.Role.coach and exercise.owner_coach_id != current_user.coach.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own exercises.")

    # Determine action type and description for logging
    action_type = ActionType.coach_edit_exercise if current_user.role == models.Role.coach else ActionType.admin_action
    
    old_exercise_name = exercise.name # Capture old name for description

    if exercise_update.name:
        exercise.name = exercise_update.name
    if exercise_update.description:
        exercise.description = exercise_update.description
    if exercise_update.is_active is not None:
        exercise.is_active = exercise_update.is_active

    if exercise_update.categories is not None:
        # Clear existing categories and add new ones
        await db.execute(models.ExerciseCategoryLink.__table__.delete().where(
            models.ExerciseCategoryLink.exercise_id == exercise.id
        ))
        for category_enum in exercise_update.categories:
            db.add(models.ExerciseCategoryLink(exercise_id=exercise.id, category=category_enum))

    await db.commit()
    await db.refresh(exercise)
    
    # Reload exercise to get updated relationships for response
    updated_exercise = await get_exercise_by_id(exercise.id, db)

    description = ""
    if current_user.role == models.Role.coach:
        description = f"Coach {current_user.coach.first_name} {current_user.coach.last_name} updated exercise '{old_exercise_name}' to '{updated_exercise.name}'."
    elif current_user.role == models.Role.admin:
        description = f"Admin {current_user.email} updated exercise '{old_exercise_name}' to '{updated_exercise.name}'."

    await create_activity_log(
        db=db,
        log=ActivityLogCreate(
            action_type=action_type,
            user_id=current_user.id,
            target_exercise_id=updated_exercise.id,
            description=description,
        ),
    )

    return updated_exercise


@router.delete("/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_exercise(
    exercise: models.Exercise = Depends(get_exercise_by_id),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Soft delete (archive) an exercise (Owner Coach or Admin).
    Sets is_active to False.
    """
    if current_user.role == models.Role.coach and exercise.owner_coach_id != current_user.coach.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own exercises.")

    exercise.is_active = False
    db.add(exercise)
    await db.commit()
    return


@router.post("/{exercise_id}/measurements", response_model=schemas.Exercise, status_code=status.HTTP_200_OK)
async def add_measurement_type_to_exercise(
    exercise_id: int,
    measurement_type_create: schemas.ExerciseMeasurementTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Add a measurement type to an exercise (Owner Coach or Admin).
    """
    exercise = await get_exercise_by_id(exercise_id, db)

    if current_user.role == models.Role.coach and exercise.owner_coach_id != current_user.coach.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only modify your own exercises.")

    # Check if measurement type already exists
    existing_link = await db.execute(
        select(models.MeasurementTypeLink).filter(
            models.MeasurementTypeLink.exercise_id == exercise_id,
            models.MeasurementTypeLink.measurement_type == measurement_type_create.measurement_type
        )
    )
    if existing_link.scalars().first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Measurement type already exists for this exercise.")

    db.add(models.MeasurementTypeLink(
        exercise_id=exercise_id,
        measurement_type=measurement_type_create.measurement_type,
        is_required=measurement_type_create.is_required
    ))
    await db.commit()
    await db.refresh(exercise)
    exercise = await get_exercise_by_id(exercise.id, db)
    return exercise


@router.delete("/{exercise_id}/measurements/{measurement_type}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_measurement_type_from_exercise(
    exercise_id: int,
    measurement_type: models.MeasurementType,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_coach_or_admin),
):
    """
    Remove a measurement type from an exercise (Owner Coach or Admin).
    Only if no player measurements recorded with this type.
    """
    exercise = await get_exercise_by_id(exercise_id, db)

    if current_user.role == models.Role.coach and exercise.owner_coach_id != current_user.coach.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only modify your own exercises.")

    # Check if there are any player measurements recorded with this type
    # This check is not straightforward as player_measurements does not directly store measurement_type
    # It stores exercise_id. We need to infer if removing this measurement_type would invalidate existing player_measurements.
    # For now, we will allow removal, assuming application logic will prevent creation of player measurements
    # that would become invalid. A more robust solution would involve querying player_measurements
    # and checking if the values recorded align with this specific measurement_type.

    # Find the link to delete
    measurement_link_result = await db.execute(
        select(models.MeasurementTypeLink).filter(
            models.MeasurementTypeLink.exercise_id == exercise_id,
            models.MeasurementTypeLink.measurement_type == measurement_type
        )
    )
    measurement_link = measurement_link_result.scalars().first()

    if not measurement_link:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Measurement type not found for this exercise.")

    await db.delete(measurement_link)
    await db.commit()
    return



