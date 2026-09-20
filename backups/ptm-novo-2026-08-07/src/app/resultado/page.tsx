"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { Suspense } from "react";

const PROGRAM_DATA = {
  WEIGHT_LOSS: {
    icon: "⚖️",
    name: "Pérdida de Peso",
    description: "Eres candidato para un protocolo médico de pérdida de peso con péptidos GLP-1. Tu médico definirá el tratamiento exacto en la orientación médica.",
    peptides: ["Semaglutide o Tirzepatide compuesto", "AOD-9604 (fat burning)", "CJC-1295 + Ipamorelin (preservación muscular)"],
    result: "Basado en tus respuestas, un protocolo GLP-1 es la opción más efectiva para ti.",
  },
  LONGEVITY: {
    icon: "⚡",
    name: "Péptidos & Longevidad",
    description: "Eres candidato para un stack de péptidos de longevidad y antiaging. Tu médico definirá el protocolo exacto según tu objetivo específico.",
    peptides: ["Epithalon (regulación epigenética y sueño)", "GHK-Cu (regeneración celular y antiaging)", "CJC-1295 / Ipamorelin (HGH natural)", "NAD+ / Selank según tu objetivo"],
    result: "Basado en tus respuestas, un stack de péptidos de longevidad y antiaging es lo ideal para ti.",
  },
  PERFORMANCE: {
    icon: "💪",
    name: "Rendimiento & Recuperación",
    description: "Eres candidato para un stack de péptidos enfocado en rendimiento, fuerza y recuperación muscular. Tu médico diseñará el protocolo exacto según tus objetivos.",
    peptides: ["BPC-157 (recuperación y antiinflamatorio)", "IGF-1 LR3 (músculo magro y recuperación)", "MK-677 / CJC-1295 (GH natural)", "TB-500 (regeneración de tejidos)"],
    result: "Basado en tus respuestas, un protocolo de rendimiento y recuperación es lo indicado para ti.",
  },
};

function ResultContent() {
  const params = useSearchParams();
  const program = (params.get("program") ?? "LONGEVITY") as keyof typeof PROGRAM_DATA;
  const data = PROGRAM_DATA[program] ?? PROGRAM_DATA.LONGEVITY;

  return (
    <main className="min-h-screen bg-[var(--muted)] flex items-center justify-center px-6 py-16">
      <div className="max-w-lg w-full">
        {/* Result card */}
        <div className="bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
          <div className="bg-[var(--primary)] px-8 py-6 text-center">
            <div className="text-5xl mb-3">{data.icon}</div>
            <p className="text-[var(--accent-light)] text-sm font-medium mb-1">Tu programa recomendado</p>
            <h1 className="text-2xl font-bold text-white">{data.name}</h1>
          </div>

          <div className="px-8 py-6">
            <div className="bg-[var(--accent-light)] rounded-xl p-4 mb-6">
              <p className="text-[var(--accent)] text-sm font-semibold">{data.result}</p>
            </div>

            <p className="text-gray-600 text-sm mb-5">{data.description}</p>

            <div className="mb-6">
              <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-3">
                Péptidos que revisará tu médico contigo
              </p>
              <ul className="space-y-2">
                {data.peptides.map((p) => (
                  <li key={p} className="flex items-start gap-2 text-sm text-gray-700">
                    <span className="text-[var(--accent)] mt-0.5">✓</span>
                    {p}
                  </li>
                ))}
              </ul>
            </div>

            <div className="border-t border-[var(--border)] pt-5">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <p className="font-bold text-gray-900">Orientación médica</p>
                  <p className="text-xs text-gray-500">Orientación médica 30 min · Protocolo incluida</p>
                </div>
                <div className="text-right">
                  <p className="text-2xl font-bold text-[var(--primary)]">$1,500</p>
                  <p className="text-xs text-gray-400">MXN</p>
                </div>
              </div>

              <Link
                href={`/checkout?program=${program}`}
                className="block w-full text-center py-4 rounded-xl font-bold text-white text-lg bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
              >
                Agendar mi orientación médica →
              </Link>
              <p className="text-xs text-center text-gray-400 mt-3">
                Sin costos ocultos · Mercado Pago · Tarjeta, SPEI u OXXO
              </p>
            </div>
          </div>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          ¿No es lo que buscas?{" "}
          <Link href="/#quiz" className="text-[var(--primary)] hover:underline">
            Repetir evaluación
          </Link>
        </p>
      </div>
    </main>
  );
}

export default function ResultadoPage() {
  return (
    <Suspense>
      <ResultContent />
    </Suspense>
  );
}

