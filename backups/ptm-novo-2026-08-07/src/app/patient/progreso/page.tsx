import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";

export default async function PatientProgresoPage() {
  const session = await auth();

  const patient = await prisma.patient.findFirst({
    where: { user: { email: session!.user!.email! } },
    include: {
      progressLogs: { orderBy: { createdAt: "desc" } },
    },
  });

  async function addLog(formData: FormData) {
    "use server";
    const s = await auth();
    if (!s?.user?.email) return;

    const p = await prisma.patient.findFirst({
      where: { user: { email: s.user.email } },
    });
    if (!p) return;

    const weightRaw = formData.get("weight") as string;
    const notes = (formData.get("notes") as string) || null;
    const symptoms = (formData.get("symptoms") as string) || null;

    await prisma.progressLog.create({
      data: {
        patientId: p.id,
        weight: weightRaw ? parseFloat(weightRaw) : null,
        notes,
        symptoms,
      },
    });

    revalidatePath("/patient/progreso");
  }

  const logs = patient?.progressLogs ?? [];
  const firstWeight = logs.length > 0 ? logs[logs.length - 1].weight : null;
  const latestWeight = logs.find((l) => l.weight != null)?.weight ?? null;
  const weightDiff =
    firstWeight != null && latestWeight != null ? latestWeight - firstWeight : null;

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Mi progreso</h1>
        <p className="text-gray-500 text-sm mt-1">
          Registra tu peso y cómo te sientes semana a semana
        </p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-5 mb-8">
        <div className="bg-white rounded-xl border border-[var(--border)] p-5">
          <div className="w-10 h-10 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center text-xl mb-3">
            📊
          </div>
          <p className="text-2xl font-bold text-gray-900">{logs.length}</p>
          <p className="text-sm text-gray-500 mt-0.5">Registros totales</p>
        </div>

        <div className="bg-white rounded-xl border border-[var(--border)] p-5">
          <div className="w-10 h-10 rounded-lg bg-green-50 text-green-600 flex items-center justify-center text-xl mb-3">
            ⚖️
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {latestWeight != null ? `${latestWeight} kg` : "—"}
          </p>
          <p className="text-sm text-gray-500 mt-0.5">Peso actual</p>
        </div>

        <div className="bg-white rounded-xl border border-[var(--border)] p-5">
          <div
            className={`w-10 h-10 rounded-lg flex items-center justify-center text-xl mb-3 ${
              weightDiff == null
                ? "bg-gray-50 text-gray-400"
                : weightDiff < 0
                ? "bg-green-50 text-green-600"
                : "bg-red-50 text-red-500"
            }`}
          >
            {weightDiff == null ? "—" : weightDiff < 0 ? "📉" : "📈"}
          </div>
          <p className="text-2xl font-bold text-gray-900">
            {weightDiff == null
              ? "—"
              : `${weightDiff > 0 ? "+" : ""}${weightDiff.toFixed(1)} kg`}
          </p>
          <p className="text-sm text-gray-500 mt-0.5">Cambio total</p>
        </div>
      </div>

      <div className="grid grid-cols-5 gap-5">
        {/* Add log form */}
        <div className="col-span-2">
          <div className="bg-white rounded-xl border border-[var(--border)] p-6">
            <h2 className="font-bold text-gray-900 mb-4">Agregar registro</h2>
            <form action={addLog} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Peso (kg)
                </label>
                <input
                  type="number"
                  name="weight"
                  step="0.1"
                  min="30"
                  max="300"
                  placeholder="Ej. 78.5"
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Síntomas o efectos
                </label>
                <input
                  type="text"
                  name="symptoms"
                  placeholder="Ej. Más energía, mejor sueño"
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Notas
                </label>
                <textarea
                  name="notes"
                  rows={3}
                  placeholder="Cómo te sientes esta semana..."
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors resize-none"
                />
              </div>

              <button
                type="submit"
                className="w-full py-3 rounded-xl font-semibold text-white text-sm bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
              >
                Guardar registro
              </button>
            </form>
          </div>
        </div>

        {/* Logs list */}
        <div className="col-span-3">
          <div className="bg-white rounded-xl border border-[var(--border)]">
            <div className="px-6 py-4 border-b border-[var(--border)]">
              <h2 className="font-bold text-gray-900">Historial</h2>
            </div>

            {logs.length === 0 ? (
              <div className="text-center py-12 text-gray-400">
                <p className="text-3xl mb-2">📋</p>
                <p className="text-sm">Agrega tu primer registro</p>
              </div>
            ) : (
              <div className="divide-y divide-[var(--border)]">
                {logs.map((log) => (
                  <div key={log.id} className="px-6 py-4">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-xs text-gray-400">
                        {new Date(log.createdAt).toLocaleDateString("es-MX", {
                          weekday: "long",
                          day: "numeric",
                          month: "long",
                        })}
                      </p>
                      {log.weight != null && (
                        <span className="text-sm font-bold text-gray-900">
                          {log.weight} kg
                        </span>
                      )}
                    </div>
                    {log.symptoms && (
                      <p className="text-sm text-gray-700 mb-0.5">
                        <span className="text-gray-400 text-xs">Síntomas: </span>
                        {log.symptoms}
                      </p>
                    )}
                    {log.notes && (
                      <p className="text-sm text-gray-600">{log.notes}</p>
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
