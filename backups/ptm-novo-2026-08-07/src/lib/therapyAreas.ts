import type { TherapyArea } from "@prisma/client";

// Los 4 rubros de terapia que un médico puede atender. El value coincide con el
// enum TherapyArea del schema. Fuente única para el alta y la edición de médicos.
export const THERAPY_AREAS: {
  value: TherapyArea;
  label: string;
  desc: string;
  icon: string;
}[] = [
  { value: "WEIGHT_LOSS", label: "Pérdida de peso", desc: "GLP-1: semaglutida, tirzepatida, retatrutida", icon: "⚖️" },
  { value: "PEPTIDES_LONGEVITY", label: "Péptidos y Longevidad", desc: "Recuperación, antiaging y rendimiento", icon: "🧬" },
  { value: "MENS_HEALTH", label: "Salud para Hombres", desc: "Testosterona (TRH), energía y libido", icon: "💪" },
  { value: "WOMENS_HEALTH", label: "Salud para Mujeres", desc: "Equilibrio hormonal y vitalidad", icon: "🌸" },
];

export const AREA_LABEL: Record<TherapyArea, string> = {
  WEIGHT_LOSS: "Pérdida de peso",
  PEPTIDES_LONGEVITY: "Péptidos y Longevidad",
  MENS_HEALTH: "Salud para Hombres",
  WOMENS_HEALTH: "Salud para Mujeres",
};

// Filtra strings arbitrarios (p. ej. de un formulario) a valores válidos del enum.
export function parseTherapyAreas(values: string[]): TherapyArea[] {
  const valid = THERAPY_AREAS.map((a) => a.value);
  return values.filter((v): v is TherapyArea => valid.includes(v as TherapyArea));
}
