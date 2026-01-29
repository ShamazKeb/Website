from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from app.models import User, Player, Coach, Team, Exercise, PlayerMeasurement, MeasurementValue, Role, MeasurementType, ExerciseCategoryLink, MeasurementTypeLink
from app.security import hash_password


async def create_test_data(db: AsyncSession):


    # Create users


    user_admin = User(email="admin@test.com", password_hash=hash_password("adminpass"), role=Role.admin)


    user_coach_1 = User(email="coach1@test.com", password_hash=hash_password("coachpass1"), role=Role.coach)


    user_coach_2 = User(email="coach2@test.com", password_hash=hash_password("coachpass2"), role=Role.coach)


    user_player_1 = User(email="player1@test.com", password_hash=hash_password("playerpass1"), role=Role.player)


    user_player_2 = User(email="player2@test.com", password_hash=hash_password("playerpass2"), role=Role.player)





    # Create players


    player_1 = Player(user=user_player_1, first_name="Player", last_name="One", birth_year=2000)


    player_2 = Player(user=user_player_2, first_name="Player", last_name="Two", birth_year=2001)





    # Create coaches


    coach_1 = Coach(user=user_coach_1, first_name="Coach", last_name="One")


    coach_2 = Coach(user=user_coach_2, first_name="Coach", last_name="Two")





    # Create teams and associate players/coaches


    team_1 = Team(name="Team 1", season="2023/2024", players=[player_1], coaches=[coach_1])


    team_2 = Team(name="Team 2", season="2023/2024", players=[player_2], coaches=[coach_2])





    # Create exercises


    exercise_1 = Exercise(owner_coach=coach_1, name="Sprint", description="30m Sprint")


    exercise_2 = Exercise(owner_coach=coach_2, name="Jump", description="Standing Jump")


    


    # Add categories and measurement types to exercises


    exercise_1.category_links.append(ExerciseCategoryLink(category="schnelligkeit"))


    exercise_1.measurement_type_links.append(MeasurementTypeLink(measurement_type=MeasurementType.seconds, is_required=True))


    exercise_2.category_links.append(ExerciseCategoryLink(category="maximalkraft"))


    exercise_2.measurement_type_links.append(MeasurementTypeLink(measurement_type=MeasurementType.centimeters, is_required=True))





    # Create measurements


    measurement_1 = PlayerMeasurement(player=player_1, exercise=exercise_1, recorded_at=datetime.utcnow(), created_by_user=user_player_1)


    measurement_2 = PlayerMeasurement(player=player_1, exercise=exercise_1, recorded_at=datetime.utcnow(), created_by_user=user_player_1)





    # Create measurement values


    value_1 = MeasurementValue(player_measurement=measurement_1, measurement_type=MeasurementType.seconds, value="4.5")


    value_2 = MeasurementValue(player_measurement=measurement_2, measurement_type=MeasurementType.seconds, value="4.4")





    db.add_all([


        user_admin,


        team_1,


        team_2,


        value_1,


        value_2,


    ])


    await db.commit()
