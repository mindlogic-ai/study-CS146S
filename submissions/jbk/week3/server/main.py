"""
MCP Movie Server - TMDB API를 활용한 영화 정보 서버
"""

import os
import logging
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

# 로깅 설정 (STDIO 서버에서는 stderr로 출력해야 함)
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# FastMCP 서버 초기화
mcp = FastMCP("movie-server")

# TMDB API 설정
TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")

# 기본 언어 설정 (한국어)
DEFAULT_LANGUAGE = "ko-KR"


async def make_tmdb_request(
    endpoint: str, params: dict[str, Any] | None = None
) -> dict[str, Any] | None:
    """TMDB API 요청을 수행하는 헬퍼 함수"""
    url = f"{TMDB_API_BASE}{endpoint}"

    headers = {"Authorization": f"Bearer {TMDB_ACCESS_TOKEN}", "Accept": "application/json"}

    if params is None:
        params = {}

    # 기본 언어 설정
    if "language" not in params:
        params["language"] = DEFAULT_LANGUAGE

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException:
            logger.error(f"Request timeout for {endpoint}")
            return None
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code} for {endpoint}")
            return None
        except Exception as e:
            logger.error(f"Request failed for {endpoint}: {e}")
            return None


def format_movie(movie: dict) -> str:
    """영화 정보를 읽기 쉬운 형식으로 포맷팅"""
    title = movie.get("title", "제목 없음")
    original_title = movie.get("original_title", "")
    release_date = movie.get("release_date", "미정")
    vote_average = movie.get("vote_average", 0)
    overview = movie.get("overview", "줄거리 정보 없음")

    # 제목이 다르면 원제도 표시
    title_display = title
    if original_title and original_title != title:
        title_display = f"{title} ({original_title})"

    return f"""
🎬 {title_display}
📅 개봉일: {release_date}
⭐ 평점: {vote_average}/10
📝 줄거리: {overview[:200]}{"..." if len(overview) > 200 else ""}
"""


def format_movie_detail(movie: dict) -> str:
    """영화 상세 정보를 포맷팅"""
    title = movie.get("title", "제목 없음")
    original_title = movie.get("original_title", "")
    release_date = movie.get("release_date", "미정")
    vote_average = movie.get("vote_average", 0)
    vote_count = movie.get("vote_count", 0)
    runtime = movie.get("runtime", 0)
    overview = movie.get("overview", "줄거리 정보 없음")
    genres = ", ".join([g["name"] for g in movie.get("genres", [])])
    budget = movie.get("budget", 0)
    revenue = movie.get("revenue", 0)
    tagline = movie.get("tagline", "")

    title_display = title
    if original_title and original_title != title:
        title_display = f"{title} ({original_title})"

    result = f"""
🎬 {title_display}
{"💬 " + tagline if tagline else ""}
📅 개봉일: {release_date}
⏱️ 러닝타임: {runtime}분
🎭 장르: {genres}
⭐ 평점: {vote_average}/10 ({vote_count:,}명 투표)
"""

    if budget > 0:
        result += f"💰 제작비: ${budget:,}\n"
    if revenue > 0:
        result += f"💵 수익: ${revenue:,}\n"

    result += f"\n📝 줄거리:\n{overview}"

    return result


@mcp.tool()
async def search_movie(query: str, year: int | None = None) -> str:
    """영화를 검색합니다.

    Args:
        query: 검색할 영화 제목 또는 키워드
        year: 개봉 연도로 필터링 (선택사항)
    """
    params = {"query": query}
    if year:
        params["year"] = year

    data = await make_tmdb_request("/search/movie", params)

    if not data:
        return "영화 검색 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."

    results = data.get("results", [])

    if not results:
        return f"'{query}'에 대한 검색 결과가 없습니다."

    # 상위 5개 결과만 표시
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
    # 먼저 원본 영화 정보 가져오기
    original = await make_tmdb_request(f"/movie/{movie_id}")
    original_title = original.get("title", "알 수 없는 영화") if original else "알 수 없는 영화"

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
    # 영화 제목도 함께 가져오기
    movie_data = await make_tmdb_request(f"/movie/{movie_id}")
    movie_title = movie_data.get("title", "알 수 없는 영화") if movie_data else "알 수 없는 영화"

    data = await make_tmdb_request(f"/movie/{movie_id}/credits")

    if not data:
        return "출연진 정보를 가져오는 중 오류가 발생했습니다."

    cast = data.get("cast", [])[:10]  # 상위 10명
    crew = data.get("crew", [])

    # 감독 찾기
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


def main():
    """서버 실행"""
    logger.info("Movie MCP Server starting...")
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
