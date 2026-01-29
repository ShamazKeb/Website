import asyncio
from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.models import User, Player, Team, team_players

async def create_missing_player():
    async with AsyncSessionLocal() as session:
        # Fetch User
        result = await session.execute(select(User).filter(User.email == "johann.thygs@handball.player"))
        user = result.scalars().first()
        
        if not user:
            print("User 'johann.thygs@handball.player' not found.")
            return

        print(f"User Found: ID={user.id}")

        # Check if player already exists (to avoid duplicate unique key error if run multiple times)
        result = await session.execute(select(Player).filter(Player.user_id == user.id))
        existing_player = result.scalars().first()
        if existing_player:
            print(f"Player already exists for User {user.id}: ID={existing_player.id}")
            new_player = existing_player
        else:
            # Create Player
            new_player = Player(
                first_name="Johann",
                last_name="Thygs",
                birth_year=2000,
                user_id=user.id,
                is_active=True
            )
            session.add(new_player)
            await session.commit()
            await session.refresh(new_player)
            print(f"Created Player: ID={new_player.id} linked to User {user.id}")

        # Link to Team 1 (assuming it exists, or fetch first team)
        team_result = await session.execute(select(Team).limit(1))
        team = team_result.scalars().first()
        
        if team:
            # Check if link exists
            link_check = await session.execute(select(team_players).filter(team_players.c.team_id == team.id, team_players.c.player_id == new_player.id))
            if link_check.first():
                 print(f"Player already linked to Team: {team.name}")
            else:
                # Insert into team_players table
                await session.execute(team_players.insert().values(team_id=team.id, player_id=new_player.id))
                await session.commit()
                print(f"Linked Player to Team: {team.name} (ID: {team.id})")
        else:
            print("No teams found to link to.")

if __name__ == "__main__":
    asyncio.run(create_missing_player())
