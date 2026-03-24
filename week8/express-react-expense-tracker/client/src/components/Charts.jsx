import {
  PieChart,
  Pie,
  Cell,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from "recharts";

const PIE_COLORS = [
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

function Charts({ summary }) {
  const { total_income = 0, total_expense = 0, by_category = [] } = summary || {};

  const barData = [
    { name: "수입", value: total_income },
    { name: "지출", value: total_expense },
  ];

  const hasCategoryData = by_category && by_category.length > 0;
  const hasBarData = total_income > 0 || total_expense > 0;

  return (
    <div className="charts">
      <div className="chart-container">
        <h3>카테고리별 지출</h3>
        {hasCategoryData ? (
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={by_category}
                dataKey="total"
                nameKey="category"
                cx="50%"
                cy="50%"
                outerRadius={100}
                label={({ category, percent }) =>
                  `${category} (${(percent * 100).toFixed(0)}%)`
                }
              >
                {by_category.map((_, index) => (
                  <Cell key={index} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
            </PieChart>
          </ResponsiveContainer>
        ) : (
          <p className="no-data">데이터가 없습니다</p>
        )}
      </div>
      <div className="chart-container">
        <h3>수입 vs 지출</h3>
        {hasBarData ? (
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={barData}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip formatter={(value) => `₩${value.toLocaleString()}`} />
              <Legend />
              <Bar dataKey="value" name="금액">
                <Cell fill="#2196F3" />
                <Cell fill="#f44336" />
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        ) : (
          <p className="no-data">데이터가 없습니다</p>
        )}
      </div>
    </div>
  );
}

export default Charts;
