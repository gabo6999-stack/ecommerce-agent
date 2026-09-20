import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";

const STATUS_BADGE: Record<string, { label: string; cls: string }> = {
  SCHEDULED: { label: "Programada", cls: "bg-blue-100 text-blue-700" },
  IN_PROGRESS: { label: "En curso", cls: "bg-red-100 text-red-700" },
  COMPLETED: { label: "Completada", cls: "bg-green-100 text-green-700" },
  CANCELLED: { label: "Cancelada", cls: "bg-gray-100 text-gray-500" },
};

const PROGRAM_LABELS: Record<string, string> = {
  WEIGHT_LOSS: "⚖️ Pérdida de Peso",
  LONGEVITY: "⚡ Péptidos & Longevidad",
  PERFORMANCE: "💪 Rendimiento & Recuperación",
};

export default async function PatientConsultasPage() {
  const session = await auth();

  const patient = await prisma.patient.findFirst({
    where: { user: { email: session!.user!.email! } },
  });

  const consultations = patient
    ? await prisma.consultation.findMany({
        where: { patientId: patient.id },
        include: {
          doctor: { include: { user: true } },
          prescription: true,
        },
        orderBy: { scheduledAt: "desc" },
      })
    : [];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Mis orientaciones</h1>
        <p className="text-gray-500 text-sm mt-1">
          {consultations.length} orientación{consultations.length !== 1 ? "es" : ""} en total
        </p>
      </div>

      <div className="bg-white rounded-xl border border-[var(--border)]">
        {consultations.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-4xl mb-3">📭</p>
            <p className="text-sm">Aún no tienes orientaciones registradas</p>
          </div>
        ) : (
          <div className="divide-y divide-[var(--border)]">
            {consultations.map((c) => {
              const badge = STATUS_BADGE[c.status];
              return (
                <div
                  key={c.id}
                  className="flex items-center justify-between p-5 hover:bg-[var(--muted)] transition-colors"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-[var(--accent-light)] flex items-center justify-center text-[var(--primary)] font-bold text-sm shrink-0">
                      {c.doctor.user.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="font-medium text-gray-900 text-sm">
                        Dr. {c.doctor.user.name}
                      </p>
                      <p className="text-xs text-gray-500 mt-0.5">
                        {PROGRAM_LABELS[c.program]} ·{" "}
                        {new Date(c.scheduledAt).toLocaleString("es-MX", {
                          day: "numeric",
                          month: "long",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </p>
                    </div>
                  </div>

                  <div className="flex items-center gap-3">
                    {c.prescription && (
                      <span className="text-xs text-[var(--primary)] font-medium">
                        💊 Con protocolo
                      </span>
                    )}
                    <span className={`px-3 py-1 rounded-full text-xs font-semibold ${badge.cls}`}>
                      {badge.label}
                    </span>
                    {c.status === "IN_PROGRESS" && c.roomUrl && (
                      <a
                        href={c.roomUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="px-4 py-2 rounded-lg text-xs font-semibold text-white bg-red-500 hover:bg-red-600 transition-colors"
                      >
                        Unirse →
                      </a>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
}

