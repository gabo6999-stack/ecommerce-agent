import { NextRequest, NextResponse } from "next/server";
import { prisma } from "@/lib/prisma";
import { stripe, MEDICO_CENTAVOS } from "@/lib/stripe";

export async function POST(req: NextRequest) {
  try {
    const { consultationId, peptides, instructions, notes } = await req.json();

    const consultation = await prisma.consultation.findUnique({
      where: { id: consultationId },
      include: { patient: true },
    });

    if (!consultation) {
      return NextResponse.json({ error: "Consulta no encontrada" }, { status: 404 });
    }

    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 30);

    // Al completar la consulta: se crea la receta (el paciente la recibe) y se
    // marca COMPLETED. PTM NO envía la receta a ninguna farmacia ni rastrea su
    // surtido — neutralidad de dispensación (MODELO_MONETIZACION_PTM.md §3.1).
    await prisma.$transaction([
      prisma.prescription.create({
        data: {
          patientId: consultation.patientId,
          doctorId: consultation.doctorId,
          consultationId,
          peptides,
          instructions,
          expiresAt,
        },
      }),
      prisma.consultation.update({
        where: { id: consultationId },
        data: { status: "COMPLETED", notes },
      }),
    ]);

    // Liberar el split retenido: transfer de $1,000 al médico que atendió
    // (separate charges & transfers). Si algo falla, el pago queda HELD y la
    // consulta igual queda COMPLETED — el payout se puede reintentar.
    await releasePayout(consultation.patientId, consultation.doctorId, consultationId);

    return NextResponse.json({ ok: true });
  } catch (err) {
    console.error("Complete consultation error:", err);
    return NextResponse.json({ error: "Error completando consulta" }, { status: 500 });
  }
}

async function releasePayout(patientId: string, doctorId: string, consultationId: string) {
  // El Payment se crea en el checkout sin consultationId; se localiza por el
  // paciente el pago retenido más antiguo (1 pago = 1 consulta).
  const payment = await prisma.payment.findFirst({
    where: { patientId, payoutStatus: "HELD", status: "APPROVED" },
    orderBy: { createdAt: "asc" },
  });
  if (!payment) {
    console.warn("releasePayout: sin pago HELD para el paciente", patientId);
    return;
  }

  const doctor = await prisma.doctor.findUnique({ where: { id: doctorId } });
  if (!doctor?.stripeAccountId) {
    console.warn("releasePayout: el médico no tiene cuenta Connect; payout sigue HELD", doctorId);
    return;
  }

  try {
    const transfer = await stripe.transfers.create({
      amount: MEDICO_CENTAVOS, // $1,000 al médico; los $500 quedan en la plataforma
      currency: "mxn",
      destination: doctor.stripeAccountId,
      transfer_group: consultationId,
      metadata: { consultationId, paymentId: payment.id, doctorId },
    });

    await prisma.payment.update({
      where: { id: payment.id },
      data: {
        consultationId,
        payoutStatus: "RELEASED",
        payoutReleasedAt: new Date(),
        stripeTransferId: transfer.id,
      },
    });
  } catch (err) {
    console.error("releasePayout: transfer falló; payout sigue HELD", err);
  }
}
