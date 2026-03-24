"use client";

import { useState, useEffect } from "react";

const EXPENSE_CATEGORIES = ["식비", "교통", "쇼핑", "주거", "여가", "기타"];
const INCOME_CATEGORIES = ["급여", "용돈", "기타수입"];

export default function TransactionForm({ transaction, onSave, onCancel }) {
  const [form, setForm] = useState({
    type: "expense",
    category: "식비",
    amount: "",
    date: new Date().toISOString().slice(0, 10),
    description: "",
  });

  useEffect(() => {
    if (transaction) {
      setForm({
        type: transaction.type || "expense",
        category: transaction.category || "식비",
        amount: transaction.amount || "",
        date: transaction.date?.slice(0, 10) || new Date().toISOString().slice(0, 10),
        description: transaction.description || "",
      });
    }
  }, [transaction]);

  const categories =
    form.type === "income" ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;

  const handleTypeChange = (type) => {
    const newCategories =
      type === "income" ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;
    setForm((prev) => ({
      ...prev,
      type,
      category: newCategories[0],
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      ...form,
      amount: Number(form.amount),
    });
  };

  return (
    <div className="modal-overlay" onClick={onCancel}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h2>{transaction ? "거래 수정" : "새 거래 추가"}</h2>
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>타입</label>
            <div className="radio-group">
              <label>
                <input
                  type="radio"
                  name="type"
                  value="expense"
                  checked={form.type === "expense"}
                  onChange={() => handleTypeChange("expense")}
                />
                지출
              </label>
              <label>
                <input
                  type="radio"
                  name="type"
                  value="income"
                  checked={form.type === "income"}
                  onChange={() => handleTypeChange("income")}
                />
                수입
              </label>
            </div>
          </div>
          <div className="form-group">
            <label>카테고리</label>
            <select
              value={form.category}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, category: e.target.value }))
              }
            >
              {categories.map((cat) => (
                <option key={cat} value={cat}>
                  {cat}
                </option>
              ))}
            </select>
          </div>
          <div className="form-group">
            <label>금액</label>
            <input
              type="number"
              min="0"
              required
              value={form.amount}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, amount: e.target.value }))
              }
              placeholder="금액을 입력하세요"
            />
          </div>
          <div className="form-group">
            <label>날짜</label>
            <input
              type="date"
              required
              value={form.date}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, date: e.target.value }))
              }
            />
          </div>
          <div className="form-group">
            <label>메모</label>
            <input
              type="text"
              value={form.description}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, description: e.target.value }))
              }
              placeholder="메모를 입력하세요"
            />
          </div>
          <div className="form-actions">
            <button type="button" className="btn btn-secondary" onClick={onCancel}>
              취소
            </button>
            <button type="submit" className="btn btn-primary">
              {transaction ? "수정" : "추가"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
