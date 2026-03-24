var API_BASE = "";

var currentMonth = "";
var currentCategory = "";
var currentType = "";

var pieChart = null;
var barChart = null;

var EXPENSE_CATEGORIES = ["식비", "교통", "쇼핑", "주거", "여가", "기타"];
var INCOME_CATEGORIES = ["급여", "용돈", "기타수입"];

document.addEventListener("DOMContentLoaded", function () {
    var now = new Date();
    currentMonth =
        now.getFullYear() + "-" + String(now.getMonth() + 1).padStart(2, "0");
    document.getElementById("filter-month").value = currentMonth;

    populateFilterCategories();
    updateCategoryOptions();

    document
        .getElementById("filter-month")
        .addEventListener("change", function () {
            currentMonth = this.value;
            fetchAll();
        });
    document
        .getElementById("filter-category")
        .addEventListener("change", function () {
            currentCategory = this.value;
            fetchAll();
        });
    document
        .getElementById("filter-type")
        .addEventListener("change", function () {
            currentType = this.value;
            fetchAll();
        });

    fetchAll();
});

function populateFilterCategories() {
    var select = document.getElementById("filter-category");
    select.innerHTML = '<option value="">전체 카테고리</option>';
    var all = EXPENSE_CATEGORIES.concat(INCOME_CATEGORIES);
    all.forEach(function (cat) {
        var opt = document.createElement("option");
        opt.value = cat;
        opt.textContent = cat;
        select.appendChild(opt);
    });
}

function updateCategoryOptions() {
    var type = document.querySelector('input[name="type"]:checked').value;
    var select = document.getElementById("form-category");
    var categories = type === "income" ? INCOME_CATEGORIES : EXPENSE_CATEGORIES;
    select.innerHTML = "";
    categories.forEach(function (cat) {
        var opt = document.createElement("option");
        opt.value = cat;
        opt.textContent = cat;
        select.appendChild(opt);
    });
}

function fetchAll() {
    fetchTransactions();
    fetchSummary();
}

function fetchTransactions() {
    var params = new URLSearchParams();
    if (currentMonth) params.append("month", currentMonth);
    if (currentCategory) params.append("category", currentCategory);
    if (currentType) params.append("type", currentType);

    fetch(API_BASE + "/api/transactions?" + params.toString())
        .then(function (res) {
            return res.json();
        })
        .then(function (data) {
            renderTable(data);
        });
}

function fetchSummary() {
    var params = new URLSearchParams();
    if (currentMonth) params.append("month", currentMonth);

    fetch(API_BASE + "/api/summary?" + params.toString())
        .then(function (res) {
            return res.json();
        })
        .then(function (data) {
            document.getElementById("total-income").textContent = formatCurrency(
                data.total_income
            );
            document.getElementById("total-expense").textContent =
                formatCurrency(data.total_expense);

            var balanceEl = document.getElementById("balance");
            balanceEl.textContent = formatCurrency(data.balance);
            balanceEl.className = data.balance >= 0 ? "positive" : "negative";

            renderCharts(data);
        });
}

function renderTable(transactions) {
    var tbody = document.getElementById("table-body");
    if (transactions.length === 0) {
        tbody.innerHTML =
            '<tr><td colspan="6" style="text-align:center;color:#888;">거래 내역이 없습니다.</td></tr>';
        return;
    }
    tbody.innerHTML = transactions
        .map(function (tx) {
            var typeLabel = tx.type === "income" ? "수입" : "지출";
            var amountClass =
                tx.type === "income" ? "amount-income" : "amount-expense";
            var prefix = tx.type === "income" ? "+" : "-";
            return (
                "<tr>" +
                "<td>" + tx.date + "</td>" +
                "<td>" + typeLabel + "</td>" +
                "<td>" + tx.category + "</td>" +
                "<td>" + (tx.description || "") + "</td>" +
                '<td class="' + amountClass + '">' + prefix + formatCurrency(tx.amount) + "</td>" +
                "<td>" +
                '<button class="btn btn-sm btn-primary" onclick="showModal(' +
                JSON.stringify(tx).replace(/"/g, "&quot;") +
                ')">수정</button> ' +
                '<button class="btn btn-sm btn-danger" onclick="deleteTransaction(' +
                tx.id +
                ')">삭제</button>' +
                "</td>" +
                "</tr>"
            );
        })
        .join("");
}

function renderCharts(summary) {
    if (pieChart) pieChart.destroy();
    if (barChart) barChart.destroy();

    var pieColors = [
        "#2196F3", "#f44336", "#4CAF50", "#FF9800", "#9C27B0",
        "#00BCD4", "#795548", "#607D8B", "#E91E63",
    ];

    var pieCtx = document.getElementById("pie-chart").getContext("2d");
    var categories = summary.by_category || [];
    pieChart = new Chart(pieCtx, {
        type: "pie",
        data: {
            labels: categories.map(function (c) { return c.category; }),
            datasets: [
                {
                    data: categories.map(function (c) { return c.total; }),
                    backgroundColor: pieColors.slice(0, categories.length),
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: "카테고리별 지출" },
            },
        },
    });

    var barCtx = document.getElementById("bar-chart").getContext("2d");
    barChart = new Chart(barCtx, {
        type: "bar",
        data: {
            labels: [summary.month || currentMonth],
            datasets: [
                {
                    label: "수입",
                    data: [summary.total_income],
                    backgroundColor: "#2196F3",
                },
                {
                    label: "지출",
                    data: [summary.total_expense],
                    backgroundColor: "#f44336",
                },
            ],
        },
        options: {
            responsive: true,
            plugins: {
                title: { display: true, text: "월별 수입/지출" },
            },
            scales: {
                y: { beginAtZero: true },
            },
        },
    });
}

function showModal(transaction) {
    var overlay = document.getElementById("modal-overlay");
    var title = document.getElementById("modal-title");
    var formId = document.getElementById("form-id");

    if (transaction) {
        title.textContent = "거래 수정";
        formId.value = transaction.id;
        document.querySelector(
            'input[name="type"][value="' + transaction.type + '"]'
        ).checked = true;
        updateCategoryOptions();
        document.getElementById("form-category").value = transaction.category;
        document.getElementById("form-amount").value = transaction.amount;
        document.getElementById("form-date").value = transaction.date;
        document.getElementById("form-description").value =
            transaction.description || "";
    } else {
        title.textContent = "새 거래 추가";
        formId.value = "";
        document.getElementById("transaction-form").reset();
        document.getElementById("form-date").value = new Date()
            .toISOString()
            .slice(0, 10);
        updateCategoryOptions();
    }

    overlay.classList.add("active");
}

function hideModal() {
    document.getElementById("modal-overlay").classList.remove("active");
}

function saveTransaction() {
    var id = document.getElementById("form-id").value;
    var type = document.querySelector('input[name="type"]:checked').value;
    var category = document.getElementById("form-category").value;
    var amount = parseInt(document.getElementById("form-amount").value, 10);
    var date = document.getElementById("form-date").value;
    var description = document.getElementById("form-description").value;

    var body = {
        type: type,
        category: category,
        amount: amount,
        date: date,
        description: description,
    };

    var url = id
        ? API_BASE + "/api/transactions/" + id
        : API_BASE + "/api/transactions";
    var method = id ? "PATCH" : "POST";

    fetch(url, {
        method: method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
    })
        .then(function (res) {
            return res.json();
        })
        .then(function () {
            hideModal();
            fetchAll();
        });
}

function deleteTransaction(id) {
    if (!confirm("정말 삭제하시겠습니까?")) return;

    fetch(API_BASE + "/api/transactions/" + id, { method: "DELETE" })
        .then(function () {
            fetchAll();
        });
}

function formatCurrency(amount) {
    return "₩" + Number(amount).toLocaleString("ko-KR");
}
