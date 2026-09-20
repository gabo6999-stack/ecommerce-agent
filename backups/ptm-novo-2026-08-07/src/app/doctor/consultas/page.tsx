import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import Link from "next/link";

const STATUS_LABEL: Record<string, { label: string; color: string }> = {
  SCHEDULED: { label: "Programada", color: "bg-blue-100 text-blue-700" },
  IN_PROGRESS: { label: "En curso", color: "bg-yellow-100 text-yellow-700" },
  COMPLETED: { label: "Completada", color: "bg-green-100 text-green-700" },
  CANCELLED: { label: "Cancelada", color: "bg-red-100 text-red-700" },
};

export default async function ConsultasPage() {
  const session = await auth();

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session!.user!.email! } },
  });

  const consultations = doctor
    ? await prisma.consultation.findMany({
        where: { doctorId: doctor.id },
        include: { patient: { include: { user: true } } },
        orderBy: { scheduledAt: "desc" },
      })
    : [];

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Mis consultas</h1>

      <div className="bg-white rounded-xl border border-[var(--border)]">
        {consultations.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-3xl mb-2">📭</p>
            <p className="text-sm">No tienes consultas registradas aún</p>
          </div>
        ) : (
          <div className="divide-y divide-[var(--border)]">
            {consultations.map((c) => {
              const badge = STATUS_LABEL[c.status];
              return (
                <div key={c.id} className="flex items-center justify-between px-6 py-4 hover:bg-[var(--muted)] transition-colors">
                  <div className="flex items-center gap-4">
                    <div className="w-9 h-9 rounded-full bg-[var(--accent-light)] flex items-center justify-center text-[var(--primary)] font-bold text-sm">
                      {c.patient.user.name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{c.patient.user.name}</p>
                      <p className="text-xs text-gray-400">
                        {c.program === "WEIGHT_LOSS" ? "⚖️ Pérdida de Peso" : c.program === "PERFORMANCE" ? "💪 Rendimiento" : "⚡ Longevidad"} ·{" "}
                        {new Date(c.scheduledAt).toLocaleString("es-MX")}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center gap-3">
                    <span className={`text-xs font-medium px-2.5 py-1 rounded-full ${badge.color}`}>
                      {badge.label}
                    </span>
                    <Link
                      href={`/doctor/consultas/${c.id}`}
                      className="text-sm text-[var(--primary)] hover:underline font-medium"
                    >
                      Ver →
                    </Link>
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
