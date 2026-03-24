import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = parseInt(params.id);

    const existing = await prisma.actionItem.findUnique({ where: { id } });
    if (!existing) {
      return NextResponse.json({ error: 'Action item not found' }, { status: 404 });
    }

    const item = await prisma.actionItem.update({
      where: { id },
      data: { completed: true },
    });

    return NextResponse.json(item);
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
