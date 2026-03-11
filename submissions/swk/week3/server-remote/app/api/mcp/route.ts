import { z } from "zod";
import { createMcpHandler, withMcpAuth } from "mcp-handler";
import type { AuthInfo } from "@modelcontextprotocol/sdk/server/auth/types.js";

const MCP_API_KEY = process.env.MCP_API_KEY ?? "";

// --- Helper ---

const COINGECKO_API_BASE = "https://api.coingecko.com/api/v3";
const API_KEY = process.env.COINGECKO_API_KEY ?? "";
const MAX_RETRIES = 3;
const REQUEST_TIMEOUT_MS = 15_000;

function sleep(ms: number) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function coinGeckoRequest<T>(
  path: string,
  params: Record<string, string> = {}
): Promise<T> {
  const url = new URL(`${COINGECKO_API_BASE}${path}`);
  for (const [k, v] of Object.entries(params)) {
    url.searchParams.set(k, v);
  }
  if (API_KEY) {
    url.searchParams.set("x_cg_demo_api_key", API_KEY);
  }

  for (let attempt = 1; attempt <= MAX_RETRIES; attempt++) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), REQUEST_TIMEOUT_MS);

    try {
      const response = await fetch(url.toString(), {
        headers: { Accept: "application/json" },
        signal: controller.signal,
      });

      if (response.status === 429) {
        if (attempt < MAX_RETRIES) {
          const backoffMs = attempt * 2000;
          console.log(
            `Rate limited (429). Retrying in ${backoffMs}ms (attempt ${attempt}/${MAX_RETRIES})...`
          );
          await sleep(backoffMs);
          continue;
        }
        throw new Error(
          "Rate limit exceeded after retries. Please wait before making another request."
        );
      }

      if (!response.ok) {
        throw new Error(
          `CoinGecko API error: ${response.status} ${response.statusText}`
        );
      }

      return (await response.json()) as T;
    } catch (err) {
      if ((err as Error).name === "AbortError") {
        if (attempt < MAX_RETRIES) {
          console.log(
            `Request timed out. Retrying (attempt ${attempt}/${MAX_RETRIES})...`
          );
          continue;
        }
        throw new Error(
          "Request timed out after retries. The CoinGecko API may be slow or unreachable."
        );
      }
      throw err;
    } finally {
      clearTimeout(timeout);
    }
  }

  throw new Error("Unexpected: exhausted retries.");
}

// --- Types ---

interface CoinMarket {
  id: string;
  symbol: string;
  name: string;
  current_price: number | null;
  market_cap: number | null;
  market_cap_rank: number | null;
  total_volume: number | null;
  price_change_percentage_24h: number | null;
  high_24h: number | null;
  low_24h: number | null;
}

interface CoinDetail {
  id: string;
  symbol: string;
  name: string;
  description: { en: string };
  market_data: {
    current_price: Record<string, number>;
    market_cap: Record<string, number>;
    total_volume: Record<string, number>;
    price_change_percentage_24h: number | null;
    price_change_percentage_7d: number | null;
    price_change_percentage_30d: number | null;
    high_24h: Record<string, number>;
    low_24h: Record<string, number>;
    circulating_supply: number | null;
    total_supply: number | null;
    max_supply: number | null;
  };
}

interface TrendingResponse {
  coins: Array<{
    item: {
      id: string;
      name: string;
      symbol: string;
      market_cap_rank: number | null;
      data: {
        price: number;
        price_change_percentage_24h: Record<string, number>;
      };
    };
  }>;
}

// --- MCP Handler ---

const handler = createMcpHandler(
  (server) => {
    // Tool 1: Get coin markets
    server.tool(
      "get_coin_markets",
      "Get current market data (price, market cap, volume, 24h change) for cryptocurrencies. Can filter by specific coin IDs or get top coins by market cap.",
      {
        vs_currency: z
          .string()
          .default("usd")
          .describe("Target currency (e.g. usd, eur, krw)"),
        ids: z
          .string()
          .optional()
          .describe(
            "Comma-separated coin IDs (e.g. bitcoin,ethereum). Leave empty for top coins."
          ),
        per_page: z
          .number()
          .int()
          .min(1)
          .max(50)
          .default(10)
          .describe("Number of results (1-50, default 10)"),
      },
      async ({ vs_currency, ids, per_page }) => {
        try {
          const params: Record<string, string> = {
            vs_currency,
            per_page: String(per_page),
            order: "market_cap_desc",
            sparkline: "false",
          };
          if (ids) params.ids = ids;

          const data = await coinGeckoRequest<CoinMarket[]>(
            "/coins/markets",
            params
          );

          if (data.length === 0) {
            return { content: [{ type: "text", text: "No results found." }] };
          }

          const lines = data.map((coin) => {
            const change = coin.price_change_percentage_24h;
            const changeStr =
              change != null
                ? `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`
                : "N/A";
            return [
              `${coin.market_cap_rank ?? "-"}. ${coin.name} (${coin.symbol.toUpperCase()})`,
              `   Price: ${coin.current_price != null ? `$${coin.current_price.toLocaleString()}` : "N/A"}`,
              `   24h: ${changeStr}  |  Vol: $${coin.total_volume != null ? coin.total_volume.toLocaleString() : "N/A"}`,
              `   High/Low: $${coin.high_24h ?? "N/A"} / $${coin.low_24h ?? "N/A"}`,
            ].join("\n");
          });

          return { content: [{ type: "text", text: lines.join("\n\n") }] };
        } catch (err) {
          return {
            content: [
              { type: "text", text: `Error: ${(err as Error).message}` },
            ],
            isError: true,
          };
        }
      }
    );

    // Tool 2: Get coin detail
    server.tool(
      "get_coin_detail",
      "Get detailed information about a specific cryptocurrency including description, market data, price changes, and supply info.",
      {
        coin_id: z
          .string()
          .describe("CoinGecko coin ID (e.g. bitcoin, ethereum, solana)"),
        vs_currency: z
          .string()
          .default("usd")
          .describe("Target currency (e.g. usd, eur, krw)"),
      },
      async ({ coin_id, vs_currency }) => {
        try {
          const data = await coinGeckoRequest<CoinDetail>(
            `/coins/${encodeURIComponent(coin_id)}`,
            {
              localization: "false",
              tickers: "false",
              community_data: "false",
              developer_data: "false",
            }
          );

          const md = data.market_data;
          const cur = vs_currency.toLowerCase();
          const desc = data.description.en
            ? data.description.en.replace(/<[^>]*>/g, "").slice(0, 300) + "..."
            : "No description available.";

          const text = [
            `# ${data.name} (${data.symbol.toUpperCase()})`,
            "",
            desc,
            "",
            `## Market Data (${cur.toUpperCase()})`,
            `Price: $${md.current_price[cur]?.toLocaleString() ?? "N/A"}`,
            `Market Cap: $${md.market_cap[cur]?.toLocaleString() ?? "N/A"}`,
            `24h Volume: $${md.total_volume[cur]?.toLocaleString() ?? "N/A"}`,
            `24h High/Low: $${md.high_24h[cur] ?? "N/A"} / $${md.low_24h[cur] ?? "N/A"}`,
            "",
            `## Price Changes`,
            `24h: ${md.price_change_percentage_24h?.toFixed(2) ?? "N/A"}%`,
            `7d:  ${md.price_change_percentage_7d?.toFixed(2) ?? "N/A"}%`,
            `30d: ${md.price_change_percentage_30d?.toFixed(2) ?? "N/A"}%`,
            "",
            `## Supply`,
            `Circulating: ${md.circulating_supply?.toLocaleString() ?? "N/A"}`,
            `Total: ${md.total_supply?.toLocaleString() ?? "N/A"}`,
            `Max: ${md.max_supply?.toLocaleString() ?? "N/A"}`,
          ].join("\n");

          return { content: [{ type: "text", text }] };
        } catch (err) {
          return {
            content: [
              { type: "text", text: `Error: ${(err as Error).message}` },
            ],
            isError: true,
          };
        }
      }
    );

    // Tool 3: Get trending coins
    server.tool(
      "get_trending",
      "Get the top trending cryptocurrencies on CoinGecko based on search activity.",
      {},
      async () => {
        try {
          const data =
            await coinGeckoRequest<TrendingResponse>("/search/trending");

          if (data.coins.length === 0) {
            return {
              content: [{ type: "text", text: "No trending coins found." }],
            };
          }

          const lines = data.coins.map((c, i) => {
            const item = c.item;
            const change = item.data?.price_change_percentage_24h?.usd;
            const changeStr =
              change != null
                ? `${change >= 0 ? "+" : ""}${change.toFixed(2)}%`
                : "N/A";
            return `${i + 1}. ${item.name} (${item.symbol.toUpperCase()}) — Rank #${item.market_cap_rank ?? "N/A"} | 24h: ${changeStr}`;
          });

          return {
            content: [
              { type: "text", text: "# Trending Coins\n\n" + lines.join("\n") },
            ],
          };
        } catch (err) {
          return {
            content: [
              { type: "text", text: `Error: ${(err as Error).message}` },
            ],
            isError: true,
          };
        }
      }
    );
  },
  {},
  { basePath: "/api" }
);

// --- Auth ---

const verifyToken = async (
  _req: Request,
  bearerToken?: string
): Promise<AuthInfo | undefined> => {
  if (!MCP_API_KEY) return { token: "no-auth", scopes: [], clientId: "anonymous" };
  if (!bearerToken) return undefined;
  if (bearerToken !== MCP_API_KEY) return undefined;

  return {
    token: bearerToken,
    scopes: ["read:crypto"],
    clientId: "mcp-client",
  };
};

const authHandler = MCP_API_KEY
  ? withMcpAuth(handler, verifyToken, {
      required: true,
      requiredScopes: ["read:crypto"],
      resourceMetadataPath: "/.well-known/oauth-protected-resource",
    })
  : handler;

export { authHandler as GET, authHandler as POST, authHandler as DELETE };
