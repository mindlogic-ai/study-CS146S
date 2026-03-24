import { NextResponse } from "next/server";
import prisma from "@/lib/prisma";

export async function GET(request) {
  const { searchParams } = new URL(request.url);
  const month = searchParams.get("month");
  const category = searchParams.get("category");
  const type = searchParams.get("type");

  const where = {};
  if (month) {
    const [year, m] = month.split("-");
    const start = new Date(parseInt(year), parseInt(m) - 1, 1);
    const end = new Date(parseInt(year), parseInt(m), 1);
    where.date = { gte: start, lt: end };
  }
  if (category) where.category = category;
  if (type) where.type = type;

  const transactions = await prisma.transaction.findMany({
    where,
    orderBy: [{ date: "desc" }, { createdAt: "desc" }],
  });
  return NextResponse.json(transactions);
}

export async function POST(request) {
  const body = await request.json();
  const tx = await prisma.transaction.create({
    data: {
      type: body.type,
      category: body.category,
      amount: body.amount,
      description: body.description || "",
      date: new Date(body.date),
    },
  });
  return NextResponse.json({ id: tx.id }, { status: 201 });
}
