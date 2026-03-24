const { PrismaClient } = require("@prisma/client");
const prisma = new PrismaClient();

const SEED_DATA = [
  { type: "expense", category: "식비", amount: 15000, description: "점심 김치찌개", date: new Date("2026-03-01") },
  { type: "expense", category: "교통", amount: 3000, description: "버스비", date: new Date("2026-03-02") },
  { type: "expense", category: "쇼핑", amount: 45000, description: "운동화", date: new Date("2026-03-05") },
  { type: "income", category: "급여", amount: 3500000, description: "3월 급여", date: new Date("2026-03-10") },
  { type: "expense", category: "여가", amount: 12000, description: "영화 관람", date: new Date("2026-03-12") },
  { type: "expense", category: "주거", amount: 500000, description: "월세", date: new Date("2026-03-15") },
  { type: "expense", category: "식비", amount: 8000, description: "저녁 국밥", date: new Date("2026-03-18") },
  { type: "income", category: "용돈", amount: 100000, description: "부모님 용돈", date: new Date("2026-03-20") },
  { type: "expense", category: "교통", amount: 55000, description: "교통카드 충전", date: new Date("2026-02-05") },
  { type: "expense", category: "식비", amount: 25000, description: "회식", date: new Date("2026-02-10") },
  { type: "income", category: "급여", amount: 3500000, description: "2월 급여", date: new Date("2026-02-10") },
  { type: "expense", category: "쇼핑", amount: 32000, description: "책 구매", date: new Date("2026-02-15") },
  { type: "expense", category: "여가", amount: 20000, description: "카페", date: new Date("2026-02-20") },
];

async function main() {
  await prisma.transaction.deleteMany();
  for (const item of SEED_DATA) {
    await prisma.transaction.create({ data: item });
  }
  console.log(`Seeded ${SEED_DATA.length} transactions`);
}

main()
  .catch(console.error)
  .finally(() => prisma.$disconnect());
