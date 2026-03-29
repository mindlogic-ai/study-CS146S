export default function Home() {
  return (
    <main style={{ padding: "2rem", fontFamily: "system-ui" }}>
      <h1>NBA MCP Server</h1>
      <p>This is an MCP server for NBA data powered by BALLDONTLIE API.</p>
      <h2>Available Tools</h2>
      <ul>
        <li><strong>get_teams</strong> - Get NBA teams by conference</li>
        <li><strong>search_player</strong> - Search for NBA players by name</li>
        <li><strong>get_games</strong> - Get NBA games by date/team</li>
      </ul>
      <h2>MCP Endpoint</h2>
      <code>/api/mcp</code>
    </main>
  );
}
