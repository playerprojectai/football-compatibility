import requests
from flask import Flask, request, jsonify
import pandas as pd
import threading
import time

app = Flask(__name__)
API_KEY = "d4ac659404904b65994d01995bd92c3a"  # Replace with your key
BASE_URL = "https://api.football-data.org/v4/"
players_data = []

def update_data():
    global players_data
    while True:
        headers = {"X-Auth-Token": API_KEY}
        matches = requests.get(f"{BASE_URL}competitions/2021/matches?status=LIVE", headers=headers).json()
        
        temp_players = []
        for match in matches.get("matches", []):
            for team in ["homeTeam", "awayTeam"]:
                team_id = match[team]["id"]
                team_data = requests.get(f"{BASE_URL}teams/{team_id}", headers=headers).json()
                squad = requests.get(f"{BASE_URL}teams/{team_id}/squad", headers=headers).json()
                for player in squad.get("squad", []):
                    temp_players.append({
                        "player_id": player["id"],
                        "name": player["name"],
                        "team": team_data["name"],
                        "position": player["position"] or "Unknown",
                        "goals": 0,
                        "assists": 0,
                        "tackles": 0,
                        "pass_accuracy": 0,
                        "age": 25
                    })
        players_data = temp_players
        pd.DataFrame(players_data).to_csv("players_live.csv", index=False)
        time.sleep(60)

threading.Thread(target=update_data, daemon=True).start()

def calculate_compatibility(player, team_name):
    team_styles = {
        "Manchester City": {"goals": 0.5, "pass_accuracy": 0.3, "tackles": 0.2},
        "Paris Saint-Germain": {"goals": 0.4, "assists": 0.4, "pass_accuracy": 0.2},
        "Real Madrid": {"goals": 0.6, "tackles": 0.3, "age": 0.1}
    }
    style = team_styles.get(team_name, {"goals": 0.5, "assists": 0.5})
    score = (
        style.get("goals", 0) * min(player["goals"] / 30, 1) +
        style.get("assists", 0) * min(player["assists"] / 15, 1) +
        style.get("pass_accuracy", 0) * (player["pass_accuracy"] / 100) +
        style.get("tackles", 0) * min(player["tackles"] / 50, 1) +
        style.get("age", 0) * (1 - (player["age"] - 18) / 22)
    ) * 100
    return round(min(max(score, 0), 100), 2)

@app.route("/compatibility", methods=["POST"])
def compatibility():
    req = request.json
    player_name = req["player_name"]
    team_name = req["team_name"]

    df = pd.read_csv("players_live.csv")
    player_row = df[df["name"].str.contains(player_name, case=False, na=False)]
    if player_row.empty:
        return jsonify({"error": "Player not found"}), 404
    player = player_row.iloc[0]

    compatibility_score = calculate_compatibility(player, team_name)
    return jsonify({
        "player_name": player["name"],
        "team_name": team_name,
        "compatibility": compatibility_score
    })

if __name__ == "__main__":
    app.run(debug=True, port=5000)