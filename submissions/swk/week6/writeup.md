# Week 6 Write-up
Tip: To preview this markdown file
- On Mac, press `Command (⌘) + Shift + V`
- On Windows/Linux, press `Ctrl + Shift + V`

## Instructions

Fill out all of the `TODO`s in this file.

## Submission Details

Name: **swk** \
SUNet ID: **swk** \
Citations: **Claude Code**

This assignment took me about **0.5** hours to do.


## Brief findings overview
> Semgrep scanned 19 files with 489 rules and reported **6 blocking findings**, all in
> the SAST (Static Application Security Testing) category:
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
> No Secrets or SCA (Supply Chain Analysis) findings were reported.
>
> **Remaining unfixed findings (3):**
> - `wildcard-cors`: Left as-is because this is a local development app; restricting
>   origins would break the dev setup. In production, this should be set to specific domains.
> - `subprocess-shell-true`: The `/debug/run` endpoint is intentionally dangerous demo
>   code. In production, this entire endpoint should be removed.
> - `dynamic-urllib-use-detected`: The `/debug/fetch` endpoint is similarly demo code
>   that would be removed in production.

## Fix #1: SQL Injection
a. File and line(s)
> `backend/app/routers/notes.py`, lines 71–79 (original)

b. Rule/category Semgrep flagged
> `python.sqlalchemy.security.audit.avoid-sqlalchemy-text.avoid-sqlalchemy-text` (SAST)

c. Brief risk description
> The `/unsafe-search` endpoint used `sqlalchemy.text()` with an f-string to construct
> a raw SQL query, directly interpolating the user-supplied `q` parameter into the SQL
> string. An attacker could inject arbitrary SQL (e.g., `' OR 1=1 --`) to dump the
> entire database, modify data, or extract sensitive information.

d. Your change (short code diff or explanation, AI coding tool usage)
> **Before:**
> ```python
> sql = text(
>     f"""
>     SELECT id, title, content, created_at, updated_at
>     FROM notes
>     WHERE title LIKE '%{q}%' OR content LIKE '%{q}%'
>     ORDER BY created_at DESC
>     LIMIT 50
>     """
> )
> rows = db.execute(sql).all()
> ```
>
> **After:**
> ```python
> stmt = (
>     select(Note)
>     .where((Note.title.contains(q)) | (Note.content.contains(q)))
>     .order_by(desc(Note.created_at))
>     .limit(50)
> )
> rows = db.execute(stmt).scalars().all()
> return [NoteRead.model_validate(row) for row in rows]
> ```
>
> Used Claude Code to replace the raw SQL with SQLAlchemy ORM query builder, which
> automatically parameterizes user input.

e. Why this mitigates the issue
> SQLAlchemy's ORM methods (`contains()`, `select()`, etc.) use parameterized queries
> internally, meaning user input is never interpolated into the SQL string. The database
> driver treats the `q` value as a parameter, not as SQL code, completely preventing
> SQL injection attacks.

## Fix #2: Code Injection via eval()
a. File and line(s)
> `backend/app/routers/notes.py`, line 104 (original)

b. Rule/category Semgrep flagged
> `python.lang.security.audit.eval-detected.eval-detected` (SAST)

c. Brief risk description
> The `/debug/eval` endpoint passed user-supplied input directly to Python's `eval()`,
> allowing arbitrary code execution. An attacker could run any Python code on the server
> (e.g., `__import__('os').system('rm -rf /')`) — this is a Remote Code Execution (RCE)
> vulnerability, one of the most critical security issues possible.

d. Your change (short code diff or explanation, AI coding tool usage)
> **Before:**
> ```python
> result = str(eval(expr))  # noqa: S307
> ```
>
> **After:**
> ```python
> import ast
> import operator
>
> allowed_ops = {
>     ast.Add: operator.add,
>     ast.Sub: operator.sub,
>     ast.Mult: operator.mul,
>     ast.Div: operator.truediv,
>     ast.USub: operator.neg,
> }
>
> def _safe_eval(node):
>     if isinstance(node, ast.Expression):
>         return _safe_eval(node.body)
>     if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
>         return node.value
>     if isinstance(node, ast.BinOp) and type(node.op) in allowed_ops:
>         return allowed_ops[type(node.op)](_safe_eval(node.left), _safe_eval(node.right))
>     if isinstance(node, ast.UnaryOp) and type(node.op) in allowed_ops:
>         return allowed_ops[type(node.op)](_safe_eval(node.operand))
>     raise ValueError(f"Unsupported expression: {ast.dump(node)}")
>
> tree = ast.parse(expr, mode="eval")
> result = str(_safe_eval(tree))
> ```
>
> Used Claude Code to replace `eval()` with a safe AST-based evaluator that only allows
> arithmetic operations on numeric literals.

e. Why this mitigates the issue
> Instead of executing arbitrary Python code, the new implementation parses the expression
> into an AST and only evaluates nodes that are numeric constants or basic arithmetic
> operators (+, -, *, /). Any attempt to call functions, access attributes, or import
> modules results in a `ValueError` with a 400 HTTP response. This preserves the
> calculator functionality while eliminating the RCE attack surface.

## Fix #3: XSS via innerHTML
a. File and line(s)
> `frontend/app.js`, line 14 (original)

b. Rule/category Semgrep flagged
> `javascript.browser.security.insecure-document-method.insecure-document-method` (SAST)

c. Brief risk description
> The `loadNotes()` function used `innerHTML` to render note titles and content directly
> into the DOM. If an attacker stored a note with a malicious title like
> `<img src=x onerror=alert(document.cookie)>`, it would execute JavaScript in every
> user's browser who views the notes list — a Stored Cross-Site Scripting (XSS) attack
> that could steal session cookies or perform actions on behalf of the user.

d. Your change (short code diff or explanation, AI coding tool usage)
> **Before:**
> ```javascript
> li.innerHTML = `<strong>${n.title}</strong>: ${n.content}`;
> ```
>
> **After:**
> ```javascript
> const strong = document.createElement('strong');
> strong.textContent = n.title;
> li.appendChild(strong);
> li.appendChild(document.createTextNode(': ' + n.content));
> ```
>
> Used Claude Code to replace the `innerHTML` assignment with safe DOM API methods.

e. Why this mitigates the issue
> `textContent` and `createTextNode()` treat all input as plain text, never parsing it
> as HTML. Any HTML tags or script elements in the note title/content are displayed as
> literal text characters instead of being interpreted as markup. This completely prevents
> XSS attacks because the browser never executes the injected content as code.
