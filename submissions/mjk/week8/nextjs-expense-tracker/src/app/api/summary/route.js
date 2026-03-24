import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  let month = searchParams.get("month");

  if (!month) {
    const now = new Date();
    month = `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, "0")}`;
  }

  const [year, m] = month.split("-");
  const start = new Date(parseInt(year), parseInt(m) - 1, 1);
  const end = new Date(parseInt(year), parseInt(m), 1);

  const transactions = await prisma.transaction.findMany({
    where: { date: { gte: start, lt: end } },
  });

  let total_income = 0;
  let total_expense = 0;
  const categoryMap = {};

  for (const tx of transactions) {
    if (tx.type === "income") {
      total_income += tx.amount;
    } else {
      total_expense += tx.amount;
    }
    categoryMap[tx.category] = (categoryMap[tx.category] || 0) + tx.amount;
  }

  const by_category = Object.entries(categoryMap)
    .map(([category, total]) => ({ category, total }))
    .sort((a, b) => b.total - a.total);

  return NextResponse.json({
    month,
    total_income,
    total_expense,
    balance: total_income - total_expense,
    by_category,
  });
}
