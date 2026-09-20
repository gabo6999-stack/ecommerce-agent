import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";

export async function POST(
  _req: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  const endDate = new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString();

  const res = await fetch("https://api.whereby.dev/v1/meetings", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${process.env.WHEREBY_API_KEY}`,
    },
    body: JSON.stringify({ endDate }),
  });

  const meeting = await res.json();
  const roomUrl = meeting.roomUrl;

  await prisma.consultation.update({
    where: { id },
    data: { status: "IN_PROGRESS", roomUrl },
  });

  return NextResponse.redirect(new URL(`/doctor/consultas/${id}`, _req.url));
}
