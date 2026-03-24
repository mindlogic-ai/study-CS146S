"use client";

import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  Legend,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  ResponsiveContainer,
} from "recharts";

const COLORS = [
  "#FF6384",
  "#36A2EB",
  "#FFCE56",
  "#4BC0C0",
  "#9966FF",
  "#FF9F40",
  "#C9CBCF",
  "#7BC8A4",
  "#E7E9ED",
];

export default function Charts({ summary }) {
  const { by_category = [], total_income = 0, total_expense = 0 } = summary || {};

  const pieData = by_category.map((item) => ({
    name: item.category,
    value: item.total,
  }));

  const barData = [
    { name: "수입", amount: total_income },
    { name: "지출", amount: total_expense },
  ];

  return (
    <div className="charts-container">
      <div className="chart-box">
        <h3>카테고리별 지출</h3>
        {pieData.length > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={pieData}
                dataKey="value"
                nameKey="name"
                cx="50%"
                cy="50%"
                outerRadius={80}
                label={({ name, percent }) =>
                  `${name} ${(percent * 100).toFixed(0)}%`
                }
              >
                {pieData.map((_, index) => (
                  <Cell
                    key={`cell-${index}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
              <Legend />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <div className="chart-placeholder">데이터가 없습니다</div>
        )}
      </div>
      <div className="chart-box">
        <h3>수입 vs 지출</h3>
        {total_income > 0 || total_expense > 0 ? (
          <ResponsiveContainer width="100%" height={250}>
            <BarChart data={barData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
              <Bar dataKey="amount">
                <Cell fill="#2196F3" />
                <Cell fill="#f44336" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <div className="chart-placeholder">데이터가 없습니다</div>
        )}
      </div>
    </div>
  );
}
