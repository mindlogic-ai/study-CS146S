import { z } from "zod";
import { createMcpHandler, withMcpAuth } from "mcp-handler";
import { AuthInfo } from "@modelcontextprotocol/sdk/server/auth/types.js";

const BALLDONTLIE_API_KEY = process.env.BALLDONTLIE_API_KEY || "";
const BALLDONTLIE_BASE_URL = "https://api.balldontlie.io/v1";
const MCP_API_KEY = process.env.MCP_API_KEY || "nba-mcp-secret-key";

// Team name to ID mapping
const TEAM_NAME_MAP: Record<string, number> = {
  // Full names
  "atlanta hawks": 1, "boston celtics": 2, "brooklyn nets": 3, "charlotte hornets": 4,
  "chicago bulls": 5, "cleveland cavaliers": 6, "dallas mavericks": 7, "denver nuggets": 8,
  "detroit pistons": 9, "golden state warriors": 10, "houston rockets": 11, "indiana pacers": 12,
  "los angeles clippers": 13, "los angeles lakers": 14, "memphis grizzlies": 15,
  "miami heat": 16, "milwaukee bucks": 17, "minnesota timberwolves": 18,
  "new orleans pelicans": 19, "new york knicks": 20, "oklahoma city thunder": 21,
  "orlando magic": 22, "philadelphia 76ers": 23, "phoenix suns": 24, "portland trail blazers": 25,
  "sacramento kings": 26, "san antonio spurs": 27, "toronto raptors": 28, "utah jazz": 29,
  "washington wizards": 30,
  // Short names
  "hawks": 1, "celtics": 2, "nets": 3, "hornets": 4, "bulls": 5, "cavaliers": 6, "cavs": 6,
  "mavericks": 7, "mavs": 7, "nuggets": 8, "pistons": 9, "warriors": 10, "dubs": 10,
  "rockets": 11, "pacers": 12, "clippers": 13, "lakers": 14, "grizzlies": 15, "heat": 16,
  "bucks": 17, "timberwolves": 18, "wolves": 18, "pelicans": 19, "pels": 19, "knicks": 20,
  "thunder": 21, "okc": 21, "magic": 22, "sixers": 23, "76ers": 23, "suns": 24,
  "trail blazers": 25, "blazers": 25, "kings": 26, "spurs": 27, "raptors": 28, "jazz": 29,
  "wizards": 30,
  // Abbreviations
  "atl": 1, "bos": 2, "bkn": 3, "cha": 4, "chi": 5, "cle": 6, "dal": 7, "den": 8,
  "det": 9, "gsw": 10, "hou": 11, "ind": 12, "lac": 13, "lal": 14, "mem": 15,
  "mia": 16, "mil": 17, "min": 18, "nop": 19, "nyk": 20, "orl": 22,
  "phi": 23, "phx": 24, "por": 25, "sac": 26, "sas": 27, "tor": 28, "uta": 29, "was": 30,
};

function getTeamId(teamName: string): number | undefined {
  return TEAM_NAME_MAP[teamName.toLowerCase().trim()];
}

interface Team {
  id: number;
  full_name: string;
  abbreviation: string;
  conference: string;
  division: string;
}

interface Player {
  id: number;
  first_name: string;
  last_name: string;
  position: string;
  height?: string;
  weight?: string;
  jersey_number?: string;
  team?: Team;
}

interface Game {
  id: number;
  date: string;
  status: string;
  home_team: Team;
  visitor_team: Team;
  home_team_score: number;
  visitor_team_score: number;
}

async function makeApiRequest<T>(endpoint: string, params?: Record<string, string>): Promise<T> {
  const url = new URL(`${BALLDONTLIE_BASE_URL}/${endpoint}`);
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      url.searchParams.append(key, value);
    });
  }

  const response = await fetch(url.toString(), {
    headers: {
      Authorization: BALLDONTLIE_API_KEY,
    },
  });

  if (!response.ok) {
    if (response.status === 429) {
      throw new Error("Rate limit exceeded. Please wait 60 seconds.");
    }
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

const handler = createMcpHandler(
  (server) => {
    // Tool 1: Get NBA Teams
    server.tool(
      "get_teams",
      "Get NBA teams, optionally filtered by conference (East or West)",
      { conference: z.string().optional().describe("Filter by conference: 'East' or 'West'") },
      async ({ conference }) => {
        try {
          const params: Record<string, string> = {};
          if (conference) {
            params.conference = conference;
          }

          const result = await makeApiRequest<{ data: Team[] }>("teams", params);
          const teams = result.data;

          if (!teams.length) {
            return { content: [{ type: "text", text: "No teams found." }] };
          }

          const eastTeams = teams.filter((t) => t.conference === "East");
          const westTeams = teams.filter((t) => t.conference === "West");

          let output = `NBA Teams (${teams.length} total):\n\n`;

          if (eastTeams.length && (!conference || conference.toLowerCase() === "east")) {
            output += "=== Eastern Conference ===\n";
            eastTeams.forEach((t) => {
              output += `  ${t.full_name} (${t.abbreviation}) - ${t.division} Division\n`;
            });
            output += "\n";
          }

          if (westTeams.length && (!conference || conference.toLowerCase() === "west")) {
            output += "=== Western Conference ===\n";
            westTeams.forEach((t) => {
              output += `  ${t.full_name} (${t.abbreviation}) - ${t.division} Division\n`;
            });
          }

          return { content: [{ type: "text", text: output }] };
        } catch (error) {
          return { content: [{ type: "text", text: `Error: ${error}` }] };
        }
      }
    );

    // Tool 2: Search NBA Players
    server.tool(
      "search_player",
      "Search for NBA players by name",
      { name: z.string().min(2).describe("Player name to search (at least 2 characters)") },
      async ({ name }) => {
        try {
          const result = await makeApiRequest<{ data: Player[] }>("players", { search: name });
          const players = result.data;

          if (!players.length) {
            return { content: [{ type: "text", text: `No players found matching '${name}'.` }] };
          }

          let output = `Players matching '${name}' (${players.length} found):\n\n`;
          players.slice(0, 10).forEach((p) => {
            const teamName = p.team?.full_name || "Unknown Team";
            const jersey = p.jersey_number ? `#${p.jersey_number}` : "";
            const position = p.position ? `Position: ${p.position}` : "";
            const height = p.height ? `Height: ${p.height}` : "";
            const weight = p.weight ? `Weight: ${p.weight} lbs` : "";

            output += `  • ${p.first_name} ${p.last_name} - ${teamName}`;
            if (jersey) output += `, ${jersey}`;
            if (position) output += `, ${position}`;
            if (height) output += `, ${height}`;
            if (weight) output += `, ${weight}`;
            output += "\n";
          });

          if (players.length > 10) {
            output += `\n  ... and ${players.length - 10} more results.`;
          }

          return { content: [{ type: "text", text: output }] };
        } catch (error) {
          return { content: [{ type: "text", text: `Error: ${error}` }] };
        }
      }
    );

    // Tool 3: Get NBA Games
    server.tool(
      "get_games",
      "Get NBA games, optionally filtered by date and/or team",
      {
        date: z.string().optional().describe("Game date in YYYY-MM-DD format"),
        team: z.string().optional().describe("Team name, city, or abbreviation (e.g., Lakers, LAL)"),
      },
      async ({ date, team }) => {
        try {
          const params: Record<string, string> = {};
          if (date) {
            params["dates[]"] = date;
          }

          let teamId: number | undefined;
          if (team) {
            teamId = getTeamId(team);
            if (!teamId) {
              return {
                content: [
                  {
                    type: "text",
                    text: `Unknown team '${team}'. Try full name (Los Angeles Lakers), short name (Lakers), or abbreviation (LAL).`,
                  },
                ],
              };
            }
            params["team_ids[]"] = teamId.toString();
          }

          const result = await makeApiRequest<{ data: Game[] }>("games", params);
          const games = result.data;

          if (!games.length) {
            const filterParts = [];
            if (date) filterParts.push(`date ${date}`);
            if (team) filterParts.push(`team ${team}`);
            const filterStr = filterParts.length ? filterParts.join(" and ") : "the given criteria";
            return { content: [{ type: "text", text: `No games found for ${filterStr}.` }] };
          }

          let header = "NBA Games";
          if (date) header += ` on ${date}`;
          if (team) header += ` for ${team}`;

          let output = `${header} (${games.length} games):\n\n`;
          games.slice(0, 15).forEach((g) => {
            const gameDate = g.date.slice(0, 10);
            let result: string;

            if (g.status === "Final") {
              result = `Final: ${g.visitor_team.full_name} ${g.visitor_team_score} @ ${g.home_team.full_name} ${g.home_team_score}`;
            } else if (["In Progress", "1st Qtr", "2nd Qtr", "3rd Qtr", "4th Qtr", "Halftime"].includes(g.status)) {
              result = `LIVE (${g.status}): ${g.visitor_team.full_name} ${g.visitor_team_score} @ ${g.home_team.full_name} ${g.home_team_score}`;
            } else {
              result = `Scheduled: ${g.visitor_team.full_name} @ ${g.home_team.full_name}`;
            }

            output += `  • [${gameDate}] ${result}\n`;
          });

          if (games.length > 15) {
            output += `\n  ... and ${games.length - 15} more games.`;
          }

          return { content: [{ type: "text", text: output }] };
        } catch (error) {
          return { content: [{ type: "text", text: `Error: ${error}` }] };
        }
      }
    );
  },
  {},
  { basePath: "/api" }
);

// Token verification function
const verifyToken = async (
  req: Request,
  bearerToken?: string
): Promise<AuthInfo | undefined> => {
  if (!bearerToken) return undefined;

  // Validate the token against our API key
  const isValid = bearerToken === MCP_API_KEY;
  if (!isValid) return undefined;

  return {
    token: bearerToken,
    scopes: ["read:teams", "read:players", "read:games"],
    clientId: "mcp-client",
    extra: {
      authenticated: true,
    },
  };
};

// Wrap handler with authentication
const authHandler = withMcpAuth(handler, verifyToken, {
  required: true,
  requiredScopes: ["read:teams"],
  resourceMetadataPath: "/.well-known/oauth-protected-resource",
});

export { authHandler as GET, authHandler as POST, authHandler as DELETE };
