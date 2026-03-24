import { NextResponse } from "next/server";

export async function GET() {
  return NextResponse.json({
    expense: ["식비", "교통", "쇼핑", "주거", "여가", "기타"],
    income: ["급여", "용돈", "기타수입"],
  });
}
