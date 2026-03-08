# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Jeongbin Kim** \
SUNet ID: **jbk** \
Citations: **Claude Code (Anthropic)**

This assignment took me about **2** hours to do.


## Brief findings overview
> Semgrep 스캔 결과 4개 카테고리(SAST, Secrets, SCA, Client-side)에서 총 7개 취약점이 발견되었습니다.
> - **SAST**: SQL Injection (f-string으로 raw SQL 생성), Code Injection (`eval()`), Command Injection (`subprocess.run(shell=True)`)
> - **Secrets**: 소스코드에 하드코딩된 API 토큰
> - **SCA (Supply Chain)**: PyYAML, Werkzeug, requests, Jinja2, pydantic 등 알려진 CVE가 있는 오래된 의존성
> - **Client-side**: XSS (`innerHTML`), Wildcard CORS (`allow_origins=["*"]`)

## Fix #1 — SQL Injection
a. File and line(s)
> `backend/app/routers/notes.py:71-79`

b. Rule/category Semgrep flagged
> SAST — `python.sqlalchemy.security.sqlalchemy-execute-raw-query`, `python.lang.security.audit.avoid-sqlalchemy-text`

c. Brief risk description
> f-string으로 사용자 입력(`q` 파라미터)을 직접 SQL 쿼리에 삽입하여 SQL Injection 공격이 가능합니다. 공격자가 `' OR 1=1 --` 같은 입력으로 전체 데이터를 유출하거나 데이터를 수정/삭제할 수 있습니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> `text(f"... WHERE title LIKE '%{q}%' ...")` 방식을 SQLAlchemy ORM의 `or_(Note.title.ilike(pattern), Note.content.ilike(pattern))`으로 변경했습니다. 엔드포인트 이름도 `/unsafe-search`에서 `/search`로 변경했습니다. Claude Code를 사용하여 수정했습니다.

e. Why this mitigates the issue
> SQLAlchemy ORM의 `ilike()`는 내부적으로 parameterized query를 생성하므로 사용자 입력이 SQL 구문으로 해석되지 않고 데이터 값으로만 처리됩니다.

## Fix #2 — Code Injection (eval)
a. File and line(s)
> `backend/app/routers/notes.py:102-105`

b. Rule/category Semgrep flagged
> SAST — `python.lang.security.audit.eval-detected`, `python.flask.security.injection.tainted-code-stdlib-fastapi`

c. Brief risk description
> `eval(expr)`로 사용자 입력을 Python 코드로 직접 실행합니다. 공격자가 `__import__('os').system('rm -rf /')` 같은 입력으로 서버에서 임의 코드를 실행할 수 있는 RCE(Remote Code Execution) 취약점입니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> `/debug/eval` 엔드포인트를 전체 삭제했습니다. 프로덕션 환경에 디버그용 eval 엔드포인트가 존재해서는 안 됩니다. 함께 `/debug/hash-md5`, `/debug/fetch`, `/debug/read` 등 다른 debug 엔드포인트도 모두 삭제했습니다. Claude Code를 사용하여 수정했습니다.

e. Why this mitigates the issue
> 엔드포인트 자체를 제거하여 공격 표면(attack surface)을 완전히 없앴습니다. eval은 안전하게 사용할 수 있는 방법이 없으므로 삭제가 올바른 대응입니다.

## Fix #3 — Command Injection (shell=True)
a. File and line(s)
> `backend/app/routers/notes.py:108-113`

b. Rule/category Semgrep flagged
> SAST — `python.lang.security.audit.subprocess-shell-true`, `python.flask.security.injection.tainted-os-command-stdlib-fastapi`

c. Brief risk description
> `subprocess.run(cmd, shell=True)`로 사용자 입력을 OS 명령어로 직접 실행합니다. 공격자가 `; cat /etc/passwd` 같은 입력으로 서버의 시스템 명령을 실행할 수 있는 Command Injection 취약점입니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> Fix #2와 함께 `/debug/run` 엔드포인트를 전체 삭제했습니다. Claude Code를 사용하여 수정했습니다.

e. Why this mitigates the issue
> 엔드포인트 자체를 제거하여 OS 명령 실행 경로를 완전히 차단했습니다.

## Fix #4 — Hardcoded API Token
a. File and line(s)
> `backend/app/services/extract.py:13`

b. Rule/category Semgrep flagged
> Secrets — hardcoded API token detected

c. Brief risk description
> 소스코드에 API 토큰(`sk_live_...`)이 하드코딩되어 있습니다. 코드가 Git에 커밋되면 토큰이 저장소에 영구 기록되어, 저장소 접근 권한이 있는 모든 사람이 토큰을 획득할 수 있습니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> 하드코딩된 토큰을 `os.environ.get("API_TOKEN")`으로 변경하여 환경변수에서 읽도록 했습니다. Claude Code를 사용하여 수정했습니다.

e. Why this mitigates the issue
> API 토큰이 소스코드에 포함되지 않으므로 Git 히스토리나 코드 유출을 통한 토큰 노출이 방지됩니다. 환경변수는 배포 환경에서 안전하게 관리할 수 있습니다.

## Fix #5 — Vulnerable Dependencies (SCA)
a. File and line(s)
> `requirements.txt:1-9`

b. Rule/category Semgrep flagged
> SCA (Supply Chain) — 알려진 CVE가 있는 취약한 의존성 버전

c. Brief risk description
> PyYAML 5.1에는 CRITICAL CVE 3개(임의 코드 실행), Werkzeug 0.14.1에는 HIGH CVE(디버거 PIN 우회), requests 2.19.1과 Jinja2 2.10.1에도 각각 보안 취약점이 존재합니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> 취약한 패키지들을 안전한 최소 버전으로 업그레이드했습니다: PyYAML 5.1→5.4.1, Werkzeug 0.14.1→3.0.6, requests 2.19.1→2.32.4, Jinja2 2.10.1→3.1.6, pydantic 1.5.1→1.10.13, MarkupSafe 1.1.0→2.1.5. Claude Code를 사용하여 수정했습니다.

e. Why this mitigates the issue
> 알려진 CVE가 패치된 버전으로 업그레이드하여 해당 취약점들의 악용 가능성을 제거했습니다.

## Fix #6 — XSS (Cross-Site Scripting)
a. File and line(s)
> `frontend/app.js:14`

b. Rule/category Semgrep flagged
> Code — `javascript.browser.security.insecure-document-method.insecure-document-method`

c. Brief risk description
> `innerHTML`에 서버에서 받은 노트 데이터를 그대로 삽입하여, 노트 title/content에 `<img src=x onerror=alert('XSS')>` 같은 악성 HTML을 저장하면 다른 사용자가 페이지를 볼 때 스크립트가 실행됩니다. 세션 탈취, 피싱 등에 악용될 수 있습니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> `li.innerHTML = ...`을 `document.createElement('strong')` + `textContent`로 변경하여 DOM API를 통해 안전하게 텍스트를 삽입하도록 했습니다. Claude Code를 사용하여 수정했습니다.

e. Why this mitigates the issue
> `textContent`는 문자열을 HTML로 파싱하지 않고 순수 텍스트로 처리하므로, 악성 스크립트가 포함되어 있어도 실행되지 않습니다.

## Fix #7 — Wildcard CORS
a. File and line(s)
> `backend/app/main.py:24`

b. Rule/category Semgrep flagged
> Code — `python.fastapi.security.wildcard-cors.wildcard-cors`

c. Brief risk description
> `allow_origins=["*"]`는 모든 도메인에서의 cross-origin 요청을 허용합니다. 악성 사이트에서 사용자의 브라우저를 통해 API에 요청을 보내 데이터를 탈취하거나 조작할 수 있습니다.

d. Your change (short code diff or explanation, AI coding tool usage)
> `allow_origins=["*"]`를 `allow_origins=["http://localhost:8000"]`으로 변경하여 자기 자신의 origin만 허용하도록 했습니다. Claude Code를 사용하여 수정했습니다.

e. Why this mitigates the issue
> 허용된 origin만 cross-origin 요청을 보낼 수 있으므로, 외부 악성 사이트에서의 CSRF/데이터 탈취 공격을 차단합니다.
