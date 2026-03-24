function TransactionTable({ transactions, onEdit, onDelete }) {
  if (!transactions || transactions.length === 0) {
    return <p className="no-data">거래 내역이 없습니다</p>;
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
              <td>{tx.date}</td>
              <td>{tx.type === "income" ? "수입" : "지출"}</td>
              <td>{tx.category}</td>
              <td>{tx.description}</td>
              <td
                style={{
                  color: tx.type === "income" ? "#2196F3" : "#f44336",
                  fontWeight: "bold",
                }}
              >
                ₩{tx.amount.toLocaleString()}
              </td>
              <td>
                <button className="btn-edit" onClick={() => onEdit(tx)}>
                  수정
                </button>
                <button className="btn-delete" onClick={() => onDelete(tx.id)}>
                  삭제
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default TransactionTable;
