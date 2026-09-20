"use client";

import Link from "next/link";
import { Suspense } from "react";
import { useSearchParams } from "next/navigation";

function FailureContent() {
  const params = useSearchParams();
  const program = params.get("program") ?? "LONGEVITY";

  return (
    <main className="min-h-screen bg-[var(--muted)] flex items-center justify-center px-6 py-16">
      <div className="max-w-md w-full bg-white rounded-2xl border border-[var(--border)] shadow-sm p-10 text-center">
        <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mx-auto mb-6">
          <span className="text-3xl">❌</span>
        </div>
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Pago no procesado</h1>
        <p className="text-gray-500 text-sm mb-8">
          No se pudo completar el pago. Puedes intentarlo de nuevo o usar otro método de pago.
          No se realizó ningún cargo.
        </p>

        <div className="space-y-3">
          <Link
            href={`/checkout?program=${program}`}
            className="block w-full py-3 rounded-xl font-semibold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] transition-colors text-sm"
          >
            Intentar de nuevo →
          </Link>
          <Link
            href="/"
            className="block w-full py-3 rounded-xl font-semibold text-gray-600 border border-[var(--border)] hover:bg-[var(--muted)] transition-colors text-sm"
          >
            Volver al inicio
          </Link>
        </div>
      </div>
    </main>
  );
}

export default function PagoFallidoPage() {
  return (
    <Suspense>
      <FailureContent />
    </Suspense>
  );
}
