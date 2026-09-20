import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";

export async function POST(req: NextRequest) {
  const token = req.headers.get("x-init-token");
  if (!token || token !== process.env.ADMIN_INIT_TOKEN) {
    return NextResponse.json({ error: "Forbidden" }, { status: 403 });
  }

  const existing = await prisma.user.findFirst({ where: { role: "ADMIN" } });
  if (existing) {
    return NextResponse.json({ error: "Admin already exists" }, { status: 409 });
  }

  const body = await req.json();
  const { name, email, password } = body;

  if (!name || !email || !password) {
    return NextResponse.json({ error: "name, email y password requeridos" }, { status: 400 });
  }

  const hashed = await bcrypt.hash(password, 12);
  const user = await prisma.user.create({
    data: { name, email, password: hashed, role: "ADMIN" },
    select: { id: true, name: true, email: true, role: true },
  });

  return NextResponse.json({ ok: true, user }, { status: 201 });
}
