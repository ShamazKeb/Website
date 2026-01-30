import sys
import os
import asyncio
import random
from datetime import datetime, timedelta

# Add the parent directory to sys.path to allow importing app
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from app.database import AsyncSessionLocal
from app import models, schemas

from app.crud import teams as crud_teams
from app.crud import players as crud_players
from app.crud import measurements as crud_measurements
from app.security import hash_password
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

async def populate():
    async with AsyncSessionLocal() as db:
        print("Starting database population...")

        # 0. Cleanup (Optional but requested "reset")
        print("Cleaning up old data...")
        # Order matters due to FKs
        await db.execute(models.ActivityLog.__table__.delete())
        await db.execute(models.MeasurementValue.__table__.delete())
        await db.execute(models.PlayerMeasurement.__table__.delete())
        await db.execute(models.ExerciseCategoryLink.__table__.delete())
        await db.execute(models.MeasurementTypeLink.__table__.delete())
        # Many-to-Many tables
        await db.execute(models.team_players.delete())
        await db.execute(models.team_coaches.delete())
        
        await db.execute(models.Exercise.__table__.delete())
        await db.execute(models.Player.__table__.delete())
        await db.execute(models.Team.__table__.delete())
        await db.commit()
        print("Cleanup complete.")

        # 1. Get or Create Admin/Coach
        print("Checking for admin user...")
        result = await db.execute(
            select(models.User)
            .options(selectinload(models.User.coach))
            .filter(models.User.email == "admin@handball.de")
        )
        admin_user = result.scalars().first()
        
        if not admin_user:
            print("Admin user (admin@handball.de) not found. Creating default admin...")
            hashed_pwd = hash_password("admin123")
            admin_user = models.User(email="admin@handball.de", password_hash=hashed_pwd, role=models.Role.admin)
            db.add(admin_user)
            await db.commit()
            # Re-fetch with coach options
            result = await db.execute(
                select(models.User)
                .options(selectinload(models.User.coach))
                .filter(models.User.email == "admin@handball.de")
            )
            admin_user = result.scalars().first()
        
        # Ensure admin has a coach profile if they are admin
        owner_id = admin_user.id
        owner_coach_id = None
        if admin_user.coach:
            owner_coach_id = admin_user.coach.id
        elif admin_user.role == models.Role.admin:
            # check if there is any coach
            res = await db.execute(select(models.Coach).limit(1))
            c = res.scalars().first()
            if c:
                owner_coach_id = c.id
            else:
                 # Create a dummy coach for admin
                 print("Creating dummy coach profile for admin...")
                 new_coach = models.Coach(user_id=admin_user.id, first_name="Admin", last_name="Coach")
                 db.add(new_coach)
                 await db.commit()
                 await db.refresh(new_coach)
                 await db.refresh(admin_user)
                 owner_coach_id = new_coach.id

        print(f"Using Owner Coach ID: {owner_coach_id}")

        # 2. Create Standard Exercises
        exercises_data = [
            {
                "name": "Bench Press",
                "description": "Barbell bench press for maximum strength.",
                "categories": [models.Category.maximalkraft],
                "measurement_types": [
                    {"measurement_type": models.MeasurementType.kilograms, "is_required": True},
                    {"measurement_type": models.MeasurementType.repetitions, "is_required": False}
                ]
            },
            {
                "name": "Back Squat",
                "description": "Barbell back squat for lower body strength.",
                "categories": [models.Category.maximalkraft],
                "measurement_types": [
                    {"measurement_type": models.MeasurementType.kilograms, "is_required": True}
                ]
            },
            {
                "name": "40m Sprint",
                "description": "Maximum speed test.",
                "categories": [models.Category.schnelligkeit],
                "measurement_types": [
                    {"measurement_type": models.MeasurementType.seconds, "is_required": True}
                ]
            },
            {
                "name": "Cooper Test",
                "description": "12-minute run for endurance.",
                "categories": [models.Category.ausdauer],
                "measurement_types": [
                    {"measurement_type": models.MeasurementType.meters, "is_required": True}
                ]
            },
             {
                "name": "Agility T-Test",
                "description": "Agility and coordination test.",
                "categories": [models.Category.koordination, models.Category.schnelligkeit],
                "measurement_types": [
                    {"measurement_type": models.MeasurementType.seconds, "is_required": True}
                ]
            }
        ]

        created_exercises = []
        for ex_data in exercises_data:
            # Check if exists
            res = await db.execute(select(models.Exercise).filter(models.Exercise.name == ex_data["name"]))
            existing = res.scalars().first()
            if not existing:
                print(f"Creating exercise: {ex_data['name']}")
                
                # Create Exercise
                db_ex = models.Exercise(
                    owner_coach_id=owner_coach_id,
                    name=ex_data["name"],
                    description=ex_data["description"]
                )
                db.add(db_ex)
                await db.flush()
                
                # Add Categories
                for cat in ex_data["categories"]:
                    db.add(models.ExerciseCategoryLink(exercise_id=db_ex.id, category=cat))
                
                # Add Measurement Types
                for mt in ex_data["measurement_types"]:
                    db.add(models.MeasurementTypeLink(
                        exercise_id=db_ex.id, 
                        measurement_type=mt["measurement_type"], 
                        is_required=mt["is_required"]
                    ))
                
                await db.commit()
                await db.refresh(db_ex)
                existing = db_ex
            else:
                print(f"Exercise {ex_data['name']} already exists.")
            
            created_exercises.append(existing)

        # 3. Create Teams
        teams_data = ["Jugend A", "Jugend B", "Jugend C"]
        created_teams = []
        for t_name in teams_data:
            res = await db.execute(select(models.Team).filter(models.Team.name == t_name))
            existing = res.scalars().first()
            if not existing:
                 print(f"Creating team: {t_name}")
                 new_team = models.Team(name=t_name, season="2024/2025")
                 db.add(new_team)
                 await db.commit()
                 await db.refresh(new_team)
                 existing = new_team
                 
                 # Assign our coach to this team
                 # Using insert for Many-to-Many Table
                 await db.execute(models.team_coaches.insert().values(team_id=new_team.id, coach_id=owner_coach_id))
                 await db.commit()

            created_teams.append(existing)


        # 4. Create Players
        first_names = ["Lukas", "Tim", "Jan", "Niklas", "Finn", "Leon", "Elias", "Jonas", "Luis", "Paul", "Felix", "David", "Julian", "Philipp", "Maximilian"]
        last_names = ["Müller", "Schmidt", "Schneider", "Fischer", "Weber", "Meyer", "Wagner", "Becker", "Schulz", "Hoffmann", "Koch", "Richter", "Klein", "Wolf", "Schröder"]
        
        created_players = []
        
        # Ensure we have enough unique names
        for i in range(30): # Increased to fill 3 teams
            fn = random.choice(first_names)
            ln = random.choice(last_names)
            
            # Check if player exists (loose check)
            res = await db.execute(select(models.Player).filter(models.Player.first_name == fn, models.Player.last_name == ln))
            existing = res.scalars().first()
            
            if not existing:
                print(f"Creating player: {fn} {ln}")
                # Create user for player
                email = f"{fn.lower()}.{ln.lower()}{i}@example.com"
                user_res = await db.execute(select(models.User).filter(models.User.email == email))
                if user_res.scalars().first():
                    continue

                hashed_pwd = hash_password("password")
                new_user = models.User(email=email, password_hash=hashed_pwd, role=models.Role.player)
                db.add(new_user)
                await db.flush()
                
                # Create player
                birth_year = random.randint(2005, 2010) # Youth ages approx 15-20
                new_player = models.Player(user_id=new_user.id, first_name=fn, last_name=ln, birth_year=birth_year)
                db.add(new_player)
                await db.flush()
                
                # Assign to random team from our list
                team = created_teams[i % len(created_teams)] # Distribute evenly
                await db.execute(models.team_players.insert().values(team_id=team.id, player_id=new_player.id))
                await db.commit()
                await db.refresh(new_player)
                existing = new_player
            
            created_players.append(existing)

        # 5. Generate Measurements
        print("Generating historical measurements...")
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365) # 1 year back
        
        for player in created_players:
            # For each exercise
            for exercise in created_exercises:
                 # Decide if this player does this exercise
                 if random.random() < 0.2: # 20% chance they don't do it at all
                     continue

                 # Get primary measurement type
                 # Need to re-fetch exercise with links to be safe or use simple logic
                 # Using crud helper
                 exercise_full = await crud_measurements.get_exercise_with_measurement_types(db, exercise.id)
                 if not exercise_full.measurement_type_links:
                     continue
                 
                 primary_link = exercise_full.measurement_type_links[0]
                 mt_type = primary_link.measurement_type
                 
                 # Base value depends on exercise
                 base_value = 0
                 if "Bench" in exercise.name: base_value = random.randint(60, 100)
                 elif "Squat" in exercise.name: base_value = random.randint(80, 140)
                 elif "Sprint" in exercise.name: base_value = random.uniform(4.8, 6.0)
                 elif "Cooper" in exercise.name: base_value = random.randint(2200, 3200)
                 elif "Agility" in exercise.name: base_value = random.uniform(9.0, 12.0)
                 
                 # Generate 6-12 entries
                 num_entries = random.randint(6, 12)
                 for k in range(num_entries):
                     # Random date within the year
                     # Sort dates later? No, db handles it. But for logical progression lets make them sequential roughly
                     date_offset = k * (365 / num_entries)
                     entry_date = start_date + timedelta(days=date_offset) + timedelta(days=random.randint(-5, 5))
                     
                     if entry_date > datetime.now(): break
                     
                     # Add progression
                     # Strength/Endurance usually increases
                     # Sprint/Agility time decreases
                     progression = k * (base_value * 0.02) * random.uniform(0.5, 1.5) # 2% improvement per month roughly
                     
                     current_value = base_value
                     if mt_type in [models.MeasurementType.seconds]:
                         current_value -= progression * 0.5 # Time decreases (slower improvement than weight)
                     else:
                         current_value += progression
                     
                     # Add noise
                     noise = current_value * 0.02 * random.uniform(-1, 1)
                     final_value = current_value + noise
                     
                     # Format value
                     val_str = f"{final_value:.2f}"
                     if mt_type in [models.MeasurementType.kilograms, models.MeasurementType.repetitions, models.MeasurementType.meters]:
                         val_str = str(int(final_value))

                     # Create Measurement
                     # Check if exists on this date approx? Nah just add.
                     
                     meas_in = schemas.PlayerMeasurementCreate(
                         player_id=player.id,
                         exercise_id=exercise.id,
                         recorded_at=entry_date,
                         notes="Auto-generated",
                         values=[schemas.MeasurementValueSchema(measurement_type=mt_type, value=val_str)]
                     )
                     
                     await crud_measurements.create_player_measurement(db, meas_in, created_by_user_id=owner_id)
        
        print("Database population completed successfully!")

if __name__ == "__main__":
    asyncio.run(populate())
