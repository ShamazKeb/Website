"""Seed script to create sample data for the Handball-Tracker app."""
import asyncio
from sqlalchemy import select
from app.database import AsyncSessionLocal, engine, Base
from app.models import (
    User, Player, Coach, Team, Exercise, PlayerMeasurement, MeasurementValue,
    Role, Category, MeasurementType, ExerciseCategoryLink, MeasurementTypeLink
)
from app.security import hash_password
from datetime import datetime, timedelta
import random

async def seed_database():
    async with AsyncSessionLocal() as db:
        print("🌱 Seeding database with sample data...")
        
        # Check if data already exists
        result = await db.execute(select(User).limit(1))
        if result.scalars().first():
            print("⚠️ Database already has data. Skipping seed.")
            return
        
        # 1. Create Users
        print("Creating users...")
        admin_user = User(email="admin@handball.de", password_hash=hash_password("admin123"), role=Role.admin)
        coach1_user = User(email="trainer.mueller@handball.de", password_hash=hash_password("coach123"), role=Role.coach)
        coach2_user = User(email="trainer.schmidt@handball.de", password_hash=hash_password("coach123"), role=Role.coach)
        
        player_users = []
        player_names = [
            ("Max", "Mustermann"), ("Tim", "Fischer"), ("Leon", "Weber"), 
            ("Paul", "Becker"), ("Felix", "Hoffmann"), ("Jonas", "Schulz"),
            ("Lukas", "Koch"), ("Ben", "Richter"), ("Finn", "Wolf"), ("Noah", "Schäfer"),
            ("Emma", "Klein"), ("Mia", "Wagner")
        ]
        
        for i, (first, last) in enumerate(player_names):
            user = User(
                email=f"{first.lower()}.{last.lower()}@handball.de", 
                password_hash=hash_password("player123"), 
                role=Role.player
            )
            player_users.append((user, first, last))
        
        db.add(admin_user)
        db.add(coach1_user)
        db.add(coach2_user)
        for user, _, _ in player_users:
            db.add(user)
        await db.commit()
        
        # Refresh to get IDs
        await db.refresh(admin_user)
        await db.refresh(coach1_user)
        await db.refresh(coach2_user)
        for user, _, _ in player_users:
            await db.refresh(user)
        
        # 2. Create Coaches
        print("Creating coaches...")
        coach1 = Coach(user_id=coach1_user.id, first_name="Thomas", last_name="Müller")
        coach2 = Coach(user_id=coach2_user.id, first_name="Hans", last_name="Schmidt")
        db.add(coach1)
        db.add(coach2)
        await db.commit()
        await db.refresh(coach1)
        await db.refresh(coach2)
        
        # 3. Create Players
        print("Creating players...")
        players = []
        birth_years = [2010, 2011, 2012, 2013]
        for user, first, last in player_users:
            player = Player(
                user_id=user.id, 
                first_name=first, 
                last_name=last,
                birth_year=random.choice(birth_years)
            )
            db.add(player)
            players.append(player)
        await db.commit()
        for p in players:
            await db.refresh(p)
        
        # 4. Create Teams
        print("Creating teams...")
        team_a = Team(name="Jugend A", season="2025/2026", is_active=True)
        team_b = Team(name="Jugend B", season="2025/2026", is_active=True)
        team_c = Team(name="Jugend C", season="2025/2026", is_active=True)
        db.add(team_a)
        db.add(team_b)
        db.add(team_c)
        await db.commit()
        await db.refresh(team_a)
        await db.refresh(team_b)
        await db.refresh(team_c)
        
        # Assign players to teams using the association table
        for p in players[:4]:
            team_a.players.append(p)
        for p in players[4:8]:
            team_b.players.append(p)
        for p in players[8:]:
            team_c.players.append(p)
        
        # Assign coaches to teams
        team_a.coaches.append(coach1)
        team_b.coaches.append(coach1)
        team_b.coaches.append(coach2)
        team_c.coaches.append(coach2)
        await db.commit()
        
        # 5. Create Exercises with category and measurement type links
        print("Creating exercises...")
        
        # Exercise 1: 30m Sprint
        ex1 = Exercise(name="30m Sprint", description="30 Meter Sprinttest auf Zeit", owner_coach_id=coach1.id, is_active=True)
        db.add(ex1)
        await db.commit()
        await db.refresh(ex1)
        db.add(ExerciseCategoryLink(exercise_id=ex1.id, category=Category.schnelligkeit))
        db.add(MeasurementTypeLink(exercise_id=ex1.id, measurement_type=MeasurementType.seconds, is_required=True))
        
        # Exercise 2: Standweitsprung
        ex2 = Exercise(name="Standweitsprung", description="Weitsprung aus dem Stand", owner_coach_id=coach1.id, is_active=True)
        db.add(ex2)
        await db.commit()
        await db.refresh(ex2)
        db.add(ExerciseCategoryLink(exercise_id=ex2.id, category=Category.maximalkraft))
        db.add(MeasurementTypeLink(exercise_id=ex2.id, measurement_type=MeasurementType.centimeters, is_required=True))
        
        # Exercise 3: Cooper Test
        ex3 = Exercise(name="Cooper Test", description="12-Minuten-Lauf zur Ausdauermessung", owner_coach_id=coach2.id, is_active=True)
        db.add(ex3)
        await db.commit()
        await db.refresh(ex3)
        db.add(ExerciseCategoryLink(exercise_id=ex3.id, category=Category.ausdauer))
        db.add(MeasurementTypeLink(exercise_id=ex3.id, measurement_type=MeasurementType.meters, is_required=True))
        
        # Exercise 4: Liegestütze
        ex4 = Exercise(name="Liegestütze", description="Maximale Anzahl Liegestütze in 60 Sekunden", owner_coach_id=coach1.id, is_active=True)
        db.add(ex4)
        await db.commit()
        await db.refresh(ex4)
        db.add(ExerciseCategoryLink(exercise_id=ex4.id, category=Category.maximalkraft))
        db.add(MeasurementTypeLink(exercise_id=ex4.id, measurement_type=MeasurementType.repetitions, is_required=True))
        
        # Exercise 5: Ballprellen
        ex5 = Exercise(name="Ballprellen", description="Ball mit beiden Händen abwechselnd prellen", owner_coach_id=coach2.id, is_active=True)
        db.add(ex5)
        await db.commit()
        await db.refresh(ex5)
        db.add(ExerciseCategoryLink(exercise_id=ex5.id, category=Category.koordination))
        db.add(MeasurementTypeLink(exercise_id=ex5.id, measurement_type=MeasurementType.repetitions, is_required=True))
        
        await db.commit()
        
        exercises = [ex1, ex2, ex3, ex4, ex5]
        exercise_config = {
            ex1.id: (MeasurementType.seconds, lambda: round(random.uniform(4.5, 6.5), 2)),
            ex2.id: (MeasurementType.centimeters, lambda: random.randint(150, 250)),
            ex3.id: (MeasurementType.meters, lambda: random.randint(1800, 3000)),
            ex4.id: (MeasurementType.repetitions, lambda: random.randint(15, 45)),
            ex5.id: (MeasurementType.repetitions, lambda: random.randint(20, 50)),
        }
        
        # 6. Create Measurements
        print("Creating measurements...")
        measurement_count = 0
        for player in players:
            for exercise in exercises:
                num_measurements = random.randint(3, 5)
                for i in range(num_measurements):
                    days_ago = random.randint(1, 90)
                    recorded_at = datetime.now() - timedelta(days=days_ago)
                    
                    measurement = PlayerMeasurement(
                        player_id=player.id,
                        exercise_id=exercise.id,
                        recorded_at=recorded_at,
                        notes=None,
                        created_by_user_id=coach1_user.id
                    )
                    db.add(measurement)
                    await db.commit()
                    await db.refresh(measurement)
                    
                    # Add the measurement value
                    mtype, value_fn = exercise_config[exercise.id]
                    value = MeasurementValue(
                        player_measurement_id=measurement.id,
                        measurement_type=mtype,
                        value=str(value_fn())
                    )
                    db.add(value)
                    measurement_count += 1
        
        await db.commit()
        
        print(f"""
✅ Sample data created successfully!

📊 Summary:
- 1 Admin user
- 2 Coaches  
- {len(players)} Players
- 3 Teams
- {len(exercises)} Exercises
- {measurement_count} Measurements

🔐 Login credentials:
- Admin: admin@handball.de / admin123
- Coach 1: trainer.mueller@handball.de / coach123
- Coach 2: trainer.schmidt@handball.de / coach123
- Players: <firstname>.<lastname>@handball.de / player123
  (e.g., max.mustermann@handball.de)
""")

if __name__ == "__main__":
    asyncio.run(seed_database())
