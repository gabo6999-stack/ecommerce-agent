# Brief para contador — Grupo PTM (plataforma de telemedicina)

**Versión:** 1.0 · **Fecha:** 2026-06-19
**Para:** Contador(a) / asesor fiscal
**De:** Grupo PTM (Antonio Gavito Hernández)
**Documentos base:** `MODELO_MONETIZACION_PTM.md` (modelo de negocio) y `BRIEF_ABOGADO_PTM.md` (la parte sanitaria/regulatoria la lleva el abogado; **este brief es solo lo fiscal/facturación**).

> **Qué te pedimos en una frase:** definir la estructura de **facturación y flujo de dinero** para que PTM tribute **solo por su comisión de $500** (no por los $1,500 que cobra), eligiendo entre **contrato de mandato/comisión** o **split en pasarela**, y resolver si PTM queda sujeta al **régimen de retención de plataformas tecnológicas**.

---

## 1. El modelo en una imagen (lo fiscal)

PTM es una **plataforma tecnológica** que intermedia teleconsultas entre **pacientes** y **médicos independientes con cédula**.

```
Paciente paga ........... $1,500 MXN  (precio de la teleconsulta)
   ├─ Médico recibe ...... $1,000 MXN  (acto médico)
   └─ PTM retiene ........ $  500 MXN  (comisión FIJA por consulta + plataforma)
```

- El cobro lo procesa una **pasarela**; el pago se **retiene** y se libera cuando la consulta se **completa**.
- **El dinero de producto (péptidos/TRH) NUNCA pasa por PTM.** Solo se cobra la consulta.

---

## 2. El problema fiscal central

PTM cobra **$1,500** al paciente, pero **solo $500 son ingreso propio**; los **$1,000** son del médico y solo pasan a través de PTM (o de la pasarela).

**Objetivo:** que los $1,000 **no se consideren ingreso acumulable** de PTM, para no inflar su base de ISR/IVA con dinero que no es suyo.

Tenemos dos caminos y necesitamos que nos digas cuál conviene (o si se combinan):

### Opción A — Cobro por cuenta de terceros (contrato de mandato/comisión)
- PTM cobra los $1,500, se queda $500 y remite $1,000 al médico.
- Se documenta con un **contrato de mandato / comisión mercantil PTM↔médico**, de modo que los $1,000 se registren como **cobranza por cuenta de terceros**, no como ingreso de PTM.

### Opción B — Split en pasarela (preferida operativamente)
- La pasarela (**Stripe Connect Express** objetivo; el médico es cuenta conectada con su KYC) deposita **$1,000 directo al médico** y **$500 a PTM** vía `application_fee`.
- Así el dinero del médico **ni siquiera entra a las cuentas de PTM** → desaparece la discusión de ingreso por cuenta de terceros.

**Preguntas:**
1. ¿Cuál recomiendas (A, B o A+B como respaldo documental de B)?
2. En la Opción B con Stripe Connect, ¿basta el split para que fiscalmente PTM solo acumule los $500, o **igual se requiere** el contrato de mandato/comisión como soporte?

---

## 3. Esquema de CFDI propuesto (a validar)

Lo que tenemos pensado:

```
  Paciente  ◄── CFDI de la CONSULTA (si lo pide) ── MÉDICO   (PTM NO factura al paciente)
  Médico    ◄── CFDI de COMISIÓN de plataforma $500 ── PTM
```

- **PTM no emite CFDI al paciente.** La relación de servicio de salud es médico↔paciente; si el paciente quiere comprobante de la consulta, lo emite el **médico**.
- **PTM solo factura su comisión ($500) al médico** (su cliente fiscal es el médico, no el paciente).

**Preguntas:**
1. ¿Es correcto y suficiente este esquema con **CFDI 4.0**? ¿Qué **uso de CFDI**, **forma/método de pago** y **clave de producto/servicio (SAT)** aplican a la comisión de plataforma?
2. Para los $1,000 que cobramos por cuenta del médico (Opción A): ¿se requiere **CFDI con complemento de "cobranza por cuenta de terceros"** o equivalente? ¿Qué obligación de timbrado tiene PTM ahí?
3. ¿Riesgo de que el SAT interprete que **PTM presta el servicio de salud** por cobrar los $1,500? ¿Cómo lo documentamos para evitarlo?

---

## 4. ⭐ Punto crítico — ¿PTM es "plataforma tecnológica" con obligación de RETENER?

Nos preocupa que, al intermediar pagos entre pacientes y médicos vía aplicación, PTM caiga en el **régimen de plataformas tecnológicas** (intermediación digital) y quede **obligada a retener ISR e IVA** a los médicos por los ingresos que perciben a través de la plataforma (similar a Uber/Didi/Rappi con sus prestadores).

**Preguntas:**
1. ¿Aplica a PTM la obligación de **retención de ISR/IVA** del régimen de plataformas tecnológicas (arts. relativos de la LISR/LIVA) respecto de los pagos a los médicos? ¿Cambia según Opción A vs. B?
2. Si aplica: ¿qué **tasas de retención**, **enteros**, **CFDI de retenciones** y **avisos** debemos cumplir, y con qué periodicidad?
3. ¿Influye el **régimen fiscal del médico** (persona física con actividad profesional, RESICO, etc.) en la retención y en quién emite qué CFDI?

---

## 5. Régimen y obligaciones de PTM

1. ¿Qué **régimen fiscal** conviene a PTM (persona moral / persona física con actividad empresarial / RESICO PM) dado el modelo de comisiones?
2. **IVA:** ¿la comisión de plataforma de $500 causa IVA? ¿Y el servicio médico (que presta el médico) está **exento/gravado**? ¿Cómo se separan ambos a efectos de IVA?
3. **ISR:** confirmación de que la base de PTM son los $500 (más otras líneas SaaS futuras), no los $1,500.
4. **Deducibilidad:** tratamiento de las comisiones de la pasarela (Stripe), hosting y costos de plataforma.
5. **Contabilidad del dinero en tránsito:** cómo registrar los $1,000 (cuenta de orden / pasivo con terceros) para que no aparezcan como ingreso.

---

## 6. Pagos retenidos / diferidos (timing fiscal)

El pago se **retiene** y se libera al **completarse** la consulta (puede haber reagendaciones por no-show del médico).

**Preguntas:**
1. ¿En qué **momento se considera el ingreso** de PTM (los $500): al cobro, al completar la consulta, o al liberar el split? ¿Y el IVA correspondiente?
2. En caso de **no-show del médico** y reasignación a otro médico, ¿hay implicación fiscal en mover el destino del payout?

---

## 7. Líneas de ingreso futuras (para que el esquema las soporte)

Además de la comisión por consulta, el modelo prevé (opcionales): **suscripción SaaS del médico** y **membresía del paciente**. Queremos que el esquema fiscal/CFDI que definas **soporte estas líneas** sin rediseño.

---

## 8. Entregable que necesitamos de ti

1. **Recomendación A vs. B** (con/sin contrato de mandato) y por qué.
2. **Esquema de CFDI** definitivo (quién factura a quién, claves, complementos).
3. **Dictamen sobre retención de plataformas tecnológicas** (§4): aplica o no, y obligaciones si aplica.
4. **Régimen fiscal recomendado** para PTM y tratamiento de IVA/ISR de la comisión.
5. **Forma de registrar contablemente** los $1,000 en tránsito para que no sean ingreso de PTM.
6. Plantilla del **contrato de mandato/comisión PTM↔médico** (parte fiscal) si lo recomiendas — la parte legal la cruza el abogado.

---

> **Notas internas (no para el contador):** este brief es solo la capa fiscal; la viabilidad sanitaria (péptidos, licencias) la resuelve el abogado en `BRIEF_ABOGADO_PTM.md`. La decisión técnica de pasarela (Stripe Connect Express) ya está tomada en `MODELO_MONETIZACION_PTM.md` §5.A; si el contador desaconseja el split, reevaluar. Nada se cobra hasta cerrar §8 + dictamen legal.
