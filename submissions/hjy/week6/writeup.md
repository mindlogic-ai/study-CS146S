# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Hyungjoon Yoo** \
SUNet ID: **hjy** \
Citations: **Claude Code (Anthropic)**

This assignment took me about **1** hours to do.


## Brief findings overview
> Semgrep (`--config auto`)으로 19개 파일을 489개 규칙으로 스캔한 결과, **6개 blocking finding**이 발견되었습니다.
>
> | # | Rule | File | Category |
> |---|------|------|----------|
> | 1 | `wildcard-cors` | `backend/app/main.py:24` | SAST — Insecure CORS |
> | 2 | `avoid-sqlalchemy-text` | `backend/app/routers/notes.py:71-79` | SAST — SQL Injection |
> | 3 | `eval-detected` | `backend/app/routers/notes.py:104` | SAST — Code Injection |
> | 4 | `subprocess-shell-true` | `backend/app/routers/notes.py:112` | SAST — Command Injection |
> | 5 | `dynamic-urllib-use-detected` | `backend/app/routers/notes.py:120` | SAST — SSRF |
> | 6 | `insecure-document-method` | `frontend/app.js:14` | SAST — XSS |
>
> 추가로 코드 리뷰를 통해 `backend/app/services/extract.py`에 하드코딩된 API 토큰(`sk_live_...`)과
> `backend/app/routers/notes.py`의 `/debug/read` 엔드포인트(임의 파일 읽기)를 발견했습니다.
> 이 두 항목은 Semgrep `--config auto`에서는 탐지되지 않았지만 명백한 보안 이슈입니다.
>
> **수정하지 않은 finding:** SQL Injection, eval(), dynamic urllib, innerHTML XSS는 이번에 수정하지 않았습니다.
> 이들은 별도의 안전한 대안 구현이 필요한 항목으로, 단순 삭제/설정 변경으로 해결할 수 있는 항목을 우선 수정했습니다.

## Fix #1 — Command Injection 제거
a. File and line(s)
> `backend/app/routers/notes.py`, lines 108–113 (수정 전 기준)

b. Rule/category Semgrep flagged
> `python.lang.security.audit.subprocess-shell-true.subprocess-shell-true` (SAST)

c. Brief risk description
> `/debug/run` 엔드포인트가 `subprocess.run(cmd, shell=True)`로 사용자 입력을 OS 명령어로 직접 실행합니다. 공격자가 `; cat /etc/passwd`나 `; rm -rf /` 같은 입력으로 서버에서 임의 시스템 명령을 실행할 수 있는 Command Injection 취약점입니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> `/debug/run` 엔드포인트 전체를 삭제했습니다. Claude Code를 사용하여 수정했습니다.
> ```diff
> -@router.get("/debug/run")
> -def debug_run(cmd: str) -> dict[str, str]:
> -    import subprocess
> -    completed = subprocess.run(cmd, shell=True, capture_output=True, text=True)
> -    return {"returncode": str(completed.returncode), "stdout": completed.stdout, "stderr": completed.stderr}
> ```

e. Why this mitigates the issue
> 엔드포인트 자체를 제거하여 OS 명령 실행 경로를 완전히 차단했습니다. 사용자 입력을 shell에 전달하는 것은 안전하게 사용할 수 있는 방법이 없으므로 삭제가 올바른 대응입니다.

## Fix #2 — Arbitrary File Read 제거
a. File and line(s)
> `backend/app/routers/notes.py`, lines 125–131 (수정 전 기준)

b. Rule/category Semgrep flagged
> 코드 리뷰를 통해 발견. `open(path, "r").read()`로 사용자가 지정한 경로의 파일을 읽는 엔드포인트입니다.

c. Brief risk description
> `/debug/read` 엔드포인트가 사용자 입력 `path`를 `open()`에 그대로 전달합니다. 공격자가 `/etc/passwd`, `.env`, 데이터베이스 파일 등 서버의 임의 파일을 읽을 수 있는 Path Traversal / Arbitrary File Read 취약점입니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> `/debug/read` 엔드포인트 전체를 삭제했습니다. Claude Code를 사용하여 수정했습니다.
> ```diff
> -@router.get("/debug/read")
> -def debug_read(path: str) -> dict[str, str]:
> -    try:
> -        content = open(path, "r").read(1024)
> -    except Exception as exc:
> -        raise HTTPException(status_code=400, detail=str(exc))
> -    return {"snippet": content}
> ```

e. Why this mitigates the issue
> 엔드포인트 자체를 제거하여 파일 읽기 경로를 완전히 차단했습니다. 프로덕션 환경에서 임의 파일을 읽을 수 있는 디버그 엔드포인트가 존재해서는 안 됩니다.

## Fix #3 — Wildcard CORS 제한
a. File and line(s)
> `backend/app/main.py`, lines 22–28

b. Rule/category Semgrep flagged
> `python.fastapi.security.wildcard-cors.wildcard-cors` (SAST)

c. Brief risk description
> `allow_origins=["*"]`와 `allow_credentials=True`가 함께 설정되어, 모든 도메인에서 인증 포함 cross-origin 요청을 보낼 수 있습니다. 악성 사이트에서 사용자의 브라우저를 통해 API에 요청을 보내 데이터를 탈취하거나 조작할 수 있는 CSRF 우회 취약점입니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> CORS 설정을 최소 권한 원칙에 맞게 제한했습니다. Claude Code를 사용하여 수정했습니다.
> ```diff
> -    allow_origins=["*"],
> -    allow_credentials=True,
> -    allow_methods=["*"],
> -    allow_headers=["*"],
> +    allow_origins=["http://localhost:8000"],
> +    allow_credentials=False,
> +    allow_methods=["GET", "POST", "PATCH", "DELETE"],
> +    allow_headers=["Content-Type"],
> ```

e. Why this mitigates the issue
> `allow_origins`를 `http://localhost:8000`으로 제한하여 외부 도메인에서의 cross-origin 요청을 브라우저가 차단합니다. `allow_credentials=False`로 쿠키/인증 헤더 전송을 비활성화하고, 허용 메서드와 헤더도 필요한 것만 명시하여 공격 표면을 최소화했습니다.
