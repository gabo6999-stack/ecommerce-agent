import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import Link from "next/link";

function formatTime(date: Date) {
  return date.toLocaleTimeString("es-MX", { hour: "2-digit", minute: "2-digit" });
}

function formatDate(date: Date) {
  return date.toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" });
}

export default async function DoctorDashboard() {
  const session = await auth();

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session!.user!.email! } },
  });

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const tomorrow = new Date(today);
  tomorrow.setDate(tomorrow.getDate() + 1);

  const todayConsultations = doctor
    ? await prisma.consultation.findMany({
        where: {
          doctorId: doctor.id,
          scheduledAt: { gte: today, lt: tomorrow },
          status: { in: ["SCHEDULED", "IN_PROGRESS"] },
        },
        include: { patient: { include: { user: true } } },
        orderBy: { scheduledAt: "asc" },
      })
    : [];

  const totalPatients = doctor
    ? await prisma.consultation.findMany({
        where: { doctorId: doctor.id },
        select: { patientId: true },
        distinct: ["patientId"],
      })
    : [];

  const thisMonthStart = new Date();
  thisMonthStart.setDate(1);
  thisMonthStart.setHours(0, 0, 0, 0);

  const monthConsultations = doctor
    ? await prisma.consultation.count({
        where: {
          doctorId: doctor.id,
          status: "COMPLETED",
          scheduledAt: { gte: thisMonthStart },
        },
      })
    : 0;

  // Split fijo del modelo limpio: $1,000 MXN por consulta completada.
  const monthEarnings = monthConsultations * 1000;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Buen día, Dr. {session?.user?.name?.split(" ")[0]}</h1>
        <p className="text-gray-500 text-sm mt-1 capitalize">{formatDate(new Date())}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        {[
          { label: "Orientaciones hoy", value: todayConsultations.length, icon: "📅", color: "bg-blue-50 text-blue-600" },
          { label: "Pacientes totales", value: totalPatients.length, icon: "👥", color: "bg-green-50 text-green-600" },
          { label: "Ganado este mes", value: `$${monthEarnings.toLocaleString()} MXN`, icon: "💰", color: "bg-yellow-50 text-yellow-600" },
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

      {/* Today's consultations */}
      <div className="bg-white rounded-xl border border-[var(--border)] p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="font-bold text-gray-900">Orientaciones de hoy</h2>
          <Link href="/doctor/consultas" className="text-sm text-[var(--primary)] hover:underline">
            Ver todas →
          </Link>
        </div>

        {todayConsultations.length === 0 ? (
          <div className="text-center py-10 text-gray-400">
            <p className="text-3xl mb-2">📭</p>
            <p className="text-sm">No hay orientaciones programadas para hoy</p>
          </div>
        ) : (
          <div className="space-y-3">
            {todayConsultations.map((c) => (
              <div
                key={c.id}
                className="flex items-center justify-between p-4 rounded-xl border border-[var(--border)] hover:border-[var(--accent)] transition-colors"
              >
                <div className="flex items-center gap-4">
                  <div className="w-10 h-10 rounded-full bg-[var(--accent-light)] flex items-center justify-center text-[var(--primary)] font-bold text-sm">
                    {c.patient.user.name.charAt(0).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium text-gray-900 text-sm">{c.patient.user.name}</p>
                    <p className="text-xs text-gray-400">
                      {c.program === "WEIGHT_LOSS" ? "⚖️ Pérdida de Peso" : c.program === "PERFORMANCE" ? "💪 Rendimiento & Recuperación" : "⚡ Péptidos & Longevidad"} · {formatTime(c.scheduledAt)}
                    </p>
                  </div>
                </div>
                <Link
                  href={`/doctor/consultas/${c.id}`}
                  className="px-4 py-2 rounded-lg text-sm font-semibold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
                >
                  {c.status === "IN_PROGRESS" ? "🔴 En curso" : "Entrar →"}
                </Link>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
