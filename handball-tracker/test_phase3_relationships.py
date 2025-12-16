from app.core.database import Base, engine, SessionLocal
from app.models.user import User, UserRole
from app.models.team import Team
from app.models.player import Player, Hand, Position
from app.models.coach import Coach
from sqlalchemy.orm import Session
import sys

def verify_relationships():
    print("--- Verifying Phase 3 Relationships ---")
    
    # 1. Create Tables
    print("Creating tables...")
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Cleanup
        from app.models.associations import team_players, team_coaches
        
        teams_to_del = db.query(Team).filter(Team.name == "RelTestTeam").all()
        for t in teams_to_del:
            db.execute(team_players.delete().where(team_players.c.team_id == t.id))
            db.execute(team_coaches.delete().where(team_coaches.c.team_id == t.id))
            
        players_to_del = db.query(Player).filter(Player.first_name == "RelTest").all()
        for p in players_to_del:
             db.execute(team_players.delete().where(team_players.c.player_id == p.id))

        coaches_to_del = db.query(Coach).filter(Coach.first_name == "RelTest").all()
        for c in coaches_to_del:
             db.execute(team_coaches.delete().where(team_coaches.c.coach_id == c.id))
             
        db.query(Player).filter(Player.first_name == "RelTest").delete()
        db.query(Coach).filter(Coach.first_name == "RelTest").delete()
        db.query(Team).filter(Team.name == "RelTestTeam").delete()
        db.commit()

        # 2. Setup Data
        user_p = User(email="rel_player@test.com", role=UserRole.PLAYER, password_hash="dummy")
        user_c = User(email="rel_coach@test.com", role=UserRole.COACH, password_hash="dummy")
        
        # Check if users exist (re-run safety)
        existing_p = db.query(User).filter(User.email == user_p.email).first()
        if existing_p: db.delete(existing_p)
        existing_c = db.query(User).filter(User.email == user_c.email).first()
        if existing_c: db.delete(existing_c)
        db.commit()
        
        db.add_all([user_p, user_c])
        db.commit()
        db.refresh(user_p)
        db.refresh(user_c)

        player = Player(user_id=user_p.id, first_name="RelTest", last_name="Player", is_active=True)
        coach = Coach(user_id=user_c.id, first_name="RelTest", last_name="Coach", is_active=True)
        team = Team(name="RelTestTeam", season="24/25", is_active=True)
        
        db.add_all([player, coach, team])
        db.commit()
        db.refresh(player)
        db.refresh(coach)
        db.refresh(team)
        
        print(f"Created: Player {player.id}, Coach {coach.id}, Team {team.id}")

        # 3. Test Linking
        print("Linking Player and Coach to Team...")
        team.players.append(player)
        team.coaches.append(coach)
        db.commit()
        
        # 4. Verify linking via Team
        db.refresh(team)
        print(f"Team Players: {len(team.players)}")
        print(f"Team Coaches: {len(team.coaches)}")
        assert len(team.players) == 1
        assert team.players[0].first_name == "RelTest"
        assert len(team.coaches) == 1
        assert team.coaches[0].first_name == "RelTest"
        
        # 5. Verify linking via Player/Coach (Back populates)
        db.refresh(player)
        db.refresh(coach)
        print(f"Player Teams: {len(player.teams)}")
        print(f"Coach Teams: {len(coach.teams)}")
        assert len(player.teams) == 1
        assert player.teams[0].name == "RelTestTeam"
        assert len(coach.teams) == 1
        assert coach.teams[0].name == "RelTestTeam"
        
        print("SUCCESS: Relationships verified bidirectionally.")

    except Exception as e:
        import traceback
        with open("error_log.txt", "w") as f:
            f.write(traceback.format_exc())
        print(f"ERROR written to error_log.txt")
        db.rollback()
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    verify_relationships()
