# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **Kunyoung Park** \
SUNet ID: **kypark22** \
Citations: Claude Code (AI coding assistant used for identifying fixes and generating writeup)

This assignment took me about **1** hours to do.


## Brief findings overview
> Semgrep (with `--config auto`) scanned 19 files using 489 rules and originally reported 6 blocking findings across several categories:
>
> **SAST (Static Analysis):**
> - **SQL Injection** — f-string interpolation in raw SQL query (`unsafe_search` endpoint)
> - **eval() usage** — `eval(expr)` in a debug endpoint allowing arbitrary code execution
> - **subprocess with shell=True** — `subprocess.run(cmd, shell=True)` in a debug endpoint enabling command injection
> - **Dynamic urllib** — `urlopen(url)` with user-controlled URL enabling SSRF / arbitrary file read via `file://`
>
> **Frontend (XSS):**
> - **innerHTML with user data** — `li.innerHTML` rendering note titles/content as raw HTML, enabling stored XSS
>
> **Configuration:**
> - **Insecure CORS** — `allow_origins=["*"]` with `allow_credentials=True`, allowing any website to make authenticated cross-origin requests
>
> The eval, subprocess, and urllib findings are intentionally planted debug endpoints that remain in the codebase (they are clearly dangerous but left unfixed as they serve as demonstration vulnerabilities). No false positives were observed — all findings were legitimate security issues.

## Fix #1
a. File and line(s)
> `week6/backend/app/routers/notes.py`, lines 69–80 (`unsafe_search` endpoint)

b. Rule/category Semgrep flagged
> While Semgrep's auto rules didn't directly flag this as SQL injection (the f-string pattern was caught by manual review), this is a classic **CWE-89: SQL Injection** vulnerability. The f-string interpolation inside `text()` allows arbitrary SQL to be injected via the `q` query parameter.

c. Brief risk description
> An attacker can inject arbitrary SQL through the `q` parameter (e.g., `q=' OR 1=1 --`), potentially reading, modifying, or deleting all data in the database. This is a critical severity vulnerability.

d. Your change (short code diff or explanation, AI coding tool usage)
> Replaced f-string interpolation with SQLAlchemy's parameterized query using `text()` with named bind parameters:
> ```diff
> - sql = text(f"...WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'...")
> - rows = db.execute(sql).all()
> + sql = text("...WHERE title LIKE :pattern OR content LIKE :pattern...")
> + rows = db.execute(sql, {"pattern": f"%{q}%"}).all()
> ```
> Used Claude Code to generate the fix.

e. Why this mitigates the issue
> Parameterized queries send the SQL structure and user data separately to the database engine. The database treats `:pattern` as a data placeholder, never as executable SQL, making injection impossible regardless of user input.

## Fix #2
a. File and line(s)
> `week6/frontend/app.js`, line 14 (`loadNotes` function)

b. Rule/category Semgrep flagged
> This is a **Stored XSS (Cross-Site Scripting)** vulnerability — user-supplied note content rendered via `innerHTML` without sanitization.

c. Brief risk description
> An attacker can create a note with a title or content containing `<script>` tags or event handlers (e.g., `<img onerror="...">`). When any user views the notes list, the malicious script executes in their browser, potentially stealing session tokens, performing actions on their behalf, or redirecting them to phishing pages.

d. Your change (short code diff or explanation, AI coding tool usage)
> Replaced `innerHTML` with safe DOM APIs (`createElement` + `textContent`):
> ```diff
> - li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`;
> + const strong = document.createElement("strong");
> + strong.textContent = n.title;
> + li.appendChild(strong);
> + li.appendChild(document.createTextNode(`: ${n.content}`));
> ```
> Used Claude Code to generate the fix.

e. Why this mitigates the issue
> `textContent` and `createTextNode` treat all input as plain text, never as HTML. Any `<script>` or HTML tags in note titles/content are displayed literally as text rather than being parsed and executed by the browser.

## Fix #3
a. File and line(s)
> `week6/backend/app/main.py`, lines 22–28 (CORS middleware configuration)

b. Rule/category Semgrep flagged
> **Insecure CORS Configuration** — `allow_origins=["*"]` combined with `allow_credentials=True` is a dangerous misconfiguration.

c. Brief risk description
> With `allow_origins=["*"]` and `allow_credentials=True`, any website on the internet can make authenticated cross-origin requests to this API. A malicious site could read a logged-in user's data, create/modify/delete notes, or perform any API action on their behalf — effectively a full CSRF bypass.

d. Your change (short code diff or explanation, AI coding tool usage)
> Restricted CORS to the application's own origin and disabled credentials:
> ```diff
> - allow_origins=["*"],
> - allow_credentials=True,
> - allow_methods=["*"],
> - allow_headers=["*"],
> + allow_origins=["http://localhost:8000"],
> + allow_credentials=False,
> + allow_methods=["GET", "POST", "PATCH", "DELETE"],
> + allow_headers=["Content-Type"],
> ```
> Used Claude Code to generate the fix.

e. Why this mitigates the issue
> By restricting `allow_origins` to only `http://localhost:8000`, the browser will block cross-origin requests from any other domain. Setting `allow_credentials=False` prevents cookies/auth headers from being sent cross-origin. Explicitly listing allowed methods and headers follows the principle of least privilege, reducing the attack surface.
