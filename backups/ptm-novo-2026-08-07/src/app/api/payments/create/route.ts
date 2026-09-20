import { NextRequest, NextResponse } from "next/server";
import { stripe, CONSULTA_TOTAL_CENTAVOS } from "@/lib/stripe";

export async function POST(req: NextRequest) {
  try {
    const { name, email, phone, program, privacyAcceptedAt } = await req.json();

    if (!name || !email || !program) {
      return NextResponse.json({ error: "Datos incompletos" }, { status: 400 });
    }
    if (!privacyAcceptedAt) {
      return NextResponse.json({ error: "Debes aceptar el Aviso de Privacidad" }, { status: 400 });
    }

    const programLabel =
      program === "WEIGHT_LOSS" ? "Pérdida de Peso" :
      program === "PERFORMANCE" ? "Rendimiento & Recuperación" :
      "Péptidos & Longevidad";

    const baseUrl = process.env.NEXTAUTH_URL ?? "http://localhost:3000";

    // metadata que el webhook y la activación de cuenta leerán.
    const metadata = {
      program,
      patientName: name,
      patientEmail: email,
      patientPhone: phone ?? "",
      privacyAcceptedAt,
    };

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      customer_email: email,
      line_items: [
        {
          quantity: 1,
          price_data: {
            currency: "mxn",
            unit_amount: CONSULTA_TOTAL_CENTAVOS, // $1,500 — solo la consulta
            product_data: {
              name: `Orientación médica — ${programLabel}`,
              description:
                "Orientación médica 30 min con médico especialista. Protocolo de tratamiento incluido.",
            },
          },
        },
      ],
      // Sin transfer_data / on_behalf_of: los fondos quedan RETENIDOS en la
      // plataforma. El split al médico ($1,000) se transfiere al COMPLETAR la
      // consulta (separate charges & transfers).
      payment_intent_data: { metadata },
      metadata,
      success_url: `${baseUrl}/pago-exitoso?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${baseUrl}/pago-fallido`,
    });

    return NextResponse.json({ url: session.url });
  } catch (err) {
    console.error("Stripe checkout session error:", err);
    return NextResponse.json({ error: "Error creando la sesión de pago" }, { status: 500 });
  }
}
