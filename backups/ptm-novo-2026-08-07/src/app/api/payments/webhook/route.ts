import { NextRequest, NextResponse } from "next/server";
import Stripe from "stripe";
import { stripe } from "@/lib/stripe";
import { prisma } from "@/lib/prisma";
import bcrypt from "bcryptjs";

// Stripe exige verificar la firma con el body CRUDO. En route handlers se obtiene
// con req.text() (no req.json()).
export async function POST(req: NextRequest) {
  const rawBody = await req.text();
  const signature = req.headers.get("stripe-signature");
  const webhookSecret = process.env.STRIPE_WEBHOOK_SECRET;

  if (!signature || !webhookSecret) {
    return NextResponse.json({ error: "Webhook no configurado" }, { status: 400 });
  }

  let event: Stripe.Event;
  try {
    event = stripe.webhooks.constructEvent(rawBody, signature, webhookSecret);
  } catch (err) {
    console.error("Stripe webhook signature error:", err);
    return NextResponse.json({ error: "Firma inválida" }, { status: 400 });
  }

  try {
    if (event.type === "checkout.session.completed") {
      const session = event.data.object as Stripe.Checkout.Session;

      // Solo procesar si realmente se pagó.
      if (session.payment_status === "paid") {
        const meta = (session.metadata ?? {}) as Record<string, string>;
        const email =
          session.customer_email ?? session.customer_details?.email ?? meta.patientEmail ?? null;
        const name = meta.patientName ?? session.customer_details?.name ?? "Paciente";
        const phone = meta.patientPhone || session.customer_details?.phone || null;
        const program = meta.program ?? "LONGEVITY";
        const privacyAcceptedAt = meta.privacyAcceptedAt
          ? new Date(meta.privacyAcceptedAt)
          : new Date();
        const paymentIntentId =
          typeof session.payment_intent === "string"
            ? session.payment_intent
            : session.payment_intent?.id ?? null;

        if (email) {
          let user = await prisma.user.findUnique({ where: { email } });
          if (!user) {
            const tempPassword = await bcrypt.hash("NEEDS_ACTIVATION", 10);
            user = await prisma.user.create({
              data: { email, name, phone, password: tempPassword, role: "PATIENT" },
            });
          }

          let patient = await prisma.patient.findUnique({ where: { userId: user.id } });
          if (!patient) {
            patient = await prisma.patient.create({
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

          // Dedupe por el PaymentIntent de Stripe.
          const existing = paymentIntentId
            ? await prisma.payment.findFirst({ where: { stripePaymentIntentId: paymentIntentId } })
            : null;

          if (!existing) {
            await prisma.payment.create({
              data: {
                patientId: patient.id,
                status: "APPROVED",
                stripePaymentIntentId: paymentIntentId,
                // Split fijo: $1,000 médico + $500 PTM. Payout RETENIDO (HELD)
                // hasta completar la consulta. Ver MODELO_MONETIZACION_PTM.md §5/§5.A.
                amount: 1500,
                doctorAmount: 1000,
                platformFee: 500,
                payoutStatus: "HELD",
                currency: "MXN",
                privacyAcceptedAt,
              },
            });
          }
        }
      }
    }

    return NextResponse.json({ received: true });
  } catch (err) {
    console.error("Stripe webhook handling error:", err);
    // 500 para que Stripe reintente la entrega.
    return NextResponse.json({ error: "Error procesando el evento" }, { status: 500 });
  }
}
