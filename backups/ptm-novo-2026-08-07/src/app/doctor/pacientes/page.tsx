import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import Link from "next/link";

const PROGRAM_LABEL: Record<string, { label: string; icon: string; color: string }> = {
  WEIGHT_LOSS: { label: "Pérdida de Peso", icon: "⚖️", color: "bg-orange-100 text-orange-700" },
  LONGEVIDAD: { label: "Longevidad", icon: "⚡", color: "bg-purple-100 text-purple-700" },
  LONGEVITY: { label: "Longevidad", icon: "⚡", color: "bg-purple-100 text-purple-700" },
  PERFORMANCE: { label: "Rendimiento", icon: "💪", color: "bg-green-100 text-green-700" },
};

const STATUS_LABEL: Record<string, { label: string; color: string }> = {
  SCHEDULED: { label: "Programada", color: "bg-blue-100 text-blue-700" },
  IN_PROGRESS: { label: "En curso", color: "bg-yellow-100 text-yellow-700" },
  COMPLETED: { label: "Completada", color: "bg-green-100 text-green-700" },
  CANCELLED: { label: "Cancelada", color: "bg-gray-100 text-gray-500" },
};

function formatDate(date: Date) {
  return date.toLocaleDateString("es-MX", { day: "numeric", month: "short", year: "numeric" });
}

export default async function PacientesPage() {
  const session = await auth();

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session!.user!.email! } },
  });

  const patients = doctor
    ? await prisma.patient.findMany({
        where: { consultations: { some: { doctorId: doctor.id } } },
        include: {
          user: true,
          consultations: {
            where: { doctorId: doctor.id },
            orderBy: { scheduledAt: "desc" },
            take: 1,
          },
          _count: {
            select: { consultations: { where: { doctorId: doctor.id } } },
          },
        },
        orderBy: { createdAt: "desc" },
      })
    : [];

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Mis pacientes</h1>
          <p className="text-sm text-gray-500 mt-0.5">{patients.length} paciente{patients.length !== 1 ? "s" : ""} registrado{patients.length !== 1 ? "s" : ""}</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-[var(--border)]">
        {patients.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-3xl mb-2">👥</p>
            <p className="text-sm">Aún no tienes pacientes asignados</p>
            <p className="text-xs mt-1">Aparecerán aquí cuando tengas consultas programadas</p>
          </div>
        ) : (
          <>
            {/* Header */}
            <div className="grid grid-cols-12 gap-4 px-6 py-3 border-b border-[var(--border)] bg-[var(--muted)] rounded-t-xl">
              <span className="col-span-4 text-xs font-semibold text-gray-500 uppercase tracking-wide">Paciente</span>
              <span className="col-span-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Programa</span>
              <span className="col-span-2 text-xs font-semibold text-gray-500 uppercase tracking-wide text-center">Consultas</span>
              <span className="col-span-2 text-xs font-semibold text-gray-500 uppercase tracking-wide">Última consulta</span>
              <span className="col-span-1 text-xs font-semibold text-gray-500 uppercase tracking-wide">Estado</span>
              <span className="col-span-1" />
            </div>

            {/* Rows */}
            <div className="divide-y divide-[var(--border)]">
              {patients.map((p) => {
                const lastConsult = p.consultations[0];
                const prog = p.program ? PROGRAM_LABEL[p.program] : null;
                const badge = lastConsult ? STATUS_LABEL[lastConsult.status] : null;

                return (
                  <div
                    key={p.id}
                    className="grid grid-cols-12 gap-4 items-center px-6 py-4 hover:bg-[var(--muted)] transition-colors"
                  >
                    {/* Paciente */}
                    <div className="col-span-4 flex items-center gap-3">
                      <div className="w-9 h-9 rounded-full bg-[var(--accent-light)] flex items-center justify-center text-[var(--primary)] font-bold text-sm flex-shrink-0">
                        {p.user.name.charAt(0).toUpperCase()}
                      </div>
                      <div className="min-w-0">
                        <p className="text-sm font-medium text-gray-900 truncate">{p.user.name}</p>
                        <p className="text-xs text-gray-400 truncate">{p.user.email}</p>
                      </div>
                    </div>

                    {/* Programa */}
                    <div className="col-span-2">
                      {prog ? (
                        <span className={`inline-flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full ${prog.color}`}>
                          {prog.icon} {prog.label}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">—</span>
                      )}
                    </div>

                    {/* Número de consultas */}
                    <div className="col-span-2 text-center">
                      <span className="text-sm font-semibold text-gray-900">{p._count.consultations}</span>
                    </div>

                    {/* Última consulta */}
                    <div className="col-span-2">
                      {lastConsult ? (
                        <p className="text-xs text-gray-600">{formatDate(lastConsult.scheduledAt)}</p>
                      ) : (
                        <span className="text-xs text-gray-400">—</span>
                      )}
                    </div>

                    {/* Estado */}
                    <div className="col-span-1">
                      {badge ? (
                        <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${badge.color}`}>
                          {badge.label}
                        </span>
                      ) : (
                        <span className="text-xs text-gray-400">—</span>
                      )}
                    </div>

                    {/* Acción */}
                    <div className="col-span-1 text-right">
                      {lastConsult && (
                        <Link
                          href={`/doctor/consultas/${lastConsult.id}`}
                          className="text-sm text-[var(--primary)] hover:underline font-medium"
                        >
                          Ver →
                        </Link>
                      )}
                    </div>
                  </div>
                );
              })}
            </div>
          </>
        )}
      </div>
    </div>
  );
}
