import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import Link from "next/link";

const PROGRAM_LABELS = {
  WEIGHT_LOSS: { label: "Pérdida de Peso", icon: "⚖️", color: "bg-blue-50 text-blue-700" },
  LONGEVITY: { label: "Péptidos & Longevidad", icon: "⚡", color: "bg-purple-50 text-purple-700" },
  PERFORMANCE: { label: "Rendimiento & Recuperación", icon: "💪", color: "bg-green-50 text-green-700" },
};

function formatDateTime(date: Date) {
  return date.toLocaleString("es-MX", {
    weekday: "long",
    day: "numeric",
    month: "long",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export default async function PatientDashboard() {
  const session = await auth();

  const patient = await prisma.patient.findFirst({
    where: { user: { email: session!.user!.email! } },
    include: {
      user: true,
      consultations: {
        where: { status: { in: ["SCHEDULED", "IN_PROGRESS"] } },
        orderBy: { scheduledAt: "asc" },
        take: 1,
        include: { doctor: { include: { user: true } } },
      },
      prescriptions: {
        orderBy: { createdAt: "desc" },
        take: 2,
      },
      progressLogs: {
        orderBy: { createdAt: "desc" },
        take: 1,
      },
    },
  });

  const nextConsultation = patient?.consultations[0];
  const lastPrescription = patient?.prescriptions[0];
  const lastLog = patient?.progressLogs[0];
  const program = patient?.program;
  const programInfo = program ? PROGRAM_LABELS[program] : null;

  const completedCount = patient
    ? await prisma.consultation.count({
        where: { patientId: patient.id, status: "COMPLETED" },
      })
    : 0;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">
          Hola, {session?.user?.name?.split(" ")[0]} 👋
        </h1>
        {programInfo && (
          <span
            className={`inline-flex items-center gap-1.5 mt-2 px-3 py-1 rounded-full text-xs font-semibold ${programInfo.color}`}
          >
            {programInfo.icon} Programa {programInfo.label}
          </span>
        )}
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        {[
          { label: "Orientaciones completadas", value: completedCount, icon: "✅", color: "bg-green-50 text-green-600" },
          { label: "Protocolos totales", value: patient?.prescriptions.length ?? 0, icon: "💊", color: "bg-blue-50 text-blue-600" },
          {
            label: "Último peso registrado",
            value: lastLog?.weight ? `${lastLog.weight} kg` : "—",
            icon: "📊",
            color: "bg-purple-50 text-purple-600",
          },
        ].map((stat) => (
          <div key={stat.label} className="bg-white rounded-xl border border-[var(--border)] p-5">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl mb-3 ${stat.color}`}>
              {stat.icon}
            </div>
            <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
            <p className="text-sm text-gray-500 mt-0.5">{stat.label}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-2 gap-5">
        {/* Next consultation */}
        <div className="bg-white rounded-xl border border-[var(--border)] p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900">Próxima orientación médica</h2>
            <Link href="/patient/consultas" className="text-sm text-[var(--primary)] hover:underline">
              Ver todas →
            </Link>
          </div>

          {!nextConsultation ? (
            <div className="text-center py-8 text-gray-400">
              <p className="text-3xl mb-2">📭</p>
              <p className="text-sm mb-4">Sin orientaciones programadas</p>
              <Link
                href="/"
                className="inline-block px-4 py-2 rounded-lg text-sm font-semibold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
              >
                Agendar orientación médica
              </Link>
            </div>
          ) : (
            <div className="p-4 rounded-xl bg-[var(--muted)] flex items-start gap-3">
              <div className="w-10 h-10 rounded-full bg-[var(--accent-light)] flex items-center justify-center text-[var(--primary)] font-bold text-sm shrink-0">
                {nextConsultation.doctor.user.name.charAt(0).toUpperCase()}
              </div>
              <div>
                <p className="font-medium text-gray-900 text-sm">
                  Dr. {nextConsultation.doctor.user.name}
                </p>
                <p className="text-xs text-gray-500 mt-0.5 capitalize">
                  {formatDateTime(nextConsultation.scheduledAt)}
                </p>
                {nextConsultation.status === "IN_PROGRESS" && nextConsultation.roomUrl && (
                  <a
                    href={nextConsultation.roomUrl}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="mt-2 inline-block px-3 py-1.5 rounded-lg text-xs font-semibold text-white bg-red-500 hover:bg-red-600 transition-colors"
                  >
                    🔴 Unirse ahora
                  </a>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Last prescription */}
        <div className="bg-white rounded-xl border border-[var(--border)] p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900">Último protocolo</h2>
            <Link href="/patient/Protocolos" className="text-sm text-[var(--primary)] hover:underline">
              Ver todas →
            </Link>
          </div>

          {!lastPrescription ? (
            <div className="text-center py-8 text-gray-400">
              <p className="text-3xl mb-2">💊</p>
              <p className="text-sm">Se genera tras tu primera orientación médica</p>
            </div>
          ) : (
            <div className="space-y-2">
              {(lastPrescription.peptides as { name: string; dose: string }[]).slice(0, 3).map((p, i) => (
                <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-[var(--muted)]">
                  <span className="text-sm font-medium text-gray-800">{p.name}</span>
                  <span className="text-xs text-gray-500">{p.dose}</span>
                </div>
              ))}
              <p className="text-xs text-gray-400 pt-1">
                Emitida {new Date(lastPrescription.createdAt).toLocaleDateString("es-MX")}
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

