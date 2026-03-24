"use client";

export default function SummaryCards({ summary }) {
  const { total_income = 0, total_expense = 0, balance = 0 } = summary || {};

  return (
    <div className="summary-cards">
      <div className="summary-card income">
        <h3>총수입</h3>
        <p>₩{total_income.toLocaleString()}</p>
      </div>
      <div className="summary-card expense">
        <h3>총지출</h3>
        <p>₩{total_expense.toLocaleString()}</p>
      </div>
      <div className="summary-card balance">
        <h3>잔액</h3>
        <p className={balance >= 0 ? "positive" : "negative"}>
          ₩{balance.toLocaleString()}
        </p>
      </div>
    </div>
  );
}
