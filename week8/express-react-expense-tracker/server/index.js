import express from "express";
import cors from "cors";
import db from "./db.js";

const app = express();
const PORT = 3001;

app.use(cors({ origin: "http://localhost:5173" }));
app.use(express.json());

// GET /api/transactions
app.get("/api/transactions", (req, res) => {
  const { month, category, type } = req.query;
  let sql = "SELECT * FROM transactions WHERE 1=1";
  const params = [];

  if (month) {
    const [year, mon] = month.split("-").map(Number);
    const nextMonth = mon === 12 ? 1 : mon + 1;
    const nextYear = mon === 12 ? year + 1 : year;
    const start = `${year}-${String(mon).padStart(2, "0")}-01`;
    const end = `${nextYear}-${String(nextMonth).padStart(2, "0")}-01`;
    sql += " AND date >= ? AND date < ?";
    params.push(start, end);
  }

  if (category) {
    sql += " AND category = ?";
    params.push(category);
  }

  if (type) {
    sql += " AND type = ?";
    params.push(type);
  }

  sql += " ORDER BY date DESC";

  const rows = db.prepare(sql).all(...params);
  res.json(rows);
});

// POST /api/transactions
app.post("/api/transactions", (req, res) => {
  const { type, category, amount, description, date } = req.body;
  const result = db.prepare(
    "INSERT INTO transactions (type, category, amount, description, date) VALUES (?, ?, ?, ?, ?)"
  ).run(type, category, amount, description ?? "", date);
  res.status(201).json({ id: result.lastInsertRowid });
});

// PATCH /api/transactions/:id
app.patch("/api/transactions/:id", (req, res) => {
  const { id } = req.params;
  const fields = req.body;
  const keys = Object.keys(fields);

  if (keys.length === 0) {
    return res.status(400).json({ error: "No fields to update" });
  }

  const setClauses = keys.map((k) => `${k} = ?`).join(", ");
  const values = keys.map((k) => fields[k]);

  const result = db.prepare(`UPDATE transactions SET ${setClauses} WHERE id = ?`).run(...values, id);

  if (result.changes === 0) {
    return res.status(404).json({ error: "Transaction not found" });
  }

  res.json({ updated: result.changes });
});

// DELETE /api/transactions/:id
app.delete("/api/transactions/:id", (req, res) => {
  const { id } = req.params;
  const result = db.prepare("DELETE FROM transactions WHERE id = ?").run(id);

  if (result.changes === 0) {
    return res.status(404).json({ error: "Transaction not found" });
  }

  res.json({ deleted: result.changes });
});

// GET /api/summary
app.get("/api/summary", (req, res) => {
  const now = new Date();
  const month = req.query.month || `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  const [year, mon] = month.split("-").map(Number);
  const nextMonth = mon === 12 ? 1 : mon + 1;
  const nextYear = mon === 12 ? year + 1 : year;
  const start = `${year}-${String(mon).padStart(2, "0")}-01`;
  const end = `${nextYear}-${String(nextMonth).padStart(2, "0")}-01`;

  const totals = db.prepare(`
    SELECT type, COALESCE(SUM(amount), 0) as total
    FROM transactions
    WHERE date >= ? AND date < ?
    GROUP BY type
  `).all(start, end);

  const totalIncome = totals.find((r) => r.type === "income")?.total ?? 0;
  const totalExpense = totals.find((r) => r.type === "expense")?.total ?? 0;

  const byCategory = db.prepare(`
    SELECT category, SUM(amount) as total
    FROM transactions
    WHERE date >= ? AND date < ?
    GROUP BY category
  `).all(start, end);

  res.json({
    month,
    total_income: totalIncome,
    total_expense: totalExpense,
    balance: totalIncome - totalExpense,
    by_category: byCategory,
  });
});

// GET /api/categories
app.get("/api/categories", (_req, res) => {
  res.json({
    expense: ["식비", "교통", "쇼핑", "주거", "여가", "기타"],
    income: ["급여", "용돈", "기타수입"],
  });
});

app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});
