"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import type { QuizAnswer } from "@/types";

const QUESTIONS = [
  {
    id: "objective" as const,
    question: "¿Cuál es tu objetivo principal?",
    purpose: "Esto nos ayuda a asignarte el programa correcto.",
    options: [
      { value: "weight_loss", label: "Perder peso de forma efectiva", icon: "⚖️" },
      { value: "performance", label: "Mejorar rendimiento, músculo o recuperación", icon: "💪" },
      { value: "longevity", label: "Antiaging, longevidad y energía", icon: "⚡" },
      { value: "sleep_hormones", label: "Mejorar sueño o salud hormonal", icon: "🌙" },
    ],
  },
  {
    id: "previousAttempts" as const,
    question: "¿Has intentado alcanzar ese objetivo antes?",
    purpose: "Entender tu historial nos permite personalizar mejor tu protocolo.",
    options: [
      { value: "first_time", label: "No, es mi primera vez buscando ayuda médica", icon: "🌱" },
      { value: "no_results", label: "Sí, con dietas o suplementos sin resultados duraderos", icon: "😔" },
      { value: "no_followup", label: "Sí, con otro médico pero sin seguimiento real", icon: "🔄" },
      { value: "ready_to_start", label: "He investigado péptidos y quiero empezar ya", icon: "🚀" },
    ],
  },
  {
    id: "medicalConditions" as const,
    question: "¿Tienes alguna de estas condiciones?",
    purpose: "Tu médico revisará esto antes de la orientación médica.",
    options: [
      { value: "none", label: "No tengo ninguna", icon: "✅" },
      { value: "diabetes", label: "Diabetes o prediabetes", icon: "🩺" },
      { value: "hypertension", label: "Hipertensión o enfermedad cardíaca", icon: "❤️" },
      { value: "other", label: "Otra condición (la discuto con el médico)", icon: "📋" },
    ],
  },
  {
    id: "age" as const,
    question: "¿Cuántos años tienes?",
    purpose: "La edad define el protocolo de péptidos más efectivo para ti.",
    options: [
      { value: "18-30", label: "18 – 30 años", icon: "🟢" },
      { value: "31-45", label: "31 – 45 años", icon: "🟡" },
      { value: "46-60", label: "46 – 60 años", icon: "🟠" },
      { value: "60+", label: "60+ años", icon: "🔵" },
    ],
  },
  {
    id: "startDate" as const,
    question: "¿Cuándo quieres empezar tu tratamiento?",
    purpose: "Esto nos ayuda a priorizar tu agenda.",
    options: [
      { value: "asap", label: "Lo antes posible", icon: "⚡" },
      { value: "two_weeks", label: "En las próximas 2 semanas", icon: "📅" },
      { value: "comparing", label: "Estoy comparando opciones", icon: "🔍" },
      { value: "info_only", label: "Solo quiero información por ahora", icon: "📖" },
    ],
  },
];

function getProgram(answers: Partial<QuizAnswer>): "WEIGHT_LOSS" | "LONGEVITY" | "PERFORMANCE" {
  if (answers.objective === "weight_loss") return "WEIGHT_LOSS";
  if (answers.objective === "performance") return "PERFORMANCE";
  return "LONGEVITY";
}

export default function Quiz() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState<Partial<QuizAnswer>>({});
  const [selected, setSelected] = useState<string | null>(null);

  const current = QUESTIONS[step];
  const isLast = step === QUESTIONS.length - 1;
  const progress = ((step + 1) / QUESTIONS.length) * 100;

  function handleSelect(value: string) {
    setSelected(value);
  }

  function handleNext() {
    if (!selected) return;
    const updated = { ...answers, [current.id]: selected as never };
    setAnswers(updated);
    setSelected(null);

    if (isLast) {
      const program = getProgram(updated);
      const infoOnly = selected === "info_only";
      if (infoOnly) {
        router.push(`/waitlist?program=${program}`);
      } else {
        router.push(`/resultado?program=${program}&data=${encodeURIComponent(JSON.stringify(updated))}`);
      }
    } else {
      setStep((s) => s + 1);
    }
  }

  return (
    <div className="w-full max-w-xl mx-auto">
      {/* Progress */}
      <div className="mb-8">
        <div className="flex justify-between text-sm text-gray-500 mb-2">
          <span>Pregunta {step + 1} de {QUESTIONS.length}</span>
          <span>{Math.round(progress)}% completado</span>
        </div>
        <div className="h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className="h-full rounded-full transition-all duration-500"
            style={{ width: `${progress}%`, backgroundColor: "var(--primary)" }}
          />
        </div>
      </div>

      {/* Question */}
      <div className="mb-2">
        <h2 className="text-2xl font-bold text-gray-900 mb-1">{current.question}</h2>
        <p className="text-sm text-gray-500">{current.purpose}</p>
      </div>

      {/* Options */}
      <div className="mt-6 space-y-3">
        {current.options.map((opt) => (
          <button
            key={opt.value}
            onClick={() => handleSelect(opt.value)}
            className={`w-full text-left px-5 py-4 rounded-xl border-2 transition-all duration-150 flex items-center gap-3 ${
              selected === opt.value
                ? "border-[var(--primary)] bg-[var(--accent-light)] text-white font-medium"
                : "border-[var(--border)] bg-white hover:border-[var(--accent)] hover:bg-[var(--muted)]"
            }`}
          >
            <span className="text-xl">{opt.icon}</span>
            <span className="text-base">{opt.label}</span>
          </button>
        ))}
      </div>

      {/* Next button */}
      <button
        onClick={handleNext}
        disabled={!selected}
        className="mt-8 w-full py-4 rounded-xl font-semibold text-white text-lg transition-all duration-150 disabled:opacity-40 disabled:cursor-not-allowed"
        style={{ backgroundColor: selected ? "var(--primary)" : undefined }}
      >
        {isLast ? "Ver mi resultado →" : "Siguiente →"}
      </button>
    </div>
  );
}
