import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";

export default async function PatientProtocolosPage() {
  const session = await auth();

  const patient = await prisma.patient.findFirst({
    where: { user: { email: session!.user!.email! } },
  });

  const prescriptions = patient
    ? await prisma.prescription.findMany({
        where: { patientId: patient.id },
        include: {
          doctor: { include: { user: true } },
        },
        orderBy: { createdAt: "desc" },
      })
    : [];

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Mis protocolos</h1>
        <p className="text-gray-500 text-sm mt-1">
          {prescriptions.length} protocolo{prescriptions.length !== 1 ? "s" : ""}
        </p>
      </div>

      {prescriptions.length === 0 ? (
        <div className="bg-white rounded-xl border border-[var(--border)] text-center py-16 text-gray-400">
          <p className="text-4xl mb-3">🧬</p>
          <p className="text-sm">Aún no tienes protocolos. Se generan tras tu primera orientación médica.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {prescriptions.map((rx) => {
            const peptides = rx.peptides as { name: string; dose: string; frequency: string }[];
            const isExpired = new Date(rx.expiresAt) < new Date();

            return (
              <div key={rx.id} className="bg-white rounded-xl border border-[var(--border)] p-6">
                <div className="flex items-start justify-between mb-5">
                  <div>
                    <div className="flex items-center gap-2 flex-wrap">
                      <h3 className="font-bold text-gray-900">
                        Protocolo #{rx.id.slice(-6).toUpperCase()}
                      </h3>
                      <span className={`px-2 py-0.5 rounded-full text-xs font-semibold ${
                        isExpired ? "bg-red-100 text-red-600" : "bg-green-100 text-green-700"
                      }`}>
                        {isExpired ? "Vencido" : "Vigente"}
                      </span>
                    </div>
                    <p className="text-xs text-gray-500 mt-1">
                      Dr. {rx.doctor.user.name} · Emitido{" "}
                      {new Date(rx.createdAt).toLocaleDateString("es-MX")} · Vence{" "}
                      {new Date(rx.expiresAt).toLocaleDateString("es-MX")}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-2 mb-4">
                  {peptides.map((p, i) => (
                    <div key={i} className="bg-[var(--muted)] rounded-lg p-3">
                      <p className="font-semibold text-sm text-gray-800">{p.name}</p>
                      <p className="text-xs text-gray-500 mt-0.5">{p.dose} · {p.frequency}</p>
                    </div>
                  ))}
                </div>

                {rx.instructions && (
                  <div className="border-t border-[var(--border)] pt-4">
                    <p className="text-xs font-medium text-gray-600 mb-1">Instrucciones del médico</p>
                    <p className="text-sm text-gray-700 whitespace-pre-line">{rx.instructions}</p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
