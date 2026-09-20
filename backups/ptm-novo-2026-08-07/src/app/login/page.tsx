"use client";

import { useState } from "react";
import { signIn } from "next-auth/react";
import { useSearchParams } from "next/navigation";
import Link from "next/link";
import { Suspense } from "react";

function LoginForm() {
  const params = useSearchParams();
  const from = params.get("from");
  const [form, setForm] = useState({ email: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");

    const res = await signIn("credentials", {
      email: form.email,
      password: form.password,
      redirect: false,
    });

    if (res?.error) {
      setError("Correo o contraseña incorrectos");
      setLoading(false);
      return;
    }

    window.location.href = "/auth/redirect";
  }

  return (
    <main className="min-h-screen bg-[var(--muted)] flex items-center justify-center px-6">
      <div className="w-full max-w-sm">
        <div className="text-center mb-8">
          <div className="flex justify-center mb-4">
            <img
              src="/logo.jpg"
              alt="Peptide Technologies México"
              className="w-36 h-36 rounded-full object-cover ring-2 ring-[var(--primary)]/40 shadow-lg shadow-[var(--primary)]/20"
            />
          </div>
          <Link href="/" className="text-xl font-bold text-white hover:text-[var(--primary)] transition-colors">
            Peptide Technologies <span className="text-[var(--primary)]">México</span>
          </Link>
          <p className="text-[var(--text-muted)] text-sm mt-1">Acceso al portal</p>
        </div>

        <div className="bg-white rounded-2xl border border-[var(--border)] p-8 shadow-sm">
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Correo electrónico
              </label>
              <input
                type="email"
                required
                value={form.email}
                onChange={(e) => setForm((p) => ({ ...p, email: e.target.value }))}
                placeholder="tu@correo.com"
                className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)]"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Contraseña
              </label>
              <input
                type="password"
                required
                value={form.password}
                onChange={(e) => setForm((p) => ({ ...p, password: e.target.value }))}
                placeholder="••••••••"
                className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-[var(--primary)]"
              />
            </div>

            {error && (
              <p className="text-sm text-red-600 bg-red-50 px-4 py-3 rounded-xl">{error}</p>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 rounded-xl font-bold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors disabled:opacity-50"
            >
              {loading ? "Entrando..." : "Entrar →"}
            </button>
          </form>
        </div>

        <p className="text-center text-xs text-gray-400 mt-6">
          <Link href="/" className="hover:text-[var(--primary)]">
            ← Volver al sitio
          </Link>
        </p>
      </div>
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense>
      <LoginForm />
    </Suspense>
  );
}

