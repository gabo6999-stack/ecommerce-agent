import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { stripe } from "@/lib/stripe";

// Crea (o reutiliza) la cuenta conectada de Stripe Connect Express del médico y
// devuelve un link de onboarding para que complete su KYC. El médico = cuenta
// conectada que recibe el split de $1,000 por consulta (ver MODELO §5.A).
// Acceso: ADMIN, o el propio médico.
export async function POST(req: NextRequest) {
  try {
    const session = await auth();
    if (!session?.user?.email) {
      return NextResponse.json({ error: "No autenticado" }, { status: 401 });
    }

    const { doctorId } = await req.json();
    if (!doctorId) {
      return NextResponse.json({ error: "doctorId requerido" }, { status: 400 });
    }

    const caller = await prisma.user.findUnique({
      where: { email: session.user.email },
      include: { doctor: true },
    });
    const isAdmin = caller?.role === "ADMIN";
    const isSelf = caller?.doctor?.id === doctorId;
    if (!isAdmin && !isSelf) {
      return NextResponse.json({ error: "No autorizado" }, { status: 403 });
    }

    const doctor = await prisma.doctor.findUnique({
      where: { id: doctorId },
      include: { user: true },
    });
    if (!doctor) {
      return NextResponse.json({ error: "Médico no encontrado" }, { status: 404 });
    }

    // Crear la cuenta conectada si aún no existe.
    let accountId = doctor.stripeAccountId;
    if (!accountId) {
      const account = await stripe.accounts.create({
        type: "express",
        country: "MX",
        email: doctor.user.email,
        business_type: "individual",
        capabilities: { transfers: { requested: true } },
        // Pre-llenamos el perfil de negocio con los datos de la plataforma para
        // que Stripe NO le pida "sitio web" a cada médico (un médico individual
        // no tiene uno). MCC 8011 = médicos / servicios de salud.
        business_profile: {
          url: process.env.NEXTAUTH_URL ?? "https://ptm-novo-production.up.railway.app",
          product_description: "Teleconsultas médicas a través de la plataforma PTM.",
          mcc: "8011",
        },
        metadata: { doctorId },
      });
      accountId = account.id;
      await prisma.doctor.update({
        where: { id: doctorId },
        data: { stripeAccountId: accountId },
      });
    }

    const baseUrl = process.env.NEXTAUTH_URL ?? "http://localhost:3000";
    const accountLink = await stripe.accountLinks.create({
      account: accountId,
      refresh_url: `${baseUrl}/doctor/pagos?onboarding=refresh`,
      return_url: `${baseUrl}/doctor/pagos?onboarding=done`,
      type: "account_onboarding",
    });

    return NextResponse.json({ url: accountLink.url });
  } catch (err) {
    console.error("Connect onboarding error:", err);
    return NextResponse.json({ error: "Error iniciando el onboarding de pagos" }, { status: 500 });
  }
}
