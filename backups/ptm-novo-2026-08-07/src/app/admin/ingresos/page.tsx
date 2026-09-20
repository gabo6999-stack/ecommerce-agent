import { prisma } from "@/lib/prisma";

function formatDate(date: Date) {
  return date.toLocaleDateString("es-MX", {
    day: "numeric",
    month: "short",
    year: "numeric",
  });
}

function getMonthKey(date: Date) {
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}`;
}

function formatMonthKey(key: string) {
  const [year, month] = key.split("-");
  const d = new Date(Number(year), Number(month) - 1, 1);
  return d.toLocaleDateString("es-MX", { month: "long", year: "numeric" });
}

export default async function AdminIngresosPage() {
  const payments = await prisma.payment.findMany({
    where: { status: "APPROVED" },
    include: {
      patient: { include: { user: true } },
      consultation: { include: { doctor: { include: { user: true } } } },
    },
    orderBy: { createdAt: "desc" },
  });

  // Split FIJO (no porcentaje): PTM = platformFee ($500), médico = doctorAmount
  // ($1,000). Ver MODELO_MONETIZACION_PTM.md §5.
  const totalCobrado = payments.reduce((s, p) => s + p.amount, 0);
  const totalPTM = payments.reduce((s, p) => s + p.platformFee, 0);
  const totalMedicos = payments.reduce((s, p) => s + p.doctorAmount, 0);

  const monthStart = new Date();
  monthStart.setDate(1);
  monthStart.setHours(0, 0, 0, 0);

  const pagosMes = payments.filter((p) => p.createdAt >= monthStart);
  const cobradoMes = pagosMes.reduce((s, p) => s + p.amount, 0);

  // Group by month for summary
  const byMonth: Record<string, { count: number; total: number; ptm: number }> = {};
  for (const p of payments) {
    const key = getMonthKey(p.createdAt);
    if (!byMonth[key]) byMonth[key] = { count: 0, total: 0, ptm: 0 };
    byMonth[key].count += 1;
    byMonth[key].total += p.amount;
    byMonth[key].ptm += p.platformFee;
  }
  const monthKeys = Object.keys(byMonth).sort((a, b) => b.localeCompare(a));

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Ingresos</h1>
        <p className="text-gray-500 text-sm mt-1">{payments.length} pagos aprobados</p>
      </div>

      {/* KPI cards */}
      <div className="grid grid-cols-4 gap-5 mb-8">
        {[
          { label: "Cobrado este mes", value: `$${cobradoMes.toLocaleString()}`, sub: "MXN · total bruto", color: "bg-blue-50 text-blue-600", icon: "📅" },
          { label: "Total histórico", value: `$${totalCobrado.toLocaleString()}`, sub: "MXN · total bruto", color: "bg-gray-50 text-gray-600", icon: "💳" },
          { label: "PTM · comisión de plataforma", value: `$${totalPTM.toLocaleString()}`, sub: "MXN · ingreso propio ($500/consulta)", color: "bg-green-50 text-green-600", icon: "💰" },
          { label: "Pagado a médicos", value: `$${totalMedicos.toLocaleString()}`, sub: "MXN · honorarios ($1,000/consulta)", color: "bg-purple-50 text-purple-600", icon: "👨‍⚕️" },
        ].map((s) => (
          <div key={s.label} className="bg-white rounded-xl border border-[var(--border)] p-5">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl mb-3 ${s.color}`}>
              {s.icon}
            </div>
            <p className="text-2xl font-bold text-gray-900">{s.value}</p>
            <p className="text-sm text-gray-500 mt-0.5">{s.label}</p>
            <p className="text-xs text-gray-400 mt-0.5">{s.sub}</p>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-3 gap-5">
        {/* Payments table */}
        <div className="col-span-2 bg-white rounded-xl border border-[var(--border)] overflow-hidden">
          <div className="px-6 py-4 border-b border-[var(--border)]">
            <h2 className="font-bold text-gray-900">Historial de pagos</h2>
          </div>

          {payments.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <p className="text-3xl mb-2">💳</p>
              <p className="text-sm">Sin pagos registrados</p>
            </div>
          ) : (
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-[var(--border)] bg-[var(--muted)]">
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Paciente
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Médico
                  </th>
                  <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Fecha
                  </th>
                  <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    Monto
                  </th>
                  <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    PTM (comisión)
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-[var(--border)]">
                {payments.map((p) => (
                  <tr key={p.id} className="hover:bg-[var(--muted)] transition-colors">
                    <td className="px-5 py-3.5 font-medium text-gray-900">
                      {p.patient.user.name}
                    </td>
                    <td className="px-5 py-3.5 text-gray-500">
                      {p.consultation?.doctor
                        ? `Dr. ${p.consultation.doctor.user.name}`
                        : <span className="text-gray-300">—</span>}
                    </td>
                    <td className="px-5 py-3.5 text-gray-400 text-xs">
                      {formatDate(p.createdAt)}
                    </td>
                    <td className="px-5 py-3.5 text-right font-semibold text-gray-900">
                      ${p.amount.toLocaleString()}
                    </td>
                    <td className="px-5 py-3.5 text-right text-green-700 font-semibold">
                      ${p.platformFee.toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </div>

        {/* Monthly summary */}
        <div className="bg-white rounded-xl border border-[var(--border)] overflow-hidden">
          <div className="px-6 py-4 border-b border-[var(--border)]">
            <h2 className="font-bold text-gray-900">Por mes</h2>
          </div>

          {monthKeys.length === 0 ? (
            <div className="text-center py-12 text-gray-400">
              <p className="text-sm">Sin datos</p>
            </div>
          ) : (
            <div className="divide-y divide-[var(--border)]">
              {monthKeys.map((key) => {
                const m = byMonth[key];
                return (
                  <div key={key} className="px-5 py-4">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-semibold text-gray-800 capitalize">
                        {formatMonthKey(key)}
                      </p>
                      <span className="text-xs text-gray-400">{m.count} pagos</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-gray-400">PTM · comisión</p>
                      <p className="text-sm font-bold text-green-700">
                        ${m.ptm.toLocaleString()} MXN
                      </p>
                    </div>
                    <div className="flex items-center justify-between">
                      <p className="text-xs text-gray-400">Total bruto</p>
                      <p className="text-xs text-gray-500">${m.total.toLocaleString()}</p>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

