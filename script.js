document.getElementById("searchForm").addEventListener("submit", async (e) => {
    e.preventDefault();
    const playerName = document.getElementById("playerName").value;
    const teamName = document.getElementById("teamName").value;

    const response = await fetch("http://localhost:5000/compatibility", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ player_name: playerName, team_name: teamName })
    });
    const data = await response.json();
    if (data.error) {
        document.getElementById("results").innerHTML = `<p>${data.error}</p>`;
    } else {
        document.getElementById("results").innerHTML = `
            <p>${data.player_name} - Compatibility with ${data.team_name}: ${data.compatibility}%</p>
        `;
    }
});