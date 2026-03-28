"""TMDB API 클라이언트 및 영화 정보 포맷터."""

import asyncio
import logging
import os
from typing import Any

import httpx

logger = logging.getLogger(__name__)

TMDB_API_BASE = "https://api.themoviedb.org/3"
TMDB_ACCESS_TOKEN = os.getenv("TMDB_ACCESS_TOKEN", "")
TMDB_API_KEY = os.getenv("TMDB_API_KEY", "")
DEFAULT_LANGUAGE = "ko-KR"


async def make_tmdb_request(
    endpoint: str, params: dict[str, Any] | None = None, _retry: int = 0
) -> dict[str, Any] | None:
    """TMDB API 요청을 수행하는 헬퍼 함수 (rate-limit 인식 포함)"""
    url = f"{TMDB_API_BASE}{endpoint}"

    headers = {"Authorization": f"Bearer {TMDB_ACCESS_TOKEN}", "Accept": "application/json"}

    if params is None:
        params = {}

    if "language" not in params:
        params["language"] = DEFAULT_LANGUAGE

    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url, headers=headers, params=params, timeout=30.0)

            remaining = response.headers.get("X-RateLimit-Remaining")
            if remaining is not None:
                logger.info(f"Rate limit remaining: {remaining} for {endpoint}")
                if int(remaining) < 5:
                    logger.warning(f"Rate limit nearly exhausted: {remaining} remaining")

            if response.status_code == 429:
                if _retry < 1:
                    retry_after = int(response.headers.get("Retry-After", "2"))
                    logger.warning(f"Rate limited on {endpoint}. Retrying after {retry_after}s...")
                    await asyncio.sleep(retry_after)
                    return await make_tmdb_request(endpoint, params, _retry=_retry + 1)
                else:
                    logger.error(f"Rate limit exceeded for {endpoint} after retry")
                    return None

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
