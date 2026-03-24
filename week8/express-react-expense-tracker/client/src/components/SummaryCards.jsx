function SummaryCards({ summary }) {
  const { total_income = 0, total_expense = 0, balance = 0 } = summary || {};

  return (
    <div className="summary-cards">
      <div className="card card-income">
        <h3>총수입</h3>
        <p className="amount">₩{total_income.toLocaleString()}</p>
      </div>
      <div className="card card-expense">
        <h3>총지출</h3>
        <p className="amount">₩{total_expense.toLocaleString()}</p>
      </div>
      <div className="card card-balance">
        <h3>잔액</h3>
        <p className="amount" style={{ color: balance >= 0 ? "#4caf50" : "#f44336" }}>
          ₩{balance.toLocaleString()}
        </p>
      </div>
    </div>
  );
}

export default SummaryCards;
