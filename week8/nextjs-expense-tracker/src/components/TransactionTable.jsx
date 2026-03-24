"use client";

export default function TransactionTable({ transactions, onEdit, onDelete }) {
  if (!transactions || transactions.length === 0) {
    return (
      <div className="table-container">
        <div className="empty-message">거래 내역이 없습니다</div>
      </div>
    );
  }

  return (
    <div className="table-container">
      <table>
        <thead>
          <tr>
            <th>날짜</th>
            <th>타입</th>
            <th>카테고리</th>
            <th>메모</th>
            <th>금액</th>
            <th>액션</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx) => (
            <tr key={tx.id}>
              <td>{tx.date?.slice(0, 10)}</td>
              <td>{tx.type === "income" ? "수입" : "지출"}</td>
              <td>{tx.category}</td>
              <td>{tx.description}</td>
              <td
                className={
                  tx.type === "income" ? "amount-income" : "amount-expense"
                }
              >
                ₩{Number(tx.amount).toLocaleString()}
              </td>
              <td>
                <div className="actions">
                  <button
                    className="btn btn-primary"
                    onClick={() => onEdit(tx)}
                  >
                    수정
                  </button>
                  <button
                    className="btn btn-danger"
                    onClick={() => onDelete(tx.id)}
                  >
                    삭제
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
