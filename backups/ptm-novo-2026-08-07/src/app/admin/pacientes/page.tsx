import { prisma } from "@/lib/prisma";
import Link from "next/link";

const PROGRAM_LABELS: Record<string, string> = {
  WEIGHT_LOSS: "⚖️ Pérdida de Peso",
  LONGEVITY: "⚡ Longevidad",
  PERFORMANCE: "💪 Rendimiento",
};

export default async function AdminPacientesPage() {
  const patients = await prisma.patient.findMany({
    include: {
      user: true,
      consultations: {
        orderBy: { scheduledAt: "desc" },
        take: 1,
      },
      _count: { select: { consultations: true } },
    },
    orderBy: { createdAt: "desc" },
  });

  return (
    <div>
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Pacientes</h1>
          <p className="text-gray-500 text-sm mt-1">{patients.length} registrados</p>
        </div>
      </div>

      <div className="bg-white rounded-xl border border-[var(--border)] overflow-hidden">
        {patients.length === 0 ? (
          <div className="text-center py-16 text-gray-400">
            <p className="text-4xl mb-3">👥</p>
            <p className="text-sm">Sin pacientes registrados aún</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] bg-[var(--muted)]">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Paciente
                </th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Programa
                </th>
                <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Consultas
                </th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Última consulta
                </th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Registrado
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {patients.map((p) => {
                const lastConsultation = p.consultations[0];
                return (
                  <tr key={p.id} className="hover:bg-[var(--muted)] transition-colors">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-[var(--accent-light)] flex items-center justify-center text-[var(--primary)] font-bold text-xs shrink-0">
                          {p.user.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">{p.user.name}</p>
                          <p className="text-xs text-gray-400">{p.user.email}</p>
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-gray-600">
                      {p.program ? PROGRAM_LABELS[p.program] : <span className="text-gray-400">—</span>}
                    </td>
                    <td className="px-5 py-4 text-center">
                      <span className="inline-flex items-center justify-center w-7 h-7 rounded-full bg-[var(--muted)] text-xs font-bold text-gray-700">
                        {p._count.consultations}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-gray-500 text-xs">
                      {lastConsultation
                        ? new Date(lastConsultation.scheduledAt).toLocaleDateString("es-MX", {
                            day: "numeric",
                            month: "short",
                            year: "numeric",
                          })
                        : "—"}
                    </td>
                    <td className="px-5 py-4 text-gray-400 text-xs">
                      {new Date(p.createdAt).toLocaleDateString("es-MX", {
                        day: "numeric",
                        month: "short",
                        year: "numeric",
                      })}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
