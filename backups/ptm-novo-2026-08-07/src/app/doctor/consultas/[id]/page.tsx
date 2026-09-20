import { notFound } from "next/navigation";
import { prisma } from "@/lib/prisma";
import VideoConsulta from "@/components/doctor/VideoConsulta";
import ProtocoloForm from "@/components/doctor/ProtocoloForm";

type QuizAnswers = {
  objective?: string;
  previousAttempts?: string;
  medicalConditions?: string;
  age?: string;
  startDate?: string;
};

const QUIZ_LABELS: Record<string, Record<string, string>> = {
  objective: { weight_loss: "Perder peso", performance: "Rendimiento/músculo", longevity: "Longevidad", sleep_hormones: "Sueño/hormonal" },
  previousAttempts: { first_time: "Primera vez", no_results: "Sin resultados duraderos", no_followup: "Sin seguimiento médico", ready_to_start: "Listo para empezar" },
  medicalConditions: { none: "Ninguna", diabetes: "Diabetes/prediabetes", hypertension: "Hipertensión/cardíaco", other: "Otra (discutir)" },
  age: { "18-30": "18–30 años", "31-45": "31–45 años", "46-60": "46–60 años", "60+": "60+ años" },
};

function StartConsultaButton({ consultationId }: { consultationId: string }) {
  return (
    <form action={`/api/consultations/${consultationId}/start`} method="POST">
      <button
        type="submit"
        className="px-5 py-2.5 rounded-xl text-sm font-bold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
      >
        Iniciar orientación médica →
      </button>
    </form>
  );
}

export default async function ConsultaPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;

  const consultation = await prisma.consultation.findUnique({
    where: { id },
    include: {
      patient: { include: { user: true } },
      doctor: { include: { user: true } },
      prescription: true,
    },
  });

  if (!consultation) notFound();

  const patient = consultation.patient;
  const quiz = (patient.quizAnswers as QuizAnswers) ?? {};
  const isCompleted = consultation.status === "COMPLETED";
  const hasRoom = !!consultation.roomUrl;

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">
          Orientación médica — {patient.user.name}
        </h1>
        <p className="text-gray-500 text-sm mt-1">
          {consultation.program === "WEIGHT_LOSS" ? "⚖️ Pérdida de Peso" : consultation.program === "PERFORMANCE" ? "💪 Rendimiento & Recuperación" : "⚡ Péptidos & Longevidad"} ·{" "}
          {new Date(consultation.scheduledAt).toLocaleString("es-MX")}
        </p>
      </div>

      <div className="grid grid-cols-5 gap-6">
        {/* Left — Video + Protocolo */}
        <div className="col-span-3 space-y-6">
          {/* Video */}
          <div className="bg-white rounded-xl border border-[var(--border)] p-5">
            <h2 className="font-bold text-gray-900 mb-4">Orientación médica</h2>
            {isCompleted ? (
              <div className="text-center py-8 text-gray-400">
                <p className="text-2xl mb-2">✅</p>
                <p className="text-sm">Orientación completada</p>
              </div>
            ) : hasRoom ? (
              <VideoConsulta
                roomUrl={consultation.roomUrl!}
                onEnd={() => { window.location.reload(); }}
              />
            ) : (
              <div className="text-center py-8">
                <p className="text-3xl mb-3">📹</p>
                <p className="text-sm text-gray-500 mb-4">
                  La sala de video se creará al iniciar la orientación médica
                </p>
                <StartConsultaButton consultationId={consultation.id} />
              </div>
            )}
          </div>

          {/* Protocolo */}
          {!isCompleted && (
            <div className="bg-white rounded-xl border border-[var(--border)] p-5">
              <h2 className="font-bold text-gray-900 mb-4">Protocolo</h2>
              <ProtocoloForm
                consultationId={consultation.id}
                program={consultation.program}
                patientName={patient.user.name}
              />
            </div>
          )}

          {isCompleted && consultation.prescription && (
            <div className="bg-white rounded-xl border border-[var(--border)] p-5">
              <h2 className="font-bold text-gray-900 mb-3">Protocolo emitido</h2>
              <div className="space-y-2">
                {(consultation.prescription.peptides as { name: string; dose: string }[]).map((p) => (
                  <div key={p.name} className="flex items-center justify-between text-sm">
                    <span className="font-medium text-gray-700">{p.name}</span>
                    <span className="text-gray-400">{p.dose}</span>
                  </div>
                ))}
                <div className="border-t border-[var(--border)] pt-3 mt-3">
                  <p className="text-xs text-gray-500">{consultation.prescription.instructions}</p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Right — Info del paciente */}
        <div className="col-span-2 space-y-5">
          <div className="bg-white rounded-xl border border-[var(--border)] p-5">
            <h2 className="font-bold text-gray-900 mb-4">Datos del paciente</h2>
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide">Nombre</p>
                <p className="text-sm font-medium text-gray-900">{patient.user.name}</p>
              </div>
              <div>
                <p className="text-xs text-gray-400 uppercase tracking-wide">Correo</p>
                <p className="text-sm text-gray-700">{patient.user.email}</p>
              </div>
              {patient.user.phone && (
                <div>
                  <p className="text-xs text-gray-400 uppercase tracking-wide">WhatsApp</p>
                  <p className="text-sm text-gray-700">{patient.user.phone}</p>
                </div>
              )}
              {patient.weight && (
                <div>
                  <p className="text-xs text-gray-400 uppercase tracking-wide">Peso</p>
                  <p className="text-sm text-gray-700">{patient.weight} kg</p>
                </div>
              )}
            </div>
          </div>

          <div className="bg-white rounded-xl border border-[var(--border)] p-5">
            <h2 className="font-bold text-gray-900 mb-4">Respuestas del quiz</h2>
            <div className="space-y-3">
              {Object.entries(QUIZ_LABELS).map(([key, map]) => {
                const val = quiz[key as keyof QuizAnswers];
                if (!val) return null;
                return (
                  <div key={key}>
                    <p className="text-xs text-gray-400 uppercase tracking-wide capitalize">{key.replace(/([A-Z])/g, " $1")}</p>
                    <p className="text-sm text-gray-800 font-medium">{map[val] ?? val}</p>
                  </div>
                );
              })}
              {patient.medicalHistory && (
                <div>
                  <p className="text-xs text-gray-400 uppercase tracking-wide">Historial</p>
                  <p className="text-sm text-gray-700">{patient.medicalHistory}</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
