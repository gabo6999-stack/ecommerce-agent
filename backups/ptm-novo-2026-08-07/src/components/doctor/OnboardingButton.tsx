"use client";

import { useState } from "react";

export default function OnboardingButton({
  doctorId,
  label,
}: {
  doctorId: string;
  label: string;
}) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleClick() {
    setLoading(true);
    setError("");
    try {
      const res = await fetch("/api/connect/onboard", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ doctorId }),
      });
      const data = await res.json();
      if (!res.ok || !data.url) throw new Error(data.error ?? "No se pudo iniciar el onboarding");
      // Redirige al formulario seguro de Stripe (KYC).
      window.location.href = data.url;
    } catch (err) {
      setError(err instanceof Error ? err.message : "Error inesperado");
      setLoading(false);
    }
  }

  return (
    <div>
      <button
        onClick={handleClick}
        disabled={loading}
        className="inline-flex items-center gap-2 px-5 py-3 rounded-xl text-sm font-bold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors disabled:opacity-50"
      >
        {loading ? "Redirigiendo a Stripe..." : label}
      </button>
      {error && (
        <p className="text-sm text-red-600 mt-2">{error}</p>
      )}
    </div>
  );
}
