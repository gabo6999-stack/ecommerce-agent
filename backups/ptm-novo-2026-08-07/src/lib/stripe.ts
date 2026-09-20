import Stripe from "stripe";

// Cliente Stripe del lado plataforma (cuenta de PTM). Las cuentas de los médicos
// son cuentas conectadas (Connect Express) — ver src/app/api/connect/onboard.
// Modelo: separate charges & transfers. Se cobra $1,500 a la plataforma y se
// RETIENE; al completar la consulta se transfiere $1,000 al médico que atendió.
// Ver MODELO_MONETIZACION_PTM.md §5 / §5.A.

// Inicialización PEREZOSA: el constructor de Stripe lanza si no hay llave, y se
// importa durante `next build` (recolección de rutas). Con el Proxy, Stripe solo
// se instancia en el primer uso real (runtime), no al importar el módulo.
let instance: Stripe | null = null;

function getStripe(): Stripe {
  if (!instance) {
    const key = process.env.STRIPE_SECRET_KEY;
    if (!key) throw new Error("STRIPE_SECRET_KEY no está configurada");
    instance = new Stripe(key);
  }
  return instance;
}

export const stripe = new Proxy({} as Stripe, {
  get(_target, prop) {
    // Las sub-resources (checkout, webhooks, transfers, accounts, accountLinks)
    // ya están ligadas al cliente, así que devolverlas directo es suficiente.
    return getStripe()[prop as keyof Stripe];
  },
});

// Montos en la unidad mínima de MXN (centavos).
export const CONSULTA_TOTAL_CENTAVOS = 150000; // $1,500 (paciente)
export const MEDICO_CENTAVOS = 100000; //         $1,000 (transfer al médico)
export const PTM_COMISION_CENTAVOS = 50000; //    $  500 (queda en plataforma)
