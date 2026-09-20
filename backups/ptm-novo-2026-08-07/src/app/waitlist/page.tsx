"use client";

import Link from "next/link";
import { useState } from "react";

export default function WaitlistPage() {
  const [submitted, setSubmitted] = useState(false);
  const [email, setEmail] = useState("");

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setSubmitted(true);
  }

  return (
    <main className="min-h-screen bg-[var(--muted)] flex items-center justify-center px-6 py-16">
      <div className="max-w-md w-full bg-white rounded-2xl border border-[var(--border)] p-8 shadow-sm text-center">
        {!submitted ? (
          <>
            <div className="text-4xl mb-4">📬</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">Te mantenemos informado</h1>
            <p className="text-gray-500 text-sm mb-6">
              Déjanos tu correo y te avisamos cuando tengamos disponibilidad o información
              relevante para tu objetivo de salud.
            </p>
            <form onSubmit={handleSubmit} className="space-y-3">
              <input
                type="email"
                required
                placeholder="tu@correo.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)]"
              />
              <button
                type="submit"
                className="w-full py-3 rounded-xl font-semibold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
              >
                Avisarme →
              </button>
            </form>
          </>
        ) : (
          <>
            <div className="text-4xl mb-4">✅</div>
            <h1 className="text-2xl font-bold text-gray-900 mb-2">¡Listo!</h1>
            <p className="text-gray-500 text-sm mb-6">
              Te contactaremos pronto. Si cambias de opinión y quieres agendar tu orientación médica ahora, puedes hacerlo en cualquier momento.
            </p>
            <Link
              href="/"
              className="inline-block px-6 py-3 rounded-xl text-sm font-semibold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors"
            >
              Volver al inicio
            </Link>
          </>
        )}
      </div>
    </main>
  );
}
