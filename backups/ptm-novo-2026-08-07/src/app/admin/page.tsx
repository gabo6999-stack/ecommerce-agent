import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import Link from "next/link";

function formatDate(date: Date) {
  return date.toLocaleDateString("es-MX", { day: "numeric", month: "short", year: "numeric" });
}

function formatDateTime(date: Date) {
  return date.toLocaleString("es-MX", {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  });
}

const STATUS_BADGE: Record<string, { label: string; cls: string }> = {
  SCHEDULED: { label: "Programada", cls: "bg-blue-100 text-blue-700" },
  IN_PROGRESS: { label: "En curso", cls: "bg-yellow-100 text-yellow-700" },
  COMPLETED: { label: "Completada", cls: "bg-green-100 text-green-700" },
  CANCELLED: { label: "Cancelada", cls: "bg-gray-100 text-gray-500" },
};

export default async function AdminDashboard() {
  const session = await auth();

  const monthStart = new Date();
  monthStart.setDate(1);
  monthStart.setHours(0, 0, 0, 0);

  const [
    totalPatients,
    totalDoctors,
    completedThisMonth,
    completedTotal,
    pendingConsultations,
    recentPayments,
  ] = await Promise.all([
    prisma.patient.count(),
    prisma.doctor.count({ where: { isActive: true } }),
    prisma.consultation.count({
      where: { status: "COMPLETED", scheduledAt: { gte: monthStart } },
    }),
    prisma.consultation.count({ where: { status: "COMPLETED" } }),
    prisma.consultation.findMany({
      where: { status: { in: ["SCHEDULED", "IN_PROGRESS"] } },
      include: {
        patient: { include: { user: true } },
        doctor: { include: { user: true } },
      },
      orderBy: { scheduledAt: "asc" },
      take: 5,
    }),
    prisma.payment.findMany({
      where: { status: "APPROVED" },
      include: { patient: { include: { user: true } } },
      orderBy: { createdAt: "desc" },
      take: 5,
    }),
  ]);

  // Modelo limpio: comisión FIJA de $500 MXN para PTM por consulta completada.
  const ingresosMes = completedThisMonth * 500;
  const ingresosTotal = completedTotal * 500;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500 text-sm mt-1">
          {formatDate(new Date())} · Vista general de Peptide Technologies México
        </p>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-4 gap-5 mb-8">
        {[
          { label: "Pacientes registrados", value: totalPatients, icon: "👥", color: "bg-blue-50 text-blue-600" },
          { label: "Médicos activos", value: totalDoctors, icon: "👨‍⚕️", color: "bg-purple-50 text-purple-600" },
          { label: "Orientaciones este mes", value: completedThisMonth, icon: "📅", color: "bg-green-50 text-green-600" },
          {
            label: "Ingresos este mes",
            value: `$${ingresosMes.toLocaleString()} MXN`,
            icon: "💰",
            color: "bg-yellow-50 text-yellow-600",
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

      {/* Revenue split card */}
      <div className="bg-white rounded-xl border border-[var(--border)] p-6 mb-5">
        <h2 className="font-bold text-gray-900 mb-4">Resumen financiero global</h2>
        <div className="grid grid-cols-3 gap-4">
          <div className="bg-[var(--muted)] rounded-lg p-4">
            <p className="text-xs text-gray-500 mb-1">Total cobrado (pagos aprobados)</p>
            <p className="text-xl font-bold text-gray-900">${(completedTotal * 1500).toLocaleString()} MXN</p>
          </div>
          <div className="bg-green-50 rounded-lg p-4">
            <p className="text-xs text-green-600 mb-1">Peptide Technologies México ($500/orientación)</p>
            <p className="text-xl font-bold text-green-700">${ingresosTotal.toLocaleString()} MXN</p>
          </div>
          <div className="bg-blue-50 rounded-lg p-4">
            <p className="text-xs text-blue-600 mb-1">Pagado a médicos ($1,000/orientación)</p>
            <p className="text-xl font-bold text-blue-700">${(completedTotal * 1000).toLocaleString()} MXN</p>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-5">
        {/* Pending consultations */}
        <div className="bg-white rounded-xl border border-[var(--border)] p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900">Orientaciones pendientes</h2>
            <span className="text-xs text-gray-400">{pendingConsultations.length} próximas</span>
          </div>

          {pendingConsultations.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <p className="text-2xl mb-2">✅</p>
              <p className="text-sm">Sin orientaciones pendientes</p>
            </div>
          ) : (
            <div className="space-y-3">
              {pendingConsultations.map((c) => {
                const badge = STATUS_BADGE[c.status];
                return (
                  <div key={c.id} className="flex items-center justify-between p-3 rounded-xl border border-[var(--border)]">
                    <div>
                      <p className="text-sm font-medium text-gray-900">{c.patient.user.name}</p>
                      <p className="text-xs text-gray-400 mt-0.5">
                        Dr. {c.doctor.user.name} · {formatDateTime(c.scheduledAt)}
                      </p>
                    </div>
                    <span className={`px-2.5 py-1 rounded-full text-xs font-semibold ${badge.cls}`}>
                      {badge.label}
                    </span>
                  </div>
                );
              })}
            </div>
          )}
        </div>

        {/* Recent payments */}
        <div className="bg-white rounded-xl border border-[var(--border)] p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="font-bold text-gray-900">Últimos pagos</h2>
            <Link href="/admin/ingresos" className="text-sm text-[var(--primary)] hover:underline">
              Ver todos →
            </Link>
          </div>

          {recentPayments.length === 0 ? (
            <div className="text-center py-8 text-gray-400">
              <p className="text-2xl mb-2">💳</p>
              <p className="text-sm">Sin pagos registrados</p>
            </div>
          ) : (
            <div className="space-y-3">
              {recentPayments.map((p) => (
                <div key={p.id} className="flex items-center justify-between p-3 rounded-xl border border-[var(--border)]">
                  <div>
                    <p className="text-sm font-medium text-gray-900">{p.patient.user.name}</p>
                    <p className="text-xs text-gray-400 mt-0.5">{formatDate(p.createdAt)}</p>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-bold text-gray-900">${p.amount.toLocaleString()} MXN</p>
                    <span className="text-xs text-green-600 font-medium">Aprobado</span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

