"""MCP Tool 등록 — TMDB 영화 검색, 상세, 추천, 트렌드, 출연진 조회."""

from datetime import datetime
from typing import Any

from mcp.server.fastmcp import FastMCP

from .tmdb import format_movie, format_movie_detail, make_tmdb_request


def register_tools(mcp: FastMCP) -> None:
    """MCP 서버 인스턴스에 tool들을 등록합니다."""

    @mcp.tool()
    async def search_movie(query: str, year: int | None = None) -> str:
        """영화를 검색합니다.

        Args:
            query: 검색할 영화 제목 또는 키워드
            year: 개봉 연도로 필터링 (선택사항)
        """
        if not query or not query.strip():
            return "검색어를 입력해주세요."

        if year is not None and (year < 1888 or year > datetime.now().year + 2):
            return f"유효하지 않은 연도입니다. 1888~{datetime.now().year + 2} 범위로 입력해주세요."

        params: dict[str, Any] = {"query": query.strip()}
        if year:
            params["year"] = year

        data = await make_tmdb_request("/search/movie", params)

        if not data:
            return "영화 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

        results = data.get("results", [])

        if not results:
            return f"'{query}'에 대한 검색 결과가 없습니다."

        movies = results[:5]
        output = f"🔍 '{query}' 검색 결과 ({len(results)}개 중 상위 5개):\n"
        output += "=" * 50

        for movie in movies:
            output += format_movie(movie)
            output += f"🔗 ID: {movie.get('id')} (상세 정보 조회 시 사용)\n"
            output += "-" * 50

        return output

    @mcp.tool()
    async def get_movie_details(movie_id: int) -> str:
        """영화의 상세 정보를 조회합니다.

        Args:
            movie_id: TMDB 영화 ID (search_movie로 검색하면 확인 가능)
        """
        if movie_id <= 0:
            return "유효하지 않은 영화 ID입니다. 양수를 입력해주세요."

        data = await make_tmdb_request(f"/movie/{movie_id}")

        if not data:
            return f"영화 ID {movie_id}의 정보를 가져올 수 없습니다."

        return format_movie_detail(data)

    @mcp.tool()
    async def get_recommendations(movie_id: int) -> str:
        """특정 영화와 비슷한 영화를 추천받습니다.

        Args:
            movie_id: 기준이 될 영화의 TMDB ID
        """
        if movie_id <= 0:
            return "유효하지 않은 영화 ID입니다. 양수를 입력해주세요."

        original = await make_tmdb_request(f"/movie/{movie_id}")
        original_title = (
            original.get("title", "알 수 없는 영화") if original else "알 수 없는 영화"
        )

        data = await make_tmdb_request(f"/movie/{movie_id}/recommendations")

        if not data:
            return "추천 영화를 가져오는 중 오류가 발생했습니다."

        results = data.get("results", [])

        if not results:
            return f"'{original_title}'과(와) 비슷한 영화를 찾을 수 없습니다."

        movies = results[:5]
        output = f"🎯 '{original_title}'을(를) 좋아하셨다면 이런 영화는 어떠세요?\n"
        output += "=" * 50

        for movie in movies:
            output += format_movie(movie)
            output += f"🔗 ID: {movie.get('id')}\n"
            output += "-" * 50

        return output

    @mcp.tool()
    async def get_trending_movies(time_window: str = "day") -> str:
        """현재 인기 있는 영화 목록을 가져옵니다.

        Args:
            time_window: 'day' (오늘) 또는 'week' (이번 주)
        """
        if time_window not in ["day", "week"]:
            time_window = "day"

        data = await make_tmdb_request(f"/trending/movie/{time_window}")

        if not data:
            return "인기 영화를 가져오는 중 오류가 발생했습니다."

        results = data.get("results", [])

        if not results:
            return "현재 인기 영화 정보가 없습니다."

        movies = results[:5]
        time_label = "오늘" if time_window == "day" else "이번 주"
        output = f"🔥 {time_label}의 인기 영화 TOP 5:\n"
        output += "=" * 50

        for i, movie in enumerate(movies, 1):
            output += f"\n#{i}"
            output += format_movie(movie)
            output += f"🔗 ID: {movie.get('id')}\n"
            output += "-" * 50

        return output

    @mcp.tool()
    async def get_movie_credits(movie_id: int) -> str:
        """영화의 출연진과 제작진 정보를 조회합니다.

        Args:
            movie_id: TMDB 영화 ID
        """
        if movie_id <= 0:
            return "유효하지 않은 영화 ID입니다. 양수를 입력해주세요."

        movie_data = await make_tmdb_request(f"/movie/{movie_id}")
        movie_title = (
            movie_data.get("title", "알 수 없는 영화") if movie_data else "알 수 없는 영화"
        )

        data = await make_tmdb_request(f"/movie/{movie_id}/credits")

        if not data:
            return "출연진 정보를 가져오는 중 오류가 발생했습니다."

        cast = data.get("cast", [])[:10]
        crew = data.get("crew", [])

        directors = [c for c in crew if c.get("job") == "Director"]

        output = f"🎬 '{movie_title}' 출연진 & 제작진\n"
        output += "=" * 50

        if directors:
            output += "\n\n🎥 감독:\n"
            for d in directors:
                output += f"  • {d.get('name', '알 수 없음')}\n"

        if cast:
            output += "\n👥 주요 출연진:\n"
            for actor in cast:
                name = actor.get("name", "알 수 없음")
                character = actor.get("character", "역할 미상")
                output += f"  • {name} → {character}\n"

        return output
