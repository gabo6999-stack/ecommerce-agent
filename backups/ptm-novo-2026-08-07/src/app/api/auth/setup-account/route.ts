import { NextRequest, NextResponse } from "next/server";
import { stripe } from "@/lib/stripe";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";

// Lee el email/nombre del paciente desde la sesión de Stripe Checkout (fuente de
// verdad para verificar que quien activa la cuenta es quien pagó).
async function readSession(sessionId: string) {
  const session = await stripe.checkout.sessions.retrieve(sessionId);
  const meta = (session.metadata ?? {}) as Record<string, string>;
  const email =
    session.customer_details?.email ?? session.customer_email ?? meta.patientEmail ?? null;
  const name = meta.patientName ?? session.customer_details?.name ?? "Paciente";
  const phone = meta.patientPhone || session.customer_details?.phone || null;
  const program = meta.program ?? "LONGEVITY";
  const paid = session.payment_status === "paid";
  return { email, name, phone, program, paid };
}

export async function GET(req: NextRequest) {
  const sessionId = req.nextUrl.searchParams.get("session_id");
  if (!sessionId) {
    return NextResponse.json({ error: "session_id requerido" }, { status: 400 });
  }

  try {
    const { email, name } = await readSession(sessionId);
    if (!email) {
      return NextResponse.json({ error: "No se encontró email en el pago" }, { status: 404 });
    }

    const user = await prisma.user.findUnique({ where: { email } });
    const needsSetup = !user || (await bcrypt.compare("NEEDS_ACTIVATION", user.password));

    return NextResponse.json({ email, name, needsSetup });
  } catch {
    return NextResponse.json({ error: "No se pudo verificar el pago" }, { status: 400 });
  }
}

export async function POST(req: NextRequest) {
  try {
    const { sessionId, email, password } = await req.json();

    if (!sessionId || !email || !password) {
      return NextResponse.json({ error: "Datos incompletos" }, { status: 400 });
    }
    if (password.length < 8) {
      return NextResponse.json(
        { error: "La contraseña debe tener al menos 8 caracteres" },
        { status: 400 }
      );
    }

    const { email: paidEmail, name, phone, program, paid } = await readSession(sessionId);

    if (!paid) {
      return NextResponse.json({ error: "El pago no está confirmado" }, { status: 400 });
    }
    if ((paidEmail ?? "").toLowerCase() !== email.toLowerCase()) {
      return NextResponse.json({ error: "El email no coincide con el pago" }, { status: 400 });
    }

    const hashed = await bcrypt.hash(password, 10);

    const user = await prisma.user.upsert({
      where: { email },
      update: { password: hashed },
      create: { email, name, phone, password: hashed, role: "PATIENT" },
    });

    const existingPatient = await prisma.patient.findUnique({ where: { userId: user.id } });
    if (!existingPatient) {
      await prisma.patient.create({
        data: {
          userId: user.id,
          program:
            program === "WEIGHT_LOSS"
              ? "WEIGHT_LOSS"
              : program === "PERFORMANCE"
              ? "PERFORMANCE"
              : "LONGEVITY",
        },
      });
    }

    return NextResponse.json({ success: true });
  } catch (err) {
    console.error("Setup account error:", err);
    return NextResponse.json({ error: "Error al crear la cuenta" }, { status: 500 });
  }
}
