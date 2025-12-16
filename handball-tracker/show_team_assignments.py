import sqlite3

def show_assignments():
    conn = sqlite3.connect("app.db")
    
    query = """
    SELECT 
        t.name as Team,
        GROUP_CONCAT(DISTINCT p.first_name || ' ' || p.last_name) as Players,
        GROUP_CONCAT(DISTINCT c.first_name || ' ' || c.last_name) as Coaches
    FROM teams t
    LEFT JOIN team_players tp ON t.id = tp.team_id
    LEFT JOIN players p ON tp.player_id = p.id
    LEFT JOIN team_coaches tc ON t.id = tc.team_id
    LEFT JOIN coaches c ON tc.coach_id = c.id
    GROUP BY t.id
    """
    
    with open("final_report.txt", "w", encoding="utf-8") as f:
        f.write("--- Team Assignments (SQL Grouped) ---\n")
        try:
            cursor = conn.cursor()
            
            # DEBUG: Check raw tables
            f.write("\n[DEBUG] Raw Counts:\n")
            for table in ['users', 'teams', 'players', 'team_players', 'coaches', 'team_coaches']:
                try:
                    cursor.execute(f"SELECT count(*) FROM {table}")
                    f.write(f"  {table}: {cursor.fetchone()[0]}\n")
                except Exception as e:
                    f.write(f"  {table}: Error {e}\n")
                    
            f.write("\n[DEBUG] team_players dump:\n")
            cursor.execute("SELECT * FROM team_players")
            f.write(str(cursor.fetchall()) + "\n")

            cursor.execute(query)
            rows = cursor.fetchall()
            
            # Header
            f.write(f"\n{'Team':<20} | {'Players':<50} | {'Coaches':<30}\n")
            f.write("-" * 105 + "\n")
            
            if not rows:
                f.write("(No teams found)\n")
                
            for row in rows:
                team = row[0]
                players = row[1] if row[1] else "(None)"
                coaches = row[2] if row[2] else "(None)"
                f.write(f"{team:<20} | {players:<50} | {coaches:<30}\n")

        except Exception as e:
            f.write(f"Error executing query: {e}\n")

    conn.close()

if __name__ == "__main__":
    show_assignments()
