"use client";

import { useState } from "react";

const PEPTIDES_BY_PROGRAM: Record<string, string[]> = {
  WEIGHT_LOSS: ["Semaglutide", "Tirzepatide", "AOD-9604", "CJC-1295", "Ipamorelin"],
  LONGEVITY: ["BPC-157", "TB-500", "CJC-1295", "Ipamorelin", "Epithalon", "Selank", "Semax", "PT-141", "GHK-Cu", "NAD+"],
  PERFORMANCE: ["BPC-157", "IGF-1 LR3", "TB-500", "MK-677", "CJC-1295", "Ipamorelin", "GHK-Cu"],
};

interface Props {
  consultationId: string;
  program: string;
  patientName: string;
}

export default function ProtocoloForm({ consultationId, program, patientName }: Props) {
  const peptideOptions = PEPTIDES_BY_PROGRAM[program] ?? PEPTIDES_BY_PROGRAM.LONGEVITY;
  const [selected, setSelected] = useState<string[]>([]);
  const [doses, setDoses] = useState<Record<string, string>>({});
  const [instructions, setInstructions] = useState("");
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  function togglePeptide(p: string) {
    setSelected((prev) =>
      prev.includes(p) ? prev.filter((x) => x !== p) : [...prev, p]
    );
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (selected.length === 0) return;
    setLoading(true);

    const res = await fetch("/api/consultations/complete", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        consultationId,
        peptides: selected.map((name) => ({ name, dose: doses[name] ?? "" })),
        instructions,
        notes,
      }),
    });

    if (res.ok) setSaved(true);
    setLoading(false);
  }

  if (saved) {
    return (
      <div className="text-center py-8">
        <p className="text-3xl mb-3">✅</p>
        <p className="font-bold text-gray-900 mb-1">Protocolo enviado a la farmacia</p>
        <p className="text-sm text-gray-500">
          peptidosysuplementos.mx recibirá el pedido para {patientName}
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      <div>
        <p className="text-sm font-semibold text-gray-700 mb-3">Péptidos del protocolo</p>
        <div className="grid grid-cols-2 gap-2">
          {peptideOptions.map((p) => (
            <div key={p}>
              <button
                type="button"
                onClick={() => togglePeptide(p)}
                className={`w-full text-left px-3 py-2.5 rounded-lg border text-sm transition-colors ${
                  selected.includes(p)
                    ? "border-[var(--primary)] bg-[var(--accent-light)] text-[var(--primary-dark)] font-medium"
                    : "border-[var(--border)] hover:border-[var(--accent)]"
                }`}
              >
                {p}
              </button>
              {selected.includes(p) && (
                <input
                  type="text"
                  placeholder="Dosis (ej: 250mcg/día)"
                  value={doses[p] ?? ""}
                  onChange={(e) => setDoses((prev) => ({ ...prev, [p]: e.target.value }))}
                  className="mt-1 w-full px-3 py-2 rounded-lg border border-[var(--border)] text-xs focus:outline-none focus:border-[var(--primary)]"
                />
              )}
            </div>
          ))}
        </div>
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Instrucciones de administración
        </label>
        <textarea
          required
          value={instructions}
          onChange={(e) => setInstructions(e.target.value)}
          rows={3}
          placeholder="Ej: Aplicar subcutáneo en abdomen, 5 días a la semana antes de dormir..."
          className="w-full px-3 py-2.5 rounded-lg border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] resize-none"
        />
      </div>

      <div>
        <label className="block text-sm font-semibold text-gray-700 mb-1">
          Notas clínicas <span className="text-gray-400 font-normal">(internas)</span>
        </label>
        <textarea
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          rows={2}
          placeholder="Observaciones del paciente, contexto clínico..."
          className="w-full px-3 py-2.5 rounded-lg border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] resize-none"
        />
      </div>

      <button
        type="submit"
        disabled={loading || selected.length === 0}
        className="w-full py-3 rounded-xl font-bold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
      >
        {loading ? "Enviando protocolo..." : "Emitir protocolo y enviar a farmacia →"}
      </button>
    </form>
  );
}
