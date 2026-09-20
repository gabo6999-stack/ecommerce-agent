"use client";

import Link from "next/link";
import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";

type SetupStep = "loading" | "form" | "submitting" | "done" | "exists";

function SuccessContent() {
  const params = useSearchParams();
  const sessionId = params.get("session_id");

  const [step, setStep] = useState<SetupStep>("loading");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    if (!sessionId) {
      setStep("form");
      return;
    }

    fetch(`/api/auth/setup-account?session_id=${sessionId}`)
      .then((r) => r.json())
      .then((data) => {
        if (data.email) setEmail(data.email);
        setStep(data.needsSetup ? "form" : "exists");
      })
      .catch(() => setStep("form"));
  }, [sessionId]);

  async function handleSetup(e: React.FormEvent) {
    e.preventDefault();
    setError("");

    if (password !== confirm) {
      setError("Las contraseñas no coinciden");
      return;
    }

    setStep("submitting");

    try {
      const res = await fetch("/api/auth/setup-account", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sessionId, email, password }),
      });

      const data = await res.json();
      if (!res.ok) throw new Error(data.error ?? "Error al crear cuenta");
      setStep("done");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
      setStep("form");
    }
  }

  return (
    <main className="min-h-screen bg-[var(--muted)] flex items-center justify-center px-6 py-16">
      <div className="max-w-md w-full space-y-5">
        {/* Payment confirmed */}
        <div className="bg-white rounded-2xl border border-[var(--border)] shadow-sm p-10 text-center">
          <div className="w-16 h-16 rounded-full bg-[var(--accent-light)] flex items-center justify-center mx-auto mb-6">
            <span className="text-3xl">✅</span>
          </div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">¡Pago confirmado!</h1>
          <p className="text-gray-500 text-sm mb-6">
            Tu orientación médica está reservada. En los próximos minutos recibirás un mensaje de
            WhatsApp con los detalles y el link de tu orientación médica.
          </p>

          {sessionId && (
            <p className="text-xs text-gray-400 mb-6">
              Referencia: <span className="font-mono">{sessionId.slice(-12)}</span>
            </p>
          )}

          <div className="bg-[var(--muted)] rounded-xl p-4 text-left space-y-2">
            <p className="text-sm font-semibold text-gray-700">¿Qué sigue?</p>
            {[
              "Recibirás confirmación por WhatsApp en los próximos minutos",
              "Tu médico revisará tu evaluación antes de la orientación médica",
              "Recibirás el link de orientación médica confirmado",
            ].map((s, i) => (
              <div key={i} className="flex items-start gap-2 text-sm text-gray-600">
                <span className="text-[var(--accent)] mt-0.5">{i + 1}.</span>
                {s}
              </div>
            ))}
          </div>
        </div>

        {/* Account activation */}
        <div className="bg-white rounded-2xl border border-[var(--border)] shadow-sm p-8">
          {step === "loading" && (
            <div className="text-center py-4 text-gray-400">
              <p className="text-sm">Preparando tu cuenta...</p>
            </div>
          )}

          {step === "exists" && (
            <div className="text-center">
              <p className="text-2xl mb-3">🔐</p>
              <p className="font-bold text-gray-900 mb-1">Ya tienes cuenta</p>
              <p className="text-sm text-gray-500 mb-5">
                Inicia sesión para ver tu orientación médica en tu portal de paciente.
              </p>
              <Link
                href="/login"
                className="inline-block px-6 py-3 rounded-xl text-sm font-semibold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
              >
                Ir a mi portal →
              </Link>
            </div>
          )}

          {(step === "form" || step === "submitting") && (
            <>
              <h2 className="font-bold text-gray-900 mb-1">Activa tu cuenta</h2>
              <p className="text-sm text-gray-500 mb-5">
                Crea tu contraseña para acceder al portal de paciente: orientaciones, Protocolos y
                seguimiento de progreso.
              </p>

              <form onSubmit={handleSetup} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Correo</label>
                  <input
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    required
                    placeholder="tu@correo.com"
                    className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña</label>
                  <input
                    type="password"
                    required
                    minLength={8}
                    value={password}
                    onChange={(e) => setPassword(e.target.value)}
                    placeholder="Mínimo 8 caracteres"
                    className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Confirmar contraseña
                  </label>
                  <input
                    type="password"
                    required
                    value={confirm}
                    onChange={(e) => setConfirm(e.target.value)}
                    placeholder="Repite tu contraseña"
                    className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)] transition-colors"
                  />
                </div>

                {error && (
                  <div className="bg-red-50 border border-red-200 text-red-600 text-sm rounded-xl px-4 py-3">
                    {error}
                  </div>
                )}

                <button
                  type="submit"
                  disabled={step === "submitting"}
                  className="w-full py-3 rounded-xl font-bold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors disabled:opacity-50"
                >
                  {step === "submitting" ? "Creando cuenta..." : "Activar mi cuenta →"}
                </button>
              </form>
            </>
          )}

          {step === "done" && (
            <div className="text-center">
              <p className="text-3xl mb-3">🎉</p>
              <p className="font-bold text-gray-900 mb-1">¡Cuenta activada!</p>
              <p className="text-sm text-gray-500 mb-5">
                Inicia sesión con tu correo y contraseña para ver tu orientación médica.
              </p>
              <Link
                href="/login"
                className="inline-block px-6 py-3 rounded-xl text-sm font-semibold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
              >
                Ir a mi portal →
              </Link>
            </div>
          )}
        </div>
      </div>
    </main>
  );
}

export default function PagoExitosoPage() {
  return (
    <Suspense>
      <SuccessContent />
    </Suspense>
  );
}

