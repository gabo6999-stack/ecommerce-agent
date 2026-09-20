import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Términos y Condiciones — Peptide Technologies México",
  description: "Términos y Condiciones de uso de la plataforma de telemedicina Peptide Technologies México, conforme a la legislación mexicana aplicable.",
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

function Clause({ num, title, children }: { num: string; title: string; children: React.ReactNode }) {
  return (
    <div className="mb-4">
      <p className="font-semibold text-gray-800 mb-1">{num}. {title}</p>
      <div className="text-gray-700 text-sm leading-relaxed space-y-2 pl-4 border-l-2 border-[var(--border)]">
        {children}
      </div>
    </div>
  );
}

export default function TerminosPage() {
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
              Peptide Technologies México — Plataforma de Telemedicina
            </p>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Términos y Condiciones</h1>
            <p className="text-sm text-gray-500">
              Contrato de prestación de servicios en modalidad electrónica conforme al{" "}
              <strong>Código de Comercio</strong>, <strong>Código Civil Federal</strong>,{" "}
              <strong>Ley Federal de Protección al Consumidor (LFPC)</strong>,{" "}
              <strong>Ley General de Salud (LGS)</strong>,{" "}
              <strong>NOM-004-SSA3-2012</strong>,{" "}
              <strong>NOM-024-SSA3-2012</strong> y demás disposiciones aplicables.
            </p>
            <div className="mt-4 flex flex-wrap gap-6 text-xs text-gray-400">
              <span>Última actualización: <strong>{LAST_UPDATED}</strong></span>
              <span>Versión: 1.0</span>
              <span>Jurisdicción: Estados Unidos Mexicanos</span>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm">

          {/* Aviso importante */}
          <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 mb-8 text-sm text-blue-700">
            <p className="font-semibold mb-1">⚠️ Lea detenidamente antes de utilizar la plataforma</p>
            <p>
              Al registrarse, acceder o utilizar los servicios de Peptide Technologies México, usted manifiesta
              haber leído, comprendido y aceptado en su totalidad los presentes Términos y Condiciones,
              así como nuestro{" "}
              <Link href="/aviso-de-privacidad" className="underline font-semibold">Aviso de Privacidad</Link>.
              Si no está de acuerdo con alguna disposición, no utilice la plataforma.
            </p>
          </div>

          {/* I */}
          <Section id="objeto" title="I. Objeto y Naturaleza del Servicio">
            <p>
              <strong>Peptide Technologies México</strong> (en adelante &quot;la Plataforma&quot;) opera exclusivamente
              como <strong>intermediario tecnológico</strong> que conecta a usuarios (pacientes) con médicos
              independientes certificados en terapia con péptidos. La Plataforma <strong>no es una institución
              de salud</strong>, hospital, clínica ni establecimiento de atención médica en los términos del
              artículo 34 de la Ley General de Salud.
            </p>
            <p>
              Los servicios médicos son prestados directamente por el médico independiente registrado en la
              plataforma, quien actúa en ejercicio de su cédula profesional y asume plena responsabilidad
              ética, técnica y legal sobre el acto médico conforme a los artículos 79 y 83 de la LGS.
            </p>
            <p>
              La Plataforma facilita: (a) consultas médicas por telemedicina vía videoconferencia;
              (b) emisión de Protocolos de tratamiento; (c) coordinación con proveedores de péptidos
              farmacéuticos; (d) seguimiento del tratamiento.
            </p>
          </Section>

          {/* II */}
          <Section id="telemedicina" title="II. Telemedicina — Marco Legal y Limitaciones">
            <Clause num="2.1" title="Fundamento normativo">
              <p>
                Los servicios de telemedicina se prestan de conformidad con el artículo 6 fracción VI bis
                de la LGS, los Lineamientos para la Práctica de la Telemedicina emitidos por la Secretaría
                de Salud, y la <strong>NOM-024-SSA3-2012</strong> sobre sistemas de información de
                registro electrónico para la salud.
              </p>
            </Clause>
            <Clause num="2.2" title="Consentimiento informado">
              <p>
                El usuario manifiesta su consentimiento informado para la atención médica a distancia al
                confirmar su cita, reconociendo las características, alcances y limitaciones inherentes
                a la modalidad de telemedicina, conforme al artículo 80 de la LGS y la NOM-004-SSA3-2012.
              </p>
            </Clause>
            <Clause num="2.3" title="Limitaciones del servicio">
              <p>La telemedicina <strong>no sustituye</strong> la atención médica presencial en situaciones de urgencia,
              emergencia médica o cuando el médico determine que la condición clínica requiere valoración física.
              En caso de emergencia médica llame al <strong>911</strong> o acuda al servicio de urgencias más cercano.</p>
            </Clause>
            <Clause num="2.4" title="Expediente clínico electrónico">
              <p>
                El expediente clínico generado en la Plataforma se rige por la{" "}
                <strong>NOM-004-SSA3-2012</strong>, será conservado por un mínimo de{" "}
                <strong>5 años</strong> a partir de la última consulta, y puede ser consultado por el
                paciente en ejercicio de sus derechos ARCO conforme a la LFPDPPP.
              </p>
            </Clause>
          </Section>

          {/* III */}
          <Section id="registro" title="III. Registro y Cuenta de Usuario">
            <Clause num="3.1" title="Requisitos de registro">
              <p>
                Para utilizar la Plataforma el usuario debe: (a) ser mayor de 18 años o contar con
                representación legal de padre/tutor; (b) proporcionar información verídica y completa;
                (c) contar con acceso a internet y dispositivo compatible; (d) residir en los Estados
                Unidos Mexicanos.
              </p>
            </Clause>
            <Clause num="3.2" title="Responsabilidad de la cuenta">
              <p>
                El usuario es el único responsable de mantener la confidencialidad de sus credenciales
                de acceso. Deberá notificar de inmediato a{" "}
                <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">
                  privacidad@ptmnovo.mx
                </a>{" "}
                ante cualquier uso no autorizado de su cuenta.
              </p>
            </Clause>
            <Clause num="3.3" title="Veracidad de información médica">
              <p>
                El usuario se compromete a proporcionar información médica veraz y completa, incluyendo
                condiciones preexistentes, medicamentos actuales y alergias. La omisión o falsedad de
                información médica relevante libera de responsabilidad al médico y a la Plataforma por
                consecuencias derivadas de dicha omisión.
              </p>
            </Clause>
          </Section>

          {/* IV */}
          <Section id="pagos" title="IV. Precios, Pagos y Política de Reembolsos">
            <Clause num="4.1" title="Precio del servicio">
              <p>
                El costo de la consulta médica es de <strong>$1,500.00 MXN (mil quinientos pesos 00/100 M.N.)</strong>{" "}
                por sesión. Los precios incluyen IVA conforme al artículo 14 de la Ley del Impuesto al
                Valor Agregado. La Plataforma se reserva el derecho de modificar precios con notificación
                previa de al menos 15 días naturales.
              </p>
            </Clause>
            <Clause num="4.2" title="Procesamiento de pagos">
              <p>
                Los pagos se procesan a través de <strong>Mercado Pago</strong>, plataforma regulada por
                la Comisión Nacional Bancaria y de Valores (CNBV). La Plataforma no almacena datos de
                tarjetas bancarias. El comprobante de pago constituye el contrato de prestación de servicios
                en términos del artículo 1803 del Código Civil Federal.
              </p>
            </Clause>
            <Clause num="4.3" title="Política de cancelación y reembolso">
              <p>Conforme a la LFPC (art. 76 bis) y en beneficio del consumidor:</p>
              <ul className="list-disc list-inside space-y-1 mt-1">
                <li><strong>Cancelación con +24 horas de anticipación:</strong> reembolso del 100%</li>
                <li><strong>Cancelación con 12-24 horas de anticipación:</strong> reembolso del 50%</li>
                <li><strong>Cancelación con menos de 12 horas:</strong> sin reembolso, salvo causa de fuerza mayor</li>
                <li><strong>Falla técnica imputable a la Plataforma:</strong> reagendamiento gratuito o reembolso total</li>
                <li><strong>Inasistencia del médico:</strong> reagendamiento gratuito con el médico disponible más próximo</li>
              </ul>
              <p className="mt-2">
                Las solicitudes de reembolso se tramitan a{" "}
                <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">
                  privacidad@ptmnovo.mx
                </a>{" "}
                en un plazo máximo de <strong>10 días hábiles</strong>.
              </p>
            </Clause>
            <Clause num="4.4" title="Derecho de retracto">
              <p>
                Conforme al artículo 56 de la LFPC, el consumidor tiene derecho a cancelar la compra
                dentro de los primeros <strong>5 días hábiles</strong> desde el pago si aún no ha
                tomado la consulta, con reembolso total sin penalización.
              </p>
            </Clause>
          </Section>

          {/* V */}
          <Section id="obligaciones" title="V. Derechos y Obligaciones de las Partes">
            <Clause num="5.1" title="Obligaciones del usuario">
              <ul className="list-disc list-inside space-y-1">
                <li>Proporcionar información médica veraz y actualizada</li>
                <li>Asistir puntualmente a las consultas programadas</li>
                <li>Utilizar la plataforma exclusivamente para fines lícitos</li>
                <li>No compartir su sesión de videoconferencia con terceros no autorizados</li>
                <li>Seguir las indicaciones médicas bajo su propia responsabilidad</li>
                <li>Mantener la confidencialidad de las indicaciones y Protocolos de su expediente</li>
              </ul>
            </Clause>
            <Clause num="5.2" title="Obligaciones de la Plataforma">
              <ul className="list-disc list-inside space-y-1">
                <li>Garantizar la disponibilidad del servicio con al menos 99% de uptime mensual</li>
                <li>Verificar la cédula profesional de todos los médicos registrados (SSA/Dirección General de Profesiones)</li>
                <li>Proteger los datos personales conforme a la LFPDPPP</li>
                <li>Conservar el expediente clínico electrónico conforme a NOM-004-SSA3-2012</li>
                <li>Proporcionar comprobante de pago conforme al CFF</li>
                <li>Atender quejas ante PROFECO dentro de los plazos legales</li>
              </ul>
            </Clause>
            <Clause num="5.3" title="Derechos del usuario como consumidor">
              <p>
                Conforme a la LFPC, el usuario tiene derecho a: información veraz sobre el servicio;
                protección contra prácticas abusivas; cancelación conforme a lo establecido en la
                Cláusula 4.3; presentar reclamaciones ante la{" "}
                <strong>PROFECO (Procuraduría Federal del Consumidor)</strong>{" "}
                al teléfono <strong>800 468 8722</strong> o en{" "}
                <a href="https://www.gob.mx/profeco" target="_blank" rel="noopener noreferrer" className="text-[var(--primary)] underline">
                  www.gob.mx/profeco
                </a>.
              </p>
            </Clause>
          </Section>

          {/* VI */}
          <Section id="responsabilidad" title="VI. Limitación de Responsabilidad">
            <Clause num="6.1" title="Naturaleza tecnológica">
              <p>
                La Plataforma actúa exclusivamente como intermediario tecnológico. La responsabilidad
                por el acto médico, diagnóstico, tratamiento y protocolo recae íntegramente en el
                médico independiente que presta el servicio, de conformidad con los artículos 79, 83
                y 84 de la LGS.
              </p>
            </Clause>
            <Clause num="6.2" title="Fuerza mayor">
              <p>
                La Plataforma no será responsable por incumplimientos derivados de caso fortuito o
                fuerza mayor conforme al artículo 2111 del Código Civil Federal, incluyendo fallas
                en el suministro de internet del usuario, interrupciones de servicios de terceros
                (proveedores de video, procesadores de pago) o causas ajenas al control de la Plataforma.
              </p>
            </Clause>
            <Clause num="6.3" title="Límite de responsabilidad económica">
              <p>
                En ningún caso la responsabilidad total de la Plataforma por daños directos excederá
                el monto pagado por el usuario en los últimos <strong>3 meses</strong> anteriores al
                evento que generó el daño. La Plataforma no responde por daños indirectos, lucro cesante
                o daño moral salvo dolo comprobado.
              </p>
            </Clause>
            <Clause num="6.4" title="Péptidos y productos farmacéuticos">
              <p>
                Los péptidos y suplementos adquiridos a través de proveedor vinculado
                (peptidosysuplementos.mx) están sujetos a los términos y condiciones de dicho
                proveedor. La Plataforma no garantiza la disponibilidad de productos específicos
                ni es responsable por retrasos en la entrega.
              </p>
            </Clause>
          </Section>

          {/* VII */}
          <Section id="propiedad" title="VII. Propiedad Intelectual">
            <p>
              Todos los contenidos de la Plataforma, incluyendo marca, logotipos, software, diseño,
              textos y materiales educativos son propiedad de Peptide Technologies México o se
              utilizan bajo licencia, y están protegidos por la{" "}
              <strong>Ley Federal del Derecho de Autor</strong> y la{" "}
              <strong>Ley de la Propiedad Industrial</strong>.
            </p>
            <p>
              Se otorga al usuario una licencia personal, no exclusiva, intransferible y revocable
              para acceder y utilizar la Plataforma exclusivamente para los fines establecidos en
              estos Términos. Queda expresamente prohibida la reproducción, modificación, distribución
              o ingeniería inversa del software de la Plataforma.
            </p>
          </Section>

          {/* VIII */}
          <Section id="privacidad" title="VIII. Protección de Datos Personales">
            <p>
              El tratamiento de datos personales, incluyendo datos de salud de carácter sensible,
              se rige por nuestro{" "}
              <Link href="/aviso-de-privacidad" className="text-[var(--primary)] underline font-semibold">
                Aviso de Privacidad Integral
              </Link>{" "}
              conforme a la <strong>LFPDPPP</strong>, su Reglamento y los Lineamientos del INAI.
              Los datos clínicos son tratados conforme a la <strong>NOM-024-SSA3-2012</strong> y
              conservados por el periodo establecido en la <strong>NOM-004-SSA3-2012</strong>.
            </p>
          </Section>

          {/* IX */}
          <Section id="conducta" title="IX. Conducta Prohibida">
            <p>Queda expresamente prohibido a los usuarios:</p>
            <ul className="list-disc list-inside space-y-1 mt-1">
              <li>Suplantar la identidad de otra persona</li>
              <li>Proporcionar información médica falsa con el fin de obtener protocolos</li>
              <li>Intentar acceder a expedientes clínicos de otros pacientes</li>
              <li>Grabar las consultas médicas sin consentimiento expreso del médico</li>
              <li>Utilizar la plataforma para fines distintos a la atención médica personal</li>
              <li>Compartir o revender acceso a la plataforma</li>
              <li>Realizar ingeniería inversa, ataques informáticos o afectar la operación del servicio</li>
            </ul>
            <p className="mt-2">
              El incumplimiento faculta a la Plataforma a suspender o cancelar la cuenta sin reembolso
              y a ejercer las acciones legales correspondientes.
            </p>
          </Section>

          {/* X */}
          <Section id="menores" title="X. Uso por Menores de Edad">
            <p>
              El servicio está dirigido a personas mayores de 18 años. Los menores de edad únicamente
              podrán utilizar la plataforma con el consentimiento expreso y supervisión de su padre,
              madre o tutor legal, quien asumirá la responsabilidad por el uso del servicio y deberá
              completar el registro en nombre del menor, de conformidad con el artículo 23 del
              Código Civil Federal.
            </p>
          </Section>

          {/* XI */}
          <Section id="modificaciones" title="XI. Modificaciones a los Términos">
            <p>
              Peptide Technologies México se reserva el derecho de modificar los presentes Términos
              y Condiciones en cualquier momento. Las modificaciones serán notificadas al usuario mediante:
              (a) publicación en la Plataforma con al menos <strong>15 días naturales</strong> de
              anticipación; (b) correo electrónico al registrado en la cuenta.
            </p>
            <p>
              El uso continuado de la Plataforma después de la fecha de vigencia de los cambios
              constituirá aceptación de los nuevos términos. Si el usuario no acepta los cambios,
              podrá solicitar la cancelación de su cuenta sin penalización.
            </p>
          </Section>

          {/* XII */}
          <Section id="terminacion" title="XII. Suspensión y Terminación">
            <p>
              La Plataforma podrá suspender o terminar el acceso del usuario en los siguientes supuestos:
              incumplimiento de los presentes Términos; uso fraudulento; solicitud del propio usuario;
              disposición legal o requerimiento de autoridad competente.
            </p>
            <p>
              La terminación no afecta los derechos ya adquiridos por el usuario respecto a consultas
              pagadas y pendientes de tomar, las cuales serán reembolsadas conforme a la Cláusula 4.3.
              El expediente clínico seguirá siendo conservado por el periodo legal establecido en la
              NOM-004-SSA3-2012.
            </p>
          </Section>

          {/* XIII */}
          <Section id="jurisdiccion" title="XIII. Ley Aplicable y Jurisdicción">
            <p>
              Los presentes Términos y Condiciones se rigen e interpretan conforme a las leyes de los
              <strong> Estados Unidos Mexicanos</strong>. Para la resolución de cualquier controversia
              derivada de su interpretación o cumplimiento, las partes se someten expresamente a la
              jurisdicción de los tribunales competentes de la{" "}
              <strong>Ciudad de México</strong>, renunciando a cualquier otro fuero que pudiera
              corresponderles por razón de su domicilio presente o futuro.
            </p>
            <p>
              Sin perjuicio de lo anterior, el usuario podrá acudir a la{" "}
              <strong>PROFECO</strong> para la resolución de controversias en materia de consumo,
              conforme a los artículos 116 y 117 de la LFPC.
            </p>
          </Section>

          {/* XIV */}
          <Section id="contacto" title="XIV. Contacto y Atención al Usuario">
            <p>Para cualquier duda, aclaración o queja respecto a estos Términos:</p>
            <div className="bg-gray-50 rounded-xl p-5 mt-3 space-y-2 text-sm">
              <p className="font-semibold text-gray-800">Peptide Technologies México</p>
              <p>Correo: <a href="mailto:privacidad@ptmnovo.mx" className="text-[var(--primary)] underline">privacidad@ptmnovo.mx</a></p>
              <p>Tiempo de respuesta: máximo <strong>5 días hábiles</strong></p>
              <p className="pt-2 border-t border-gray-200 text-gray-500">
                <strong>PROFECO (Procuraduría Federal del Consumidor):</strong><br />
                Tel: 800 468 8722 · <a href="https://www.gob.mx/profeco" target="_blank" rel="noopener noreferrer" className="text-[var(--primary)] underline">www.gob.mx/profeco</a>
              </p>
              <p className="text-gray-500">
                <strong>COFEPRIS (regulación sanitaria):</strong><br />
                <a href="https://www.gob.mx/cofepris" target="_blank" rel="noopener noreferrer" className="text-[var(--primary)] underline">www.gob.mx/cofepris</a>
              </p>
            </div>
          </Section>

          {/* Normas */}
          <Section id="normas" title="Marco Normativo de Referencia">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              {[
                ["LGS", "Ley General de Salud — Arts. 6, 34, 79, 83, 84"],
                ["LFPC", "Ley Federal de Protección al Consumidor — Arts. 56, 76 bis, 116, 117"],
                ["LFPDPPP", "Ley Federal de Protección de Datos Personales en Posesión de los Particulares"],
                ["CCF", "Código Civil Federal — Arts. 1803, 2111"],
                ["Cód. Comercio", "Código de Comercio — Arts. 89, 89 bis (contratos electrónicos)"],
                ["NOM-004-SSA3-2012", "Del Expediente Clínico — retención 5 años, datos mínimos requeridos"],
                ["NOM-024-SSA3-2012", "Sistemas de información de registro electrónico para la salud"],
                ["LDFA", "Ley Federal del Derecho de Autor"],
                ["LPI", "Ley de la Propiedad Industrial"],
                ["LINAI", "Lineamientos INAI para protección de datos en salud"],
              ].map(([norm, desc]) => (
                <div key={norm} className="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <p className="font-semibold text-[var(--primary)] mb-0.5">{norm}</p>
                  <p className="text-gray-500">{desc}</p>
                </div>
              ))}
            </div>
          </Section>

          {/* Footer */}
          <div className="pt-6 border-t border-gray-200 text-center text-xs text-gray-400">
            <p>
              © {new Date().getFullYear()} Peptide Technologies México · Todos los derechos reservados ·{" "}
              <Link href="/aviso-de-privacidad" className="hover:text-[var(--primary)]">Aviso de Privacidad</Link>
            </p>
            <p className="mt-1">Versión 1.0 · Vigente desde {LAST_UPDATED}</p>
          </div>

        </div>
      </div>
    </main>
  );
}

