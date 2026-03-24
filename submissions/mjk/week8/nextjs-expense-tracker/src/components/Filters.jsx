"use client";

const ALL_CATEGORIES = [
  "식비",
  "교통",
  "쇼핑",
  "주거",
  "여가",
  "기타",
  "급여",
  "용돈",
  "기타수입",
];

export default function Filters({ filters, onChange }) {
  const handleChange = (key, value) => {
    onChange((prev) => ({ ...prev, [key]: value }));
  };

  return (
    <div className="filters">
      <div>
        <label>월</label>
        <input
          type="month"
          value={filters.month}
          onChange={(e) => handleChange("month", e.target.value)}
        />
      </div>
      <div>
        <label>카테고리</label>
        <select
          value={filters.category}
          onChange={(e) => handleChange("category", e.target.value)}
        >
          <option value="">전체</option>
          {ALL_CATEGORIES.map((cat) => (
            <option key={cat} value={cat}>
              {cat}
            </option>
          ))}
        </select>
      </div>
      <div>
        <label>타입</label>
        <select
          value={filters.type}
          onChange={(e) => handleChange("type", e.target.value)}
        >
          <option value="">전체</option>
          <option value="income">수입</option>
          <option value="expense">지출</option>
        </select>
      </div>
    </div>
  );
}
