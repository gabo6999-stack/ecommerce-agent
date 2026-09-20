"use client";

import { useState, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";

const PROGRAM_INFO = {
  WEIGHT_LOSS: { icon: "⚖️", name: "Pérdida de Peso", desc: "Protocolo GLP-1 personalizado" },
  LONGEVITY: { icon: "⚡", name: "Péptidos & Longevidad", desc: "Stack de péptidos personalizado" },
  PERFORMANCE: { icon: "💪", name: "Rendimiento & Recuperación", desc: "Stack de péptidos para rendimiento" },
};

function CheckoutForm() {
  const params = useSearchParams();
  const program = (params.get("program") ?? "LONGEVITY") as keyof typeof PROGRAM_INFO;
  const info = PROGRAM_INFO[program] ?? PROGRAM_INFO.LONGEVITY;

  const [form, setForm] = useState({ name: "", email: "", phone: "" });
  const [privacyAccepted, setPrivacyAccepted] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  function handleChange(e: React.ChangeEvent<HTMLInputElement>) {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const res = await fetch("/api/payments/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, program, privacyAcceptedAt: new Date().toISOString() }),
      });

      const data = await res.json();

      if (!res.ok) throw new Error(data.error ?? "Error al procesar pago");

      window.location.href = data.url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[var(--muted)] flex items-center justify-center px-6 py-16">
      <div className="w-full max-w-lg">
        <Link href="/" className="text-sm text-gray-500 hover:text-[var(--primary)] mb-6 inline-block">
          ← Volver
        </Link>

        <div className="bg-white rounded-2xl border border-[var(--border)] shadow-sm overflow-hidden">
          {/* Header */}
          <div className="bg-[var(--primary)] px-8 py-6">
            <p className="text-[var(--accent-light)] text-xs font-medium uppercase tracking-widest mb-1">
              Orientación médica
            </p>
            <div className="flex items-center gap-3">
              <span className="text-3xl">{info.icon}</span>
              <div>
                <h1 className="text-xl font-bold text-white">{info.name}</h1>
                <p className="text-gray-300 text-sm">{info.desc}</p>
              </div>
            </div>
          </div>

          {/* Resumen */}
          <div className="px-8 pt-6">
            <div className="bg-[var(--muted)] rounded-xl p-4 mb-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">Orientación médica 30 min</span>
                <span className="text-sm font-semibold text-gray-900">$1,500 MXN</span>
              </div>
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-600">Protocolo de tratamiento</span>
                <span className="text-sm text-[var(--accent)] font-medium">Incluida</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Seguimiento mes 1</span>
                <span className="text-sm text-[var(--accent)] font-medium">Incluido</span>
              </div>
              <div className="border-t border-[var(--border)] mt-3 pt-3 flex justify-between items-center">
                <span className="font-bold text-gray-900">Total</span>
                <span className="text-2xl font-bold text-[var(--primary)]">$1,500 MXN</span>
              </div>
            </div>

            {/* Formulario */}
            <form onSubmit={handleSubmit} className="space-y-4 pb-8">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nombre completo
                </label>
                <input
                  type="text"
                  name="name"
                  required
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Juan Pérez García"
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Correo electrónico
                </label>
                <input
                  type="email"
                  name="email"
                  required
                  value={form.email}
                  onChange={handleChange}
                  placeholder="juan@correo.com"
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  WhatsApp <span className="text-gray-400 font-normal">(para confirmar tu cita)</span>
                </label>
                <input
                  type="tel"
                  name="phone"
                  value={form.phone}
                  onChange={handleChange}
                  placeholder="55 1234 5678"
                  className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                />
              </div>

              {/* Privacy consent */}
              <div className={`flex items-start gap-3 p-4 rounded-xl border transition-colors ${
                privacyAccepted ? "border-[var(--primary)] bg-blue-50" : "border-[var(--border)] bg-[var(--muted)]"
              }`}>
                <input
                  id="privacy"
                  type="checkbox"
                  checked={privacyAccepted}
                  onChange={(e) => setPrivacyAccepted(e.target.checked)}
                  className="mt-0.5 w-4 h-4 accent-[var(--primary)] flex-shrink-0 cursor-pointer"
                />
                <label htmlFor="privacy" className="text-xs text-gray-600 cursor-pointer leading-relaxed">
                  He leído y acepto el{" "}
                  <a
                    href="/aviso-de-privacidad"
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-[var(--primary)] underline font-medium"
                    onClick={(e) => e.stopPropagation()}
                  >
                    Aviso de Privacidad
                  </a>{" "}
                  de Peptide Technologies México, incluyendo el tratamiento de mis{" "}
                  <strong>datos sensibles de salud</strong> para la prestación del servicio médico.
                  <span className="text-red-500 ml-1">*</span>
                </label>
              </div>

              {error && (
                <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl px-4 py-3">
                  {error}
                </div>
              )}

              <button
                type="submit"
                disabled={loading || !privacyAccepted}
                className="w-full py-4 rounded-xl font-bold text-white text-lg bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? "Procesando..." : "Pagar $1,500 MXN →"}
              </button>
              {!privacyAccepted && (
                <p className="text-xs text-center text-gray-400">
                  Debes aceptar el Aviso de Privacidad para continuar
                </p>
              )}

              <div className="flex items-center justify-center gap-4 pt-1">
                <span className="text-xs text-gray-400">Pago seguro con</span>
                <span className="text-xs font-semibold text-gray-500">Stripe</span>
                <span className="text-xs text-gray-400">·</span>
                <span className="text-xs text-gray-400">Tarjeta</span>
              </div>
            </form>
          </div>
        </div>
      </div>
    </main>
  );
}

export default function CheckoutPage() {
  return (
    <Suspense>
      <CheckoutForm />
    </Suspense>
  );
}


