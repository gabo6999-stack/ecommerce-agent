import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { stripe } from "@/lib/stripe";
import OnboardingButton from "@/components/doctor/OnboardingButton";

type Status = "not_started" | "pending" | "active" | "unknown";

export default async function DoctorPagosPage({
  searchParams,
}: {
  searchParams: Promise<{ onboarding?: string }>;
}) {
  const { onboarding } = await searchParams;
  const session = await auth();

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session!.user!.email! } },
  });

  if (!doctor) {
    return (
      <div className="max-w-xl">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Pagos</h1>
        <p className="text-gray-500 text-sm">
          Esta sección es para médicos. Tu cuenta no tiene un perfil de médico asociado.
        </p>
      </div>
    );
  }

  // Determinar el estado de la cuenta conectada.
  let status: Status = "not_started";
  if (doctor.stripeAccountId) {
    try {
      const account = await stripe.accounts.retrieve(doctor.stripeAccountId);
      status = account.payouts_enabled ? "active" : "pending";
    } catch {
      status = "unknown";
    }
  }

  const STATUS_UI: Record<Status, { badge: string; color: string; title: string; desc: string; cta?: string }> = {
    not_started: {
      badge: "⚠️ Pendiente",
      color: "bg-yellow-100 text-yellow-700",
      title: "Configura tus pagos",
      desc: "Para recibir tus honorarios ($1,000 MXN por consulta completada) necesitas conectar tu cuenta bancaria con Stripe. Es un proceso seguro de una sola vez.",
      cta: "Configurar pagos con Stripe →",
    },
    pending: {
      badge: "⏳ Incompleto",
      color: "bg-orange-100 text-orange-700",
      title: "Termina de configurar tus pagos",
      desc: "Tu registro con Stripe quedó incompleto. Continúa para poder recibir tus honorarios.",
      cta: "Continuar configuración →",
    },
    active: {
      badge: "✅ Activo",
      color: "bg-green-100 text-green-700",
      title: "Tus pagos están activos",
      desc: "Tu cuenta está conectada. Recibirás $1,000 MXN por cada consulta que completes, liberados automáticamente.",
      cta: "Actualizar datos de pago →",
    },
    unknown: {
      badge: "❓ No verificable",
      color: "bg-gray-100 text-gray-600",
      title: "No pudimos verificar tu estado de pagos",
      desc: "Inténtalo de nuevo en un momento. Si el problema persiste, contacta al administrador.",
      cta: "Reintentar configuración →",
    },
  };

  const ui = STATUS_UI[status];

  return (
    <div className="max-w-xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Pagos</h1>
      <p className="text-gray-500 text-sm mb-6">Cómo recibes tus honorarios por consulta.</p>

      {onboarding === "done" && status !== "active" && (
        <div className="mb-5 bg-blue-50 border border-blue-200 text-blue-700 text-sm rounded-xl px-4 py-3">
          Regresaste de Stripe. Si tu estado sigue como pendiente, es posible que falte
          confirmar algún dato — vuelve a intentar.
        </div>
      )}

      <div className="bg-white rounded-2xl border border-[var(--border)] shadow-sm p-6">
        <div className="flex items-start justify-between gap-4 mb-3">
          <div className="w-12 h-12 rounded-xl bg-[var(--primary)]/10 flex items-center justify-center text-2xl">
            💳
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${ui.color}`}>
            {ui.badge}
          </span>
        </div>

        <h2 className="text-lg font-bold text-gray-900 mb-1">{ui.title}</h2>
        <p className="text-sm text-gray-500 mb-5 leading-relaxed">{ui.desc}</p>

        {ui.cta && <OnboardingButton doctorId={doctor.id} label={ui.cta} />}

        <p className="text-xs text-gray-400 mt-4">
          Procesado de forma segura por Stripe. PTM no almacena tus datos bancarios.
        </p>
      </div>
    </div>
  );
}
