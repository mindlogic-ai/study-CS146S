import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@/lib/prisma';

export async function PATCH(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = parseInt(params.id);
    const body = await request.json();

    const existing = await prisma.actionItem.findUnique({ where: { id } });
    if (!existing) {
      return NextResponse.json({ error: 'Action item not found' }, { status: 404 });
    }

    const data: Record<string, string | boolean> = {};
    if (body.description !== undefined) data.description = body.description;
    if (body.completed !== undefined) data.completed = body.completed;

    const item = await prisma.actionItem.update({ where: { id }, data });

    return NextResponse.json(item);
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const id = parseInt(params.id);
    const existing = await prisma.actionItem.findUnique({ where: { id } });
    if (!existing) {
      return NextResponse.json({ error: 'Action item not found' }, { status: 404 });
    }

    await prisma.actionItem.delete({ where: { id } });
    return new NextResponse(null, { status: 204 });
  } catch (error) {
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
