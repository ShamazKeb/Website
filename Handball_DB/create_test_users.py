import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import User, Role, Coach, Player, Team, team_players
from app.security import hash_password

async def create_test_users():
    async with AsyncSessionLocal() as session:
        # 1. Coach
        print("Processing Coach account...")
        # Check for old simple username to update it or create new
        result = await session.execute(select(User).filter(User.email.in_([ "coach", "coach@test.com" ])))
        coach_user = result.scalars().first()
        
        if not coach_user:
            coach_user = User(
                email="coach@test.com",
                password_hash=hash_password("coach"),
                role=Role.coach
            )
            session.add(coach_user)
            await session.flush()
            print("- Created User 'coach@test.com'")
        else:
            # Update existing user to have correct email if it was the old one
            if coach_user.email == "coach":
                print("- Updating 'coach' to 'coach@test.com'")
                coach_user.email = "coach@test.com"
            
            coach_user.password_hash = hash_password("coach")
            session.add(coach_user)
            print("- Updated Coach user")

        # Check Linked Coach Profile
        result = await session.execute(select(Coach).filter(Coach.user_id == coach_user.id))
        coach_profile = result.scalars().first()
        if not coach_profile:
            coach_profile = Coach(
                user_id=coach_user.id,
                first_name="Test",
                last_name="Coach"
            )
            session.add(coach_profile)
            print("- Created Coach profile")
        
        # 2. Admin
        print("\nProcessing Admin account...")
        result = await session.execute(select(User).filter(User.email.in_([ "admin", "admin@test.com" ])))
        admin_user = result.scalars().first()
        
        if not admin_user:
            admin_user = User(
                email="admin@test.com",
                password_hash=hash_password("admin"),
                role=Role.admin
            )
            session.add(admin_user)
            await session.flush()
            print("- Created User 'admin@test.com'")
        else:
            if admin_user.email == "admin":
                 print("- Updating 'admin' to 'admin@test.com'")
                 admin_user.email = "admin@test.com"

            admin_user.password_hash = hash_password("admin")
            session.add(admin_user)
            print("- Updated Admin user")
            
        # 3. Player
        print("\nProcessing Player account...")
        result = await session.execute(select(User).filter(User.email.in_([ "player", "player@test.com" ])))
        player_user = result.scalars().first()
        
        if not player_user:
            player_user = User(
                email="player@test.com",
                password_hash=hash_password("player"),
                role=Role.player
            )
            session.add(player_user)
            await session.flush()
            print("- Created User 'player@test.com'")
        else:
            if player_user.email == "player":
                print("- Updating 'player' to 'player@test.com'")
                player_user.email = "player@test.com"
            
            player_user.password_hash = hash_password("player")
            session.add(player_user)
            print("- Updated Player user")

        # Check Linked Player Profile
        result = await session.execute(select(Player).filter(Player.user_id == player_user.id))
        player_profile = result.scalars().first()
        if not player_profile:
            player_profile = Player(
                user_id=player_user.id,
                first_name="Test",
                last_name="Player",
                birth_year=2005,
                is_active=True
            )
            session.add(player_profile)
            await session.flush() # get id
            print("- Created Player profile")
        
        # Link Player to a Team (Required for Dashboard often)
        team_result = await session.execute(select(Team).limit(1))
        team = team_result.scalars().first()
        if team:
            link_check = await session.execute(select(team_players).filter(team_players.c.team_id == team.id, team_players.c.player_id == player_profile.id))
            if not link_check.first():
                await session.execute(team_players.insert().values(team_id=team.id, player_id=player_profile.id))
                print(f"- Linked Player to Team '{team.name}'")
        else:
            print("- Warning: No teams found to link player to.")

        await session.commit()
        print("\nAll test accounts processed successfully.")

if __name__ == "__main__":
    asyncio.run(create_test_users())
