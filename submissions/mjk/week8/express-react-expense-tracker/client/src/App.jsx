import { useState, useEffect } from "react";
import SummaryCards from "./components/SummaryCards";
import Charts from "./components/Charts";
import Filters from "./components/Filters";
import TransactionTable from "./components/TransactionTable";
import TransactionForm from "./components/TransactionForm";

function App() {
  const currentMonth = new Date().toISOString().slice(0, 7);

  const [transactions, setTransactions] = useState([]);
  const [summary, setSummary] = useState({
    month: currentMonth,
    total_income: 0,
    total_expense: 0,
    balance: 0,
    by_category: [],
  });
  const [filters, setFilters] = useState({
    month: currentMonth,
    category: "",
    type: "",
  });
  const [editingTransaction, setEditingTransaction] = useState(null);
  const [showForm, setShowForm] = useState(false);

  const fetchTransactions = async () => {
    const params = new URLSearchParams();
    if (filters.month) params.append("month", filters.month);
    if (filters.category) params.append("category", filters.category);
    if (filters.type) params.append("type", filters.type);

    try {
      const res = await fetch(`/api/transactions?${params}`);
      const data = await res.json();
      setTransactions(data);
    } catch (err) {
      console.error("Failed to fetch transactions:", err);
    }
  };

  const fetchSummary = async () => {
    const params = new URLSearchParams();
    if (filters.month) params.append("month", filters.month);

    try {
      const res = await fetch(`/api/summary?${params}`);
      const data = await res.json();
      setSummary(data);
    } catch (err) {
      console.error("Failed to fetch summary:", err);
    }
  };

  const handleSave = async (data) => {
    try {
      if (editingTransaction) {
        await fetch(`/api/transactions/${editingTransaction.id}`, {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
      } else {
        await fetch("/api/transactions", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(data),
        });
      }
      setShowForm(false);
      setEditingTransaction(null);
      fetchTransactions();
      fetchSummary();
    } catch (err) {
      console.error("Failed to save transaction:", err);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("정말 삭제하시겠습니까?")) return;
    try {
      await fetch(`/api/transactions/${id}`, { method: "DELETE" });
      fetchTransactions();
      fetchSummary();
    } catch (err) {
      console.error("Failed to delete transaction:", err);
    }
  };

  const handleEdit = (tx) => {
    setEditingTransaction(tx);
    setShowForm(true);
  };

  const handleFilterChange = (newFilters) => {
    setFilters(newFilters);
  };

  useEffect(() => {
    fetchTransactions();
    fetchSummary();
  }, [filters]);

  return (
    <div className="app">
      <h1>가계부</h1>
      <SummaryCards summary={summary} />
      <Charts summary={summary} />
      <Filters filters={filters} onChange={handleFilterChange} />
      <div className="actions">
        <button
          className="btn-add"
          onClick={() => {
            setEditingTransaction(null);
            setShowForm(true);
          }}
        >
          + 새 거래 추가
        </button>
      </div>
      {showForm && (
        <TransactionForm
          transaction={editingTransaction}
          onSave={handleSave}
          onCancel={() => {
            setShowForm(false);
            setEditingTransaction(null);
          }}
        />
      )}
      <TransactionTable
        transactions={transactions}
        onEdit={handleEdit}
        onDelete={handleDelete}
      />
    </div>
  );
}

export default App;
