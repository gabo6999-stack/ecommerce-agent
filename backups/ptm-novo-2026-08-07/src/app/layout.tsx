import type { Metadata } from "next";
import { Geist } from "next/font/google";
import "./globals.css";

const geist = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Peptide Technologies México — Orientación médica especializada en péptidos",
  description:
    "La primera plataforma mexicana de telemedicina especializada en péptidos. Médicos certificados, protocolos de clase mundial y tus péptidos en casa.",
};

const organizationSchema = {
  "@context": "https://schema.org",
  "@type": "MedicalOrganization",
  "name": "PTM Novo — Peptide Technologies México",
  "url": "https://ptmnovo.com",
  "description": "La primera plataforma mexicana de telemedicina especializada en terapia con péptidos. Médicos certificados, consulta en línea y protocolos personalizados.",
  "medicalSpecialty": "Medicina Funcional y Terapia con Péptidos",
  "availableService": [
    {
      "@type": "MedicalTherapy",
      "name": "Consulta de Telemedicina en Péptidos",
      "description": "Consulta médica en línea especializada en terapia con péptidos, protocolos de pérdida de peso y rendimiento deportivo."
    }
  ],
  "founder": {
    "@type": "Person",
    "name": "Dr. Antonio Gavito Hernández",
    "jobTitle": "Médico Especialista en Medicina Funcional y Terapia con Péptidos",
    "sameAs": "https://peptidosysuplementos.mx"
  },
  "areaServed": {
    "@type": "Country",
    "name": "México"
  },
  "inLanguage": "es-MX"
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className={`${geist.variable} h-full antialiased`}>
      <head>
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{ __html: JSON.stringify(organizationSchema) }}
        />
      </head>
      <body className="min-h-full flex flex-col">{children}</body>
    </html>
  );
}

