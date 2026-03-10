# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Min Seok Kim** \
SUNet ID: **msk** \
Citations: **Claude Code (claude.ai/code) for code fixes and writeup assistance**

This assignment took me about **2** hours to do.


## Brief findings overview
> Semgrep (`semgrep scan --config auto`) found **6 code findings** across the codebase (SAST category):
>
> | # | Rule | File | Severity |
> |---|------|------|----------|
> | 1 | `avoid-sqlalchemy-text` (SQL injection) | `backend/app/routers/notes.py:71-79` | ERROR |
> | 2 | `insecure-document-method` (XSS via innerHTML) | `frontend/app.js:14` | ERROR |
> | 3 | `wildcard-cors` (CORS allows any origin) | `backend/app/main.py:24` | WARNING |
> | 4 | `eval-detected` (arbitrary code execution) | `backend/app/routers/notes.py:104` | WARNING |
> | 5 | `subprocess-shell-true` (command injection) | `backend/app/routers/notes.py:112` | WARNING |
> | 6 | `dynamic-urllib-use-detected` (SSRF) | `backend/app/routers/notes.py:120` | WARNING |
>
> Additionally, a hardcoded API token was found in `backend/app/services/extract.py:13` through manual review (the `auto` config did not flag it, but it is a clear secrets issue).
>
> Findings 4-6 are intentional debug endpoints that should be removed entirely in production. I fixed 3 issues below and also removed the hardcoded secret as a bonus fix.

## Fix #1
a. File and line(s)
> `backend/app/routers/notes.py` lines 69-92 (the `/unsafe-search` endpoint)

b. Rule/category Semgrep flagged
> `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text` (SAST / Code)

c. Brief risk description
> The endpoint used an f-string to interpolate user input (`q`) directly into a raw SQL query. An attacker could inject arbitrary SQL via the `q` parameter (e.g., `' OR 1=1 --`) to dump all rows, modify data, or even extract sensitive information from other tables.

d. Your change (short code diff or explanation, AI coding tool usage)
> Replaced the f-string interpolation with SQLAlchemy's parameterized binding using `:pattern` named parameter:
> ```diff
> -    sql = text(
> -        f"""
> -        ...
> -        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
> -        ...
> -        """
> -    )
> -    rows = db.execute(sql).all()
> +    pattern = f"%{q}%"
> +    sql = text(
> +        """
> +        ...
> +        WHERE title LIKE :pattern OR content LIKE :pattern
> +        ...
> +        """
> +    )
> +    rows = db.execute(sql, {"pattern": pattern}).all()
> ```
> Used Claude Code to generate the parameterized query fix.

e. Why this mitigates the issue
> Parameterized queries send the user input as a bound parameter separate from the SQL statement. The database driver handles escaping, so the input is always treated as data, never as SQL syntax. This eliminates the SQL injection vector entirely.

## Fix #2
a. File and line(s)
> `frontend/app.js` line 14

b. Rule/category Semgrep flagged
> `javascript.browser.security.insecure-document-method.insecure-document-method` (SAST / Code)

c. Brief risk description
> The code used `li.innerHTML` to render note titles and content directly into the DOM. If a note's title or content contained malicious HTML/JavaScript (e.g., `<img src=x onerror=alert(1)>`), it would execute in the user's browser, leading to stored XSS. An attacker could steal session cookies, redirect users, or deface the page.

d. Your change (short code diff or explanation, AI coding tool usage)
> Replaced `innerHTML` with safe DOM creation methods:
> ```diff
> -    li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`;
> +    const strong = document.createElement('strong');
> +    strong.textContent = n.title;
> +    li.appendChild(strong);
> +    li.appendChild(document.createTextNode(': ' + n.content));
> ```
> Used Claude Code to generate the DOM-based replacement.

e. Why this mitigates the issue
> `textContent` and `createTextNode` automatically escape HTML entities. Any `<script>` tags or event handlers in the note data are rendered as plain text instead of being parsed as HTML. This eliminates the XSS vector while preserving the same visual output (bold title followed by content).

## Fix #3
a. File and line(s)
> `backend/app/main.py` line 24

b. Rule/category Semgrep flagged
> `python.fastapi.security.wildcard-cors.wildcard-cors` (SAST / Code)

c. Brief risk description
> The CORS middleware was configured with `allow_origins=["*"]`, meaning any website could make cross-origin requests to the API. Combined with `allow_credentials=True`, this could allow a malicious site to make authenticated requests on behalf of a logged-in user, leading to data theft or unauthorized actions (CSRF-like attacks via CORS).

d. Your change (short code diff or explanation, AI coding tool usage)
> Restricted the allowed origin to only the local development server:
> ```diff
> -    allow_origins=["*"],
> +    allow_origins=["http://localhost:8000"],
> ```
> Used Claude Code to apply the fix.

e. Why this mitigates the issue
> By explicitly listing allowed origins, only requests from `http://localhost:8000` (where the frontend is served) are permitted. Browsers will block cross-origin requests from any other domain, preventing malicious sites from exploiting the API. In production, this should be set to the actual deployment domain(s).
