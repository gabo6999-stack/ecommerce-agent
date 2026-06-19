# Brief para abogado regulatorio sanitario — Grupo PTM (plataforma de telemedicina)

**Versión:** 1.0 · **Fecha:** 2026-06-19
**Para:** Abogado(a) especialista en regulación sanitaria (COFEPRIS) y salud digital
**De:** Grupo PTM (Antonio Gavito Hernández)
**Documento base:** `MODELO_MONETIZACION_PTM.md` (modelo de negocio completo; se anexa)

> **Qué te pedimos en una frase:** un **dictamen de viabilidad regulatoria** que nos confirme (o corrija) si la estructura descrita aquí nos mantiene jurídicamente como **plataforma tecnológica + servicio médico**, **fuera de la cadena de venta** de péptidos y terapia de reemplazo hormonal (TRH), y que resuelva el punto más delicado: **los péptidos sin registro sanitario**.

---

## 1. Qué es Grupo PTM y qué NO es

**Es:** una plataforma de software que conecta **pacientes** con **médicos independientes con cédula profesional** para **teleconsultas** de TRH y terapia con péptidos. Cobra por la consulta y por el uso de la plataforma.

**No es** (decisión de diseño, no aspiración): PTM **no vende, no compra, no importa, no almacena, no surte, no envía** producto alguno. No recibe dinero de producto. No dirige al paciente a una farmacia o vendedor específico a cambio de contraprestación. El paciente termina la consulta con su **receta firmada por el médico** y la surte **por su cuenta, donde él elija**.

**Posicionamiento legal buscado:** análogo a Doctoralia/plataformas de telemedicina — proveedor de software + intermediación del acto médico, no establecimiento que dispensa insumos para la salud.

---

## 2. Estructura económica (resumen; detalle en doc base §5)

```
Paciente paga consulta ...... $1,500 MXN
   ├─ Médico recibe .......... $1,000 MXN   (acto médico — responde su cédula)
   └─ PTM retiene ............ $  500 MXN   (comisión FIJA por consulta + uso de plataforma)
```

- La comisión de PTM es **fija por consulta**, **nunca** un % ni atada al producto recetado.
- **Cero dinero de producto pasa por PTM.** Los $1,500 son únicamente la consulta.
- Pago objetivo: **Stripe Connect (Express)** — el médico es cuenta conectada con su propio KYC; `application_fee` de $500; retención del payout y liberación diferida al **completarse** la consulta.
- Facturación: **PTM no factura al paciente**; el **médico factura al paciente** la consulta. PTM solo **factura su comisión ($500) al médico** (cobro por cuenta de terceros — punto a cerrar con contador, ver §6).

La "prueba del ¿de qué vivo?" que aplicamos a cada línea de ingreso: *¿este ingreso existiría igual si el médico recetara cero productos este mes?* Si la respuesta es no, se elimina.

---

## 3. ⭐ EL PUNTO CRÍTICO — Péptidos sin registro sanitario

Este es el hueco que el modelo de **cobro** no resuelve por sí solo y la razón principal de este brief.

**El problema, como lo entendemos (a confirmar/corregir por ti):**
- Varios de los péptidos que un médico podría prescribir **no cuentan con registro sanitario como medicamento** ante COFEPRIS en México.
- Nuestra hipótesis es que **el hecho de que un médico los recete no los vuelve legales de surtir/dispensar**: dispensar un "insumo para la salud" sin registro sanitario podría infringir la Ley General de Salud (LGS) y el Reglamento de Insumos para la Salud (RIS).
- Aun cuando PTM se mantenga fuera de la dispensación, nos preocupa la **exposición indirecta** por: (a) facilitar consultas cuyo desenlace típico es una receta de un producto no registrado; y (b) la publicidad.

**Preguntas concretas que necesitamos que el dictamen responda:**

1. **Legalidad de la prescripción.** ¿Puede un médico con cédula **prescribir legalmente** un péptido sin registro sanitario? ¿Bajo qué figura (uso magistral/farmacia de preparados magistrales, importación para uso personal del paciente, uso compasivo, etc.) y con qué límites?
2. **Legalidad de la dispensación.** Dado que el paciente debe surtir su receta en algún lado: ¿**existe una vía lícita** para que el paciente obtenga el producto (p. ej., farmacia magistral autorizada, importación personal regulada)? ¿O no existe vía lícita, lo que cambiaría todo el modelo?
3. **Exposición de PTM.** Si la dispensación del producto fuese ilícita o de zona gris, **¿qué responsabilidad recae sobre PTM** por el solo hecho de operar la plataforma de teleconsulta, aun sin tocar el producto ni el dinero del producto? ¿Basta la neutralidad operativa (§3 del doc base) para aislar a PTM?
4. **Línea de seguridad.** ¿Qué debe **dejar de hacer** PTM, sí o sí, para no ser considerado partícipe en la cadena? (Ya identificamos por nuestra cuenta que PTM no debe rastrear, enlazar ni recomendar dónde surtir — confirmar y completar.)
5. **TRH (hormonas).** Las hormonas para TRH (a diferencia de muchos péptidos) **sí** suelen tener registro y son de **venta con receta**. ¿Cambia algo el análisis para la parte de TRH vs. la de péptidos? ¿Conviene separar ambas líneas?

---

## 4. Figura legal y licencias de PTM como plataforma

1. **¿Qué figura sanitaria, si alguna, requiere PTM** operando solo software + intermediación de teleconsulta? En particular:
   - ¿Necesita **aviso de funcionamiento** y/o **responsable sanitario** ante COFEPRIS, o al no ser establecimiento que maneja insumos queda fuera?
   - ¿Cambia si en algún momento ofrecemos expediente clínico electrónico/almacenamiento de datos clínicos?
2. **Marco de telemedicina.** ¿Qué obligaciones nos imponen el marco de telemedicina/teleconsulta vigente y las NOM aplicables —entendemos que relevan **NOM-004-SSA3-2012** (expediente clínico) y **NOM-024-SSA3-2012** (sistemas de información en salud)— y cuáles recaen sobre PTM (plataforma) vs. sobre el médico?
3. **Receta digital.** ¿Qué requisitos de validez tiene la **receta electrónica/digital** firmada por el médico en este esquema? ¿Firma electrónica, datos obligatorios, conservación?
4. **Verificación de cédula.** ¿Es suficiente verificar y publicar la **cédula profesional** de cada médico, o se requiere además algo (especialidad registrada, certificación de consejo)?

---

## 5. Relación con el médico (independencia)

- Los médicos son **contratistas independientes** que ejercen criterio clínico propio; PTM provee herramientas.
- Buscamos que el **contrato del médico** blinde: independencia clínica, cero metas/bonos de prescripción, rol de PTM = software (cláusula tipo en el Anexo del doc base).

**Preguntas:**
1. ¿La estructura de **contratista independiente** es defendible aquí, o el modelo de asignación automática de pacientes/lock de slot/retención de pago podría reinterpretarse como **relación laboral** o como que PTM "presta el servicio médico"?
2. ¿Qué cláusulas son **imprescindibles** en el contrato del médico para sostener la independencia y desplazar a PTM de la responsabilidad por el acto médico y por la prescripción?
3. ¿Quién es el **responsable del tratamiento de datos** del paciente: el médico, PTM, o corresponsables? (enlaza con §7).

---

## 6. Cobro por cuenta de terceros y facturación (interfaz con contador)

PTM cobra $1,500 al paciente y remite $1,000 al médico. Esto lo trataremos fiscalmente como **cobro por cuenta de terceros (mandato/comisión mercantil)** para que los $1,000 **no se consideren ingreso propio** de PTM. Lo cerraremos con contador, pero necesitamos tu visto bueno legal sobre:

1. ¿Es válido el **contrato de mandato/comisión mercantil PTM↔médico** para documentar que PTM solo es ingreso por los $500? ¿O conviene exclusivamente el **split en pasarela** (que la pasarela deposite $1,000 directo al médico y $500 a PTM) para que el dinero del médico ni entre a cuentas de PTM?
2. ¿Hay algún riesgo de que el cobro al paciente por PTM se interprete como que **PTM presta el servicio de salud**? ¿Cómo lo evitamos contractual y documentalmente?

---

## 7. Datos personales sensibles (LFPDPPP)

Manejaremos **datos personales sensibles de salud** (historial, padecimientos, fotos de progreso, respuestas de quiz).

1. ¿Qué exige la **LFPDPPP y su reglamento** para este tratamiento (aviso de privacidad integral, consentimiento expreso para datos sensibles, medidas de seguridad, transferencias)?
2. Corresponsabilidad médico↔PTM: ¿cómo se reparte y se documenta?
3. ¿Requisitos para almacenar **video/grabaciones** de teleconsulta, si las hubiera?

---

## 8. Política de cancelación / no-reembolso (PROFECO)

Decisión de negocio: **no hay reembolsos**. Paciente que cancela o no acude = se cobra (el médico apartó su hora). Médico no-show = se **reagenda**, no se reembolsa.

1. ¿Es **defendible ante PROFECO** una política de no-reembolso si se muestra y se **acepta expresamente** (checkbox) antes de pagar? ¿Qué redacción/forma de aceptación la hace exigible?
2. ¿Algún supuesto en que el reembolso sea **irrenunciable** por ley (p. ej., falla total del servicio imputable a PTM)?

---

## 9. Publicidad (COFEPRIS / Meta)

Anunciaremos **la consulta médica**, no el producto.

1. ¿Qué podemos y qué **no** podemos decir en publicidad (Reglamento de la LGS en materia de Publicidad)? Confirmar que está prohibido anunciar producto, beneficios terapéuticos o claims de resultados.
2. ¿La sola mención de "TRH/péptidos" en la publicidad de la consulta genera riesgo, o es admisible describir el **tipo de consulta**?
3. ¿Requiere la publicidad de servicios de telemedicina **permiso/aviso** ante COFEPRIS?

---

## 10. Entregable que necesitamos de ti

1. **Dictamen de viabilidad** (semáforo): el modelo es ✅ viable / ⚠️ viable con cambios / ❌ inviable — con la justificación.
2. **Lista de cambios obligatorios** al modelo para quedar del lado limpio (priorizada).
3. **Veredicto sobre péptidos no registrados** (§3): vía lícita de dispensación para el paciente, o confirmación de que no la hay, y qué implica eso para PTM.
4. **Checklist de licencias/avisos/figuras** que PTM debe tramitar antes de operar.
5. **Visto bueno o correcciones** a los borradores que prepararemos (Términos, Aviso de privacidad, Consentimiento informado, Contrato del médico) — los enviaremos como insumo para que solo revises.

---

## 11. Anexos que entregamos

- `MODELO_MONETIZACION_PTM.md` — modelo de monetización completo (flujo de dinero, líneas permitidas/prohibidas, reglas de neutralidad, facturación, cancelación, stack de pago).
- Cláusulas tipo (borrador) para Términos del paciente y Contrato del médico — Anexo del doc base.
- (Pendiente de adjuntar) Borradores de Términos, Aviso de privacidad y Consentimiento informado.

---

> **Nota interna (no para el abogado):** este brief NO es asesoría legal; es el insumo para obtenerla. Nada del modelo se implementa ni se cobra el primer peso hasta tener el dictamen de §10 firmado. Es el **Paso 0** del checklist de cumplimiento.
