import { useState, useEffect } from "react";

const EXPENSE_CATEGORIES = ["식비", "교통", "쇼핑", "주거", "여가", "기타"];
const INCOME_CATEGORIES = ["급여", "용돈", "기타수입"];

function TransactionForm({ transaction, onSave, onCancel }) {
  const today = new Date().toISOString().slice(0, 10);

  const [type, setType] = useState("expense");
  const [category, setCategory] = useState(EXPENSE_CATEGORIES[0]);
  const [amount, setAmount] = useState("");
  const [date, setDate] = useState(today);
  const [description, setDescription] = useState("");

  useEffect(() => {
    if (transaction) {
      setType(transaction.type || "expense");
      setCategory(transaction.category || "");
      setAmount(transaction.amount || "");
      setDate(transaction.date || today);
      setDescription(transaction.description || "");
    }
  }, [transaction]);

  const categories = type === "income" ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;

  const handleTypeChange = (newType) => {
    setType(newType);
    const newCategories = newType === "income" ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;
    if (!newCategories.includes(category)) {
      setCategory(newCategories[0]);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSave({
      type,
      category,
      amount: Number(amount),
      date,
      description,
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
                  value="income"
                  checked={type === "income"}
                  onChange={() => handleTypeChange("income")}
                />
                수입
              </label>
              <label>
                <input
                  type="radio"
                  name="type"
                  value="expense"
                  checked={type === "expense"}
                  onChange={() => handleTypeChange("expense")}
                />
                지출
              </label>
            </div>
          </div>
          <div className="form-group">
            <label>카테고리</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)}>
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
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              required
              min="0"
            />
          </div>
          <div className="form-group">
            <label>날짜</label>
            <input
              type="date"
              value={date}
              onChange={(e) => setDate(e.target.value)}
              required
            />
          </div>
          <div className="form-group">
            <label>메모</label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
            />
          </div>
          <div className="form-buttons">
            <button type="submit" className="btn-save">
              저장
            </button>
            <button type="button" className="btn-cancel" onClick={onCancel}>
              취소
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default TransactionForm;
