import Link from "next/link";
import Quiz from "@/components/quiz/Quiz";

const serviceSchema = {
  "@context": "https://schema.org",
  "@type": "MedicalWebPage",
  "name": "Consulta Médica en Línea — Terapia con Péptidos | PTM Novo",
  "url": "https://ptmnovo.com",
  "description": "Consulta médica de telemedicina especializada en péptidos en México. Protocolos para pérdida de peso, rendimiento deportivo y longevidad.",
  "reviewedBy": {
    "@type": "Person",
    "name": "Dr. Antonio Gavito Hernández",
    "jobTitle": "Médico Especialista en Medicina Funcional y Terapia con Péptidos"
  },
  "medicalAudience": { "@type": "Patient" },
  "inLanguage": "es-MX"
};

export default function HomePage() {
  return (
    <main className="flex flex-col min-h-screen">
      <script
        type="application/ld+json"
        dangerouslySetInnerHTML={{ __html: JSON.stringify(serviceSchema) }}
      />
      {/* NAV */}
      <nav className="w-full px-6 py-3 flex items-center justify-between border-b border-[var(--border)] bg-[var(--sidebar)]/95 backdrop-blur sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <img src="/logo.jpg" alt="Logo" className="w-20 h-20 rounded-full object-cover ring-2 ring-[var(--primary)]/40 shadow-md shadow-[var(--primary)]/20" />
          <span className="text-lg font-bold text-white">Peptide Technologies <span className="text-[var(--primary)]">México</span></span>
        </div>
        <div className="flex items-center gap-4">
          <Link href="/login" className="text-sm text-gray-600 hover:text-[var(--primary)]">
            Iniciar sesión
          </Link>
          <Link
            href="#quiz"
            className="text-sm font-semibold px-4 py-2 rounded-lg text-white bg-[var(--primary)]"
          >
            Comenzar
          </Link>
        </div>
      </nav>

      {/* HERO */}
      <section className="w-full px-6 py-20 text-center bg-[var(--primary-dark)]">
        <div className="max-w-3xl mx-auto">
          <span className="inline-block text-sm font-medium px-3 py-1 rounded-full mb-6 text-[var(--primary)] bg-[var(--accent-light)]">
            Telemedicina especializada en péptidos 🇲🇽
          </span>
          <h1 className="text-4xl md:text-5xl font-bold text-white leading-tight mb-6">
            La primera clínica mexicana de péptidos en línea
          </h1>
          <p className="text-lg text-gray-300 mb-10 max-w-2xl mx-auto">
            Médicos certificados en terapia de péptidos. Orientación médica desde casa, protocolo
            personalizado y tus péptidos en la puerta. Sin filas, sin esperas.
          </p>
          <Link
            href="#quiz"
            className="inline-block px-8 py-4 rounded-xl text-lg font-bold text-white bg-[var(--accent)] hover:opacity-90 transition-opacity"
          >
            Iniciar evaluación gratuita →
          </Link>
          <p className="mt-4 text-sm text-gray-400">Orientación médica inicial desde $1,500 MXN · Sin costos ocultos</p>
        </div>
      </section>

      {/* PROGRAMAS */}
      <section className="w-full px-6 py-16 bg-[var(--muted)]">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">Nuestros programas</h2>
          <p className="text-center text-gray-500 mb-12">Dos enfoques. Un mismo estándar médico.</p>
          <div className="grid md:grid-cols-2 gap-6">
            <div className="bg-white rounded-2xl p-8 border border-[var(--border)] hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">⚖️</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Pérdida de Peso</h3>
              <p className="text-gray-500 mb-4 text-sm">
                Semaglutide, Tirzepatide y protocolos GLP-1 compuestos prescritos por médicos.
                Seguimiento real cada 4 semanas.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                {["Orientación médica personalizada", "Protocolo de tratamiento personalizado", "Péptidos en tu domicilio", "Seguimiento mensual incluido"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <span className="text-[var(--accent)]">✓</span> {item}
                  </li>
                ))}
              </ul>
            </div>
            <div className="bg-white rounded-2xl p-8 border border-[var(--border)] hover:shadow-lg transition-shadow">
              <div className="text-4xl mb-4">⚡</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">Péptidos & Longevidad</h3>
              <p className="text-gray-500 mb-4 text-sm">
                BPC-157, CJC-1295, TB-500, Epithalon y más. Protocolos para recuperación,
                rendimiento, sueño y antiaging.
              </p>
              <ul className="space-y-2 text-sm text-gray-600">
                {["Stack personalizado por objetivo", "Médico especialista en péptidos", "Péptidos farmacéuticos certificados", "Ajuste de protocolo mensual"].map((item) => (
                  <li key={item} className="flex items-center gap-2">
                    <span className="text-[var(--accent)]">✓</span> {item}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* CÓMO FUNCIONA */}
      <section className="w-full px-6 py-16 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-gray-900 mb-4">¿Cómo funciona?</h2>
          <p className="text-center text-gray-500 mb-12">Tres pasos. Sin complicaciones.</p>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { step: "01", title: "Evalúate", desc: "Responde 5 preguntas rápidas. Te decimos si eres candidato y qué programa es para ti.", icon: "📋" },
              { step: "02", title: "Orientación", desc: "Agenda tu orientación médica con un especialista en péptidos. Paga $1,500 MXN y listo.", icon: "👨‍⚕️" },
              { step: "03", title: "Recibe", desc: "Tu médico emite el protocolo y tus péptidos llegan directo a casa.", icon: "📦" },
            ].map((item) => (
              <div key={item.step} className="text-center">
                <div className="text-4xl mb-3">{item.icon}</div>
                <div className="text-xs font-bold text-[var(--accent)] mb-1 tracking-widest">PASO {item.step}</div>
                <h3 className="text-lg font-bold text-gray-900 mb-2">{item.title}</h3>
                <p className="text-gray-500 text-sm">{item.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* QUIZ */}
      <section id="quiz" className="w-full px-6 py-20 bg-[var(--muted)]">
        <div className="max-w-xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold text-gray-900 mb-3">Inicia tu evaluación gratuita</h2>
            <p className="text-gray-500">5 preguntas · 2 minutos · Sin compromiso</p>
          </div>
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--border)]">
            <Quiz />
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="w-full px-6 py-10 border-t border-[var(--border)] bg-white mt-auto">
        <div className="max-w-4xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div>
            <span className="font-bold text-[var(--primary)]">Peptide Technologies México</span>
            <p className="text-xs text-gray-400 mt-1">
              Plataforma de telemedicina especializada en péptidos · México
            </p>
          </div>
          <div className="flex gap-6 text-sm text-gray-500">
            <Link href="/aviso-de-privacidad" className="hover:text-[var(--primary)]">Privacidad</Link>
            <Link href="/terminos-y-condiciones" className="hover:text-[var(--primary)]">Términos</Link>
            <Link href="/contacto" className="hover:text-[var(--primary)]">Contacto</Link>
          </div>
        </div>
      </footer>
    </main>
  );
}


