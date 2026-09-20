import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Aviso de Privacidad — Peptide Technologies México",
  description: "Aviso de privacidad integral de Peptide Technologies México conforme a la LFPDPPP y regulaciones de COFEPRIS.",
};

const LAST_UPDATED = "6 de junio de 2026";

function Section({ id, title, children }: { id: string; title: string; children: React.ReactNode }) {
  return (
    <section id={id} className="mb-10">
      <h2 className="text-lg font-bold text-gray-900 mb-3 pb-2 border-b border-gray-200">{title}</h2>
      <div className="text-gray-700 text-sm leading-relaxed space-y-3">{children}</div>
    </section>
  );
}

function Table({ headers, rows }: { headers: string[]; rows: string[][] }) {
  return (
    <div className="overflow-x-auto">
      <table className="w-full text-sm border-collapse">
        <thead>
          <tr className="bg-gray-50">
            {headers.map((h) => (
              <th key={h} className="border border-gray-200 px-4 py-2 text-left font-semibold text-gray-700">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={i} className={i % 2 === 0 ? "bg-white" : "bg-gray-50"}>
              {row.map((cell, j) => (
                <td key={j} className="border border-gray-200 px-4 py-2 text-gray-600">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default function AvisoPrivacidadPage() {
  return (
    <main className="min-h-screen bg-gray-50 py-12 px-6">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <Link href="/" className="text-sm text-[var(--primary)] hover:underline mb-4 inline-block">
            ← Volver al inicio
          </Link>
          <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">
            <p className="text-xs font-semibold text-[var(--primary)] uppercase tracking-widest mb-2">
              Peptide Technologies México — Telemedicina
            </p>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Aviso de Privacidad</h1>
            <p className="text-sm text-gray-500">
              Aviso Integral conforme a la <strong>Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP)</strong> y demás regulaciones aplicables.
            </p>
            <div className="mt-4 flex gap-6 text-xs text-gray-400">
              <span>Última actualización: <strong>{LAST_UPDATED}</strong></span>
              <span>Versión: 1.0</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">

          {/* I */}
          <Section id="responsable" title="I. Identidad y Domicilio del Responsable">
            <p>
              <strong>Peptide Technologies México</strong> (en adelante, &quot;Peptide Technologies México&quot; o &quot;el Responsable&quot;), con domicilio en
              Ciudad de México, México, y correo electrónico de contacto:{" "}
              <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">
                privacidad@ptmnovo.mx
              </a>
              , es el responsable del uso y protección de sus datos personales conforme a la LFPDPPP y su Reglamento.
            </p>
            <p>
              Peptide Technologies México opera como una <strong>plataforma tecnológica de telemedicina</strong> que conecta a pacientes con médicos independientes especializados en terapia con péptidos. Peptide Technologies México no es una institución de salud, sino un intermediario tecnológico entre el paciente y el profesional médico independiente.
            </p>
          </Section>

          {/* II */}
          <Section id="datos" title="II. Datos Personales que Recabamos">
            <p>Para la prestación de nuestros servicios, Peptide Technologies México recaba las siguientes categorías de datos personales:</p>

            <div>
              <p className="font-semibold text-gray-800 mb-1">A) Datos de identificación y contacto</p>
              <ul className="list-disc ml-5 space-y-1">
                <li>Nombre completo</li>
                <li>Correo electrónico</li>
                <li>Número de teléfono / WhatsApp</li>
                <li>Dirección IP y fecha/hora de registro</li>
              </ul>
            </div>

            <div>
              <p className="font-semibold text-gray-800 mb-1">
                B) Datos relacionados con la salud{" "}
                <span className="text-red-600 font-bold">(DATOS SENSIBLES)</span>
              </p>
              <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-2 text-xs text-red-700">
                <strong>⚠ Aviso importante:</strong> Los datos de esta categoría son considerados <strong>datos sensibles</strong> conforme al artículo 3, fracción VI de la LFPDPPP. Su tratamiento requiere su <strong>consentimiento expreso, informado y específico</strong>.
              </div>
              <ul className="list-disc ml-5 space-y-1">
                <li>Estado de salud actual y antecedentes médicos</li>
                <li>Condiciones médicas preexistentes</li>
                <li>Medicamentos en uso y alergias</li>
                <li>Peso, talla e índice de masa corporal</li>
                <li>Objetivos y motivos de consulta (respuestas al cuestionario de evaluación)</li>
                <li>Diagnósticos emitidos por el médico durante la consulta</li>
                <li>Protocolos de tratamiento y protocolos de tratamiento</li>
                <li>Notas médicas de seguimiento</li>
                <li>Registros de progreso (peso, síntomas, fotografías cuando aplique)</li>
                <li>Grabaciones o transcripciones de orientaciones médicas (cuando aplique y con consentimiento adicional)</li>
              </ul>
            </div>

            <div>
              <p className="font-semibold text-gray-800 mb-1">C) Datos financieros</p>
              <ul className="list-disc ml-5 space-y-1">
                <li>Referencia de pago y monto de la transacción</li>
                <li>Los datos de tarjeta son procesados directamente por Mercado Pago; Peptide Technologies México no almacena datos bancarios</li>
              </ul>
            </div>
          </Section>

          {/* III */}
          <Section id="finalidades" title="III. Finalidades del Tratamiento">
            <p className="font-semibold text-gray-800">Finalidades primarias (necesarias para la prestación del servicio):</p>
            <ol className="list-decimal ml-5 space-y-1">
              <li>Prestación del servicio de orientación médica por videollamada</li>
              <li>Programación y gestión de citas médicas</li>
              <li>Integración y mantenimiento del expediente clínico electrónico</li>
              <li>Emisión de Protocolos de tratamiento</li>
              <li>Seguimiento clínico y monitoreo del progreso del paciente</li>
              <li>Coordinación con la farmacia para el entrega de protocolos</li>
              <li>Procesamiento de pagos y emisión de comprobantes</li>
              <li>Creación y administración de cuenta de usuario en la plataforma</li>
              <li>Atención a dudas, aclaraciones y soporte técnico</li>
            </ol>

            <p className="font-semibold text-gray-800 mt-3">Finalidades secundarias (no necesarias para el servicio):</p>
            <ul className="list-disc ml-5 space-y-1">
              <li>Envío de comunicaciones informativas y educativas sobre salud y péptidos</li>
              <li>Generación de estadísticas internas anonimizadas para mejora del servicio</li>
              <li>Desarrollo de nuevos programas y funcionalidades de la plataforma</li>
            </ul>
            <p className="text-xs text-gray-500 mt-2">
              Si no desea que sus datos sean tratados para las finalidades secundarias, puede manifestarlo en cualquier momento enviando un correo a{" "}
              <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">privacidad@ptmnovo.mx</a>.
              La negativa para estas finalidades no afectará la prestación del servicio principal.
            </p>
          </Section>

          {/* IV */}
          <Section id="consentimiento" title="IV. Consentimiento para Datos Sensibles">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p>
                De conformidad con el artículo 9 de la LFPDPPP, el tratamiento de datos sensibles requiere el <strong>consentimiento expreso y por escrito del titular</strong>. Dicho consentimiento se recaba en el momento en que usted acepta el presente Aviso de Privacidad mediante la casilla de aceptación en nuestro proceso de registro y pago, cuya marca queda registrada con fecha, hora y dirección IP en nuestros sistemas.
              </p>
              <p className="mt-2">
                Al otorgar su consentimiento, usted declara haber leído, entendido y aceptado íntegramente el presente Aviso de Privacidad, incluyendo el tratamiento de sus datos sensibles de salud para las finalidades primarias aquí descritas.
              </p>
            </div>
          </Section>

          {/* V */}
          <Section id="transferencias" title="V. Transferencias de Datos Personales">
            <p>Sus datos personales podrán ser compartidos con los siguientes terceros para la prestación del servicio:</p>
            <Table
              headers={["Destinatario", "Finalidad", "¿Requiere consentimiento adicional?"]}
              rows={[
                ["Médicos registrados en Peptide Technologies México", "Prestación del servicio de orientación médica y expediente clínico", "No — es parte esencial del servicio"],
                ["Péptidos y Suplementos México (farmacia)", "Surtimiento de Protocolos de tratamiento emitidas durante la orientación médica", "No — es parte esencial del servicio"],
                ["Daily.co (proveedor de videollamadas)", "Habilitación de la orientación médica en video", "No — es parte esencial del servicio"],
                ["Mercado Pago S. de R.L. de C.V.", "Procesamiento seguro de pagos", "No — es necesario para completar la transacción"],
                ["Autoridades competentes (COFEPRIS, SSA, SABG, etc.)", "Cumplimiento de obligaciones legales", "No — obligación legal"],
              ]}
            />
            <p className="text-xs text-gray-500 mt-2">
              Peptide Technologies México no vende, alquila ni comercializa sus datos personales a terceros con fines publicitarios o comerciales ajenos al servicio.
            </p>
          </Section>

          {/* VI */}
          <Section id="seguridad" title="VI. Medidas de Seguridad">
            <p>Peptide Technologies México implementa las siguientes medidas de seguridad técnicas, físicas y administrativas para proteger sus datos:</p>
            <ul className="list-disc ml-5 space-y-1">
              <li>Cifrado de comunicaciones mediante TLS/SSL en toda la plataforma</li>
              <li>Almacenamiento de contraseñas con algoritmo de hash bcrypt (no reversible)</li>
              <li>Acceso a datos de salud restringido exclusivamente a médicos autorizados y administradores con credenciales verificadas</li>
              <li>Base de datos alojada en infraestructura segura con acceso por red privada</li>
              <li>Autenticación con tokens JWT de vida limitada</li>
              <li>Registro de accesos y actividad administrativa en el sistema</li>
              <li>Acuerdos de confidencialidad con todos los médicos y proveedores de tecnología</li>
            </ul>
          </Section>

          {/* VII */}
          <Section id="arco" title="VII. Derechos ARCO">
            <p>Usted tiene derecho a ejercer en cualquier momento los siguientes derechos sobre sus datos personales:</p>
            <ul className="list-none space-y-2">
              {[
                ["Acceso", "Conocer qué datos personales poseemos, para qué los utilizamos y las condiciones de su uso."],
                ["Rectificación", "Solicitar la corrección de sus datos cuando sean inexactos, incompletos o desactualizados."],
                ["Cancelación", "Solicitar la eliminación de sus datos de nuestros sistemas cuando ya no sean necesarios o cuando retire su consentimiento, salvo obligación legal de conservarlos."],
                ["Oposición", "Oponerse al tratamiento de sus datos para finalidades secundarias o cuando exista una causa legítima para ello."],
              ].map(([right, desc]) => (
                <li key={right} className="flex gap-2">
                  <span className="font-semibold text-gray-800 w-24 flex-shrink-0">{right}:</span>
                  <span>{desc}</span>
                </li>
              ))}
            </ul>
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4 mt-3">
              <p className="font-semibold text-gray-800 mb-1">¿Cómo ejercer sus derechos?</p>
              <p>Envíe un correo a <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">privacidad@ptmnovo.mx</a> con:</p>
              <ol className="list-decimal ml-5 mt-1 space-y-0.5 text-xs">
                <li>Nombre completo y correo electrónico registrado en la plataforma</li>
                <li>Descripción clara del derecho que desea ejercer</li>
                <li>Copia de identificación oficial vigente</li>
                <li>Cualquier documento que facilite la localización de sus datos</li>
              </ol>
              <p className="mt-2 text-xs">
                Peptide Technologies México dará respuesta en un plazo máximo de <strong>20 días hábiles</strong> a partir de la recepción de la solicitud.
              </p>
            </div>
          </Section>

          {/* VIII */}
          <Section id="retencion" title="VIII. Periodo de Conservación de Datos">
            <p>Sus datos personales serán conservados durante los siguientes plazos:</p>
            <Table
              headers={["Tipo de dato", "Periodo de conservación", "Base legal"]}
              rows={[
                ["Expediente clínico electrónico (diagnósticos, Protocolos, notas)", "Mínimo 5 años", "NOM-004-SSA3-2012"],
                ["Datos de cuenta (nombre, email, contraseña)", "Mientras la cuenta esté activa + 1 año tras cancelación", "LFPDPPP Art. 11"],
                ["Registros de consentimiento de privacidad", "5 años", "LFPDPPP Art. 16"],
                ["Comprobantes de pago", "5 años", "Código Fiscal de la Federación"],
                ["Datos de contacto y comunicaciones", "2 años tras última interacción", "LFPDPPP Art. 11"],
              ]}
            />
            <p className="text-xs text-gray-500 mt-2">
              Transcurridos estos plazos, sus datos serán eliminados de forma segura o anonimizados cuando sea técnicamente posible.
            </p>
          </Section>

          {/* IX */}
          <Section id="revocacion" title="IX. Revocación del Consentimiento">
            <p>
              Puede revocar su consentimiento para el tratamiento de sus datos personales sensibles en cualquier momento, salvo que dicho tratamiento sea necesario para cumplir con una obligación legal o para la defensa de reclamaciones.
            </p>
            <p>
              La revocación deberá solicitarse por escrito a{" "}
              <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">privacidad@ptmnovo.mx</a>.
              Tenga en cuenta que la revocación puede implicar la imposibilidad de continuar prestando el servicio médico, y no tendrá efectos retroactivos sobre los datos ya tratados.
            </p>
          </Section>

          {/* X */}
          <Section id="cookies" title="X. Uso de Cookies y Tecnologías de Rastreo">
            <p>
              La plataforma Peptide Technologies México utiliza <strong>cookies esenciales</strong> para el funcionamiento del sistema de autenticación y sesiones de usuario. Estas cookies son estrictamente necesarias para la operación del servicio y no pueden desactivarse.
            </p>
            <p>
              Peptide Technologies México <strong>no utiliza</strong> cookies de seguimiento publicitario, análisis de comportamiento de terceros, ni comparte datos de navegación con redes publicitarias.
            </p>
          </Section>

          {/* XI */}
          <Section id="cambios" title="XI. Cambios al Aviso de Privacidad">
            <p>
              Peptide Technologies México se reserva el derecho de actualizar el presente Aviso de Privacidad en cualquier momento para reflejar cambios en nuestros servicios, en la legislación aplicable o en nuestras prácticas de privacidad.
            </p>
            <p>
              Cualquier modificación será publicada en esta página con la fecha de actualización correspondiente. En caso de cambios sustanciales que afecten el tratamiento de datos sensibles, le notificaremos por correo electrónico al registrado en su cuenta.
            </p>
          </Section>

          {/* XII */}
          <Section id="contacto" title="XII. Contacto y Autoridad Competente">
            <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
              <p className="font-semibold text-gray-800 mb-2">Responsable de Protección de Datos — Peptide Technologies México</p>
              <p>Correo: <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">privacidad@ptmnovo.mx</a></p>
              <p className="mt-1">Horario de atención: Lunes a Viernes, 9:00 a 18:00 hrs (Hora Ciudad de México)</p>
            </div>
            <p className="mt-3">
              Si considera que sus derechos de protección de datos han sido vulnerados, puede presentar una queja ante la{" "}
              <strong>Secretaría de Administración y Buena Gobernanza (SABG)</strong>, autoridad competente en materia de protección de datos personales en México.
            </p>
          </Section>

          {/* Footer */}
          <div className="border-t border-gray-200 pt-6 mt-6 text-center">
            <p className="text-xs text-gray-400">
              © {new Date().getFullYear()} Peptide Technologies México · Todos los derechos reservados ·{" "}
              <Link href="/terminos-y-condiciones" className="hover:text-[var(--primary)]">Términos y Condiciones</Link>
              {" "}· Aviso conforme a la <strong>LFPDPPP</strong>, <strong>NOM-004-SSA3</strong>, <strong>NOM-024-SSA3</strong> y regulaciones de <strong>COFEPRIS</strong>
            </p>
            <Link href="/" className="text-xs text-[var(--primary)] hover:underline mt-2 inline-block">
              Volver al inicio →
            </Link>
          </div>

        </div>
      </div>
    </main>
  );
}


