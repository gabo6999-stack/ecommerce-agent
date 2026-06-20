# Modelo de monetización — Grupo PTM (portal de telemedicina)

**Versión:** 1.0 · **Fecha:** 2026-06-19
**Objetivo:** definir cómo cobra Grupo PTM de forma que se mantenga jurídicamente del lado de **"plataforma de software + servicio médico"** y **fuera de la cadena de venta** de péptidos y terapia de reemplazo hormonal (TRH).

> ⚠️ Este documento es una guía de estructura de negocio, no asesoría legal. Antes de operar debe validarse con un **abogado regulatorio sanitario (COFEPRIS)**. Ver `MODELO_MONETIZACION_PTM.md#paso-0`.

---

## 0. El principio rector (una sola frase)

> **PTM cobra por el acceso a la plataforma y por la consulta médica. PTM NUNCA cobra nada ligado a que se receten, vendan o surtan productos.**

Si una línea de ingreso pasa esta prueba, es válida. Si no, se elimina:

**Prueba del "¿de qué vivo?":**
> ¿Este ingreso seguiría existiendo igual si el médico recetara **cero** productos este mes?
> - **Sí** → ingreso limpio (software/servicio). ✅
> - **No / depende de cuánto se recete o venda** → cadena de venta. ❌ Eliminar.

---

## 1. Líneas de ingreso PERMITIDAS (lado "software/servicio")

Todas pasan la prueba del párrafo anterior.

| # | Línea de ingreso | Quién paga | Por qué es limpia |
|---|------------------|-----------|-------------------|
| A | **Comisión por consulta** — PTM retiene una parte fija del precio de la teleconsulta por intermediar y dar la plataforma *(modelo elegido — ver §5)* | Paciente (vía precio de consulta) | Comisión sobre el **acto médico/servicio**, no sobre producto. Igual que Doctoralia. |
| B | **Suscripción del médico (SaaS)** — cuota por usar la plataforma (agenda, expediente, videollamada, emisión de receta) | Médico | Cobras la herramienta, no el resultado clínico. |
| C | **Membresía del paciente** (acceso a consultas, seguimiento, historial) | Paciente | Acceso al servicio, independiente de si se receta algo. |
| D | **Tarifa de software por consulta procesada** (fee fijo por teleconsulta gestionada) | Médico o paciente | Fijo por uso de software, no porcentaje de venta de producto. |
| E | **Servicios de la plataforma**: branding del perfil del médico, posicionamiento dentro del portal, herramientas premium | Médico | Servicios SaaS clásicos. |

**Regla de oro de pricing:** todas las tarifas son **fijas** (por consulta, por mes, por asiento) — **nunca un % atado a ventas de producto**. Una comisión sobre la **consulta** es limpia; una comisión sobre el **producto** es línea roja (§2).

---

## 2. Líneas de ingreso PROHIBIDAS (cadena de venta — líneas rojas)

Cualquiera de estas te mete en la cadena comercial y derrumba la defensa de "solo soy plataforma":

- ❌ **Comisión / % sobre la venta** del péptido u hormona.
- ❌ **Markup**: comprar producto y revenderlo (aunque sea "a través de un tercero").
- ❌ **Fee por receta emitida** que dependa del producto recetado o su precio.
- ❌ **Acuerdo de referido pagado con un vendedor/farmacia** específico (kickback por dirigir pacientes).
- ❌ **Inventario / almacenamiento / envío** de producto, directo o por interpósita persona.
- ❌ **Bundle "consulta + producto"** cobrado por PTM como un solo precio.
- ❌ **Descuentos de producto** financiados o gestionados por PTM.

> Regla mnemónica: **si el dinero sube cuando se vende más producto, es línea roja.**

---

## 3. Eliminar la cadena de venta — reglas de neutralidad

El modelo "soy plataforma" solo aguanta si la **neutralidad es real en la operación**, no solo en el papel.

### 3.1 Neutralidad en la dispensación
- El paciente termina la consulta **con su receta en la mano** (PDF/digital firmada por el médico).
- PTM **no sugiere, no enlaza, no recomienda** un vendedor/farmacia específico.
- PTM **no sabe ni le importa** dónde surte el paciente. No hay tracking de compra de producto.
- Si se ofrece una lista de farmacias, debe ser **información pública y neutral** (ej. "farmacias con licencia sanitaria en tu zona"), sin acuerdo comercial ni preferencia.

### 3.2 Independencia del médico
- Los médicos son **profesionales independientes** con cédula; ejercen criterio propio.
- PTM **no induce, no incentiva, no premia** recetar productos específicos.
- **Cero metas de prescripción.** Cero bonos por recetar. Cero scripts que empujen un producto.
- El contrato del médico debe decir explícitamente: PTM provee software; la decisión clínica es 100% del médico.

### 3.3 Separación del dinero
- El flujo de dinero del **producto** NUNCA pasa por las cuentas de PTM.
- PTM factura: suscripciones, consultas, membresías. Nada más.
- Si en algún punto entra dinero de producto a PTM → la separación se rompió.

---

## 4. Flujo de dinero (modelo limpio)

```
  PACIENTE                       PTM (plataforma)                 MÉDICO (cédula)
     |                                |                               |
     |   paga consulta $1,500     →   |                               |
     |   ────────────────────────►    |  retiene $500 comisión        |
     |                                |  ── remite $1,000 ───────────►|
     |                                |                               |
     |   ◄──── teleconsulta ──────────────────────────────────────────|
     |                                |                               |
     |   ◄──── receta firmada (PDF) ──────────────────────────────────|
     |                                |                               |
     |                                X  ← PTM NO interviene aquí
     |                                                                |
     |   ───────────────────────────────────────────►  FARMACIA / VENDEDOR
     |        paciente surte su receta donde él elija   (tercero independiente,
     |        (dinero del producto NUNCA toca a PTM)     sin acuerdo con PTM)
```

**Punto clave:** la "X" es donde se rompe la cadena. El dinero del producto fluye paciente→vendedor **sin pasar por PTM y sin que PTM dirija**.

---

## 5. Modelo elegido (números reales)

PTM cobra el precio de la **consulta** y retiene una **comisión fija por consulta** por intermediar y proveer la plataforma de telemedicina. El resto es del médico.

```
Paciente paga ............ $1,500 MXN   (precio de la teleconsulta)
   ├─ Médico recibe ...... $1,000 MXN   (acto médico — responde su cédula)
   └─ PTM retiene ........ $  500 MXN   (comisión por consulta + uso de plataforma)
```

**Por qué es limpio:** la comisión de $500 es **por la consulta**, no por el producto. Pasa la prueba del §0: existiría aunque se recetaran **cero** productos ese mes.

### Las 3 condiciones para que se mantenga limpio
1. **La comisión es fija por consulta** — no varía según qué/cuánto se recete. (Si subiera "porque recetó péptido caro", se rompe → línea roja §2.)
2. **Cero dinero de producto pasa por PTM.** Los $1,500 son **solo la consulta**; el producto lo surte el paciente por su cuenta, donde quiera, sin que PTM lo cobre ni lo toque.
3. **Neutralidad de dispensación** (§3.1) — PTM no dirige a un vendedor a cambio de contraprestación.

### Facturación / CFDI (esquema definido)

**Regla:** PTM **no factura al paciente**. El **médico factura al paciente** la consulta, si el paciente lo requiere. PTM solo **factura su comisión ($500) al médico**.

```
  Paciente  ──── CFDI de la consulta (si lo solicita) ◄──── MÉDICO
  Médico    ──── CFDI de comisión de plataforma ($500) ◄──── PTM
```

**Por qué refuerza el modelo:** el cliente fiscal de PTM es el **médico** (le cobras la plataforma), no el paciente. La relación de servicio de salud (y su comprobante fiscal) es médico↔paciente. PTM queda claramente como proveedor de software/intermediación.

**Punto a cerrar con contador (no afecta el tema sanitario):**
- PTM cobra los $1,500 al paciente y remite $1,000 al médico → fiscalmente esto es **cobro por cuenta de terceros (mandato/comisión mercantil)**. Debe documentarse con un **contrato de mandato/comisión** entre PTM y el médico para que los $1,000 que pasan por PTM **no se consideren ingreso propio** de PTM (solo los $500 lo son).
- Alternativa más limpia operativamente: **split de pago en la pasarela** — que la pasarela deposite $1,000 directo al médico y $500 a PTM, para que el dinero del médico ni siquiera entre a las cuentas de PTM.
- Nota: no emitir CFDI no elimina la obligación fiscal; el ingreso real de PTM ($500) se documenta vía su factura de comisión al médico.

### Líneas de ingreso secundarias opcionales
- **Suscripción SaaS del médico** (línea B) — ingreso recurrente adicional.
- **Membresía del paciente** (línea C) — para seguimiento/recurrencia.

---

## 5.A Agendamiento, retención de pago y política de cancelación

### Flujo de agendamiento + pago (retención)
```
Paciente elige fecha/hora
        ↓
Sistema busca médicos del staff con ese slot LIBRE
        ↓
Asigna médico (round-robin / por especialidad) y BLOQUEA el slot
        ↓
Cobra $1,500 al paciente → RETIENE el payout (no se libera aún)
        ↓
[ Se realiza la teleconsulta ]
        ↓
Al COMPLETARSE → libera split: $1,000 al médico que atendió + $500 a PTM
```

**Por qué se retiene:** NO es para reembolsar al paciente (no hay reembolsos, ver tabla). Es para garantizar que el dinero le caiga al **médico que realmente atendió** — clave cuando hay reasignación por no-show del médico. Evita tener que perseguir a un médico para recuperar un pago ya hecho (cero clawback).

### Política de cancelación / no-show (definitiva)

| Evento | Reembolso al paciente | Pago al médico |
|--------|----------------------|----------------|
| **Paciente cancela o no acude** | ❌ **No** — se cobra, sin reembolso | ✅ Sí — apartó su hora; se libera el split $1,000 / $500 |
| **Médico no se presenta** | ❌ No (se **reagenda**, no se reembolsa) | ⏸️ Retenido hasta que un médico **complete** la consulta |
| **Consulta completada** | — | ✅ Libera $1,000 al médico + $500 a PTM |

**Requisito legal:** la política de **no-reembolso** debe estar **visible y aceptada explícitamente** por el paciente al pagar (checkbox de aceptación). Si no se acepta de forma clara, es impugnable ante **PROFECO**. Con aceptación expresa, es defendible.

### Reasignación por no-show del médico
- **Opción 1:** el médico reagenda desde su panel (propone nueva fecha al paciente).
- **Opción 2:** reasignación automática a otro médico disponible del staff.
- En ambos casos el pago sigue **retenido** y se libera solo cuando un médico completa la consulta.

### Stack de pago
- **Stripe Connect (Express accounts)** — cada médico = cuenta conectada con su propio KYC; `application_fee_amount = $500`; soporta retención + transferencia diferida nativamente. Disponible en México.
- **Estado:** split $1,000/$500 vía `application_fee` **ya configurado** ✅ — **pruebas pendientes** ⏳ (validar: retención, liberación al completar consulta, no-show paciente sin reembolso, no-show médico con reagendado).
- Alternativas evaluadas: Mercado Pago Marketplace, Conekta.

---

## 6. Implicaciones para la publicidad (Meta / COFEPRIS)

El modelo de monetización y la publicidad deben ser coherentes:

- ✅ Anunciar: **"Consulta con médicos certificados con cédula profesional"**, el servicio de telemedicina.
- ❌ NO anunciar: productos, beneficios terapéuticos, "accede a péptidos/TRH", claims de resultados.
- La landing debe vender **la consulta**, no el producto. (Ver tarea de rediseño pendiente.)

---

## 7. Checklist de cumplimiento (revisar antes de cobrar el primer peso)

- [ ] **Paso 0 — Dictamen de viabilidad** firmado por abogado regulatorio sanitario.
- [ ] Ninguna línea de ingreso falla la "prueba del ¿de qué vivo?".
- [ ] Contrato del médico establece independencia clínica y rol de PTM = software.
- [ ] Aviso de privacidad (datos sensibles de salud, LFPDPPP) publicado.
- [ ] Consentimiento informado de teleconsulta implementado.
- [ ] Cédula profesional de cada médico verificada y publicada.
- [ ] Cero enlaces/recomendaciones a vendedores de producto en el flujo.
- [ ] Facturación de PTM solo incluye consultas/suscripciones/membresías.
- [ ] Publicidad revisada: sin claims de producto.

---

## Paso 0 — Lo primero que debe pasar

Antes de implementar nada de esto técnicamente, el **dictamen de viabilidad regulatoria** debe confirmar:
1. Que la estructura de monetización aquí descrita te mantiene fuera de la cadena.
2. Cómo tratar los **péptidos no registrados** (el punto más delicado: que un médico los recete no los vuelve legales de surtir).
3. Qué figura legal/avisos necesita PTM como plataforma (aviso de funcionamiento, responsable sanitario, etc.).

---

## Anexo — Cláusulas tipo para términos y contratos (borrador, validar con abogado)

**Para los Términos de la plataforma (paciente):**
> "Grupo PTM es una plataforma tecnológica que facilita la conexión entre pacientes y médicos independientes con cédula profesional. PTM no vende, distribuye, almacena ni surte medicamentos ni productos de ningún tipo. La prescripción es responsabilidad exclusiva del médico tratante. La adquisición de cualquier producto recetado se realiza por el paciente, por su cuenta, ante el establecimiento de su elección, sin intervención de PTM."

**Para el contrato del médico:**
> "El médico ejerce su profesión de forma autónoma e independiente, conforme a su criterio clínico y su cédula profesional. PTM no instruye, incentiva ni condiciona las prescripciones del médico. La relación entre PTM y el médico se limita a la provisión de herramientas de software (agenda, expediente, teleconsulta, emisión de receta) a cambio de una contraprestación fija e independiente del contenido o volumen de las prescripciones."
