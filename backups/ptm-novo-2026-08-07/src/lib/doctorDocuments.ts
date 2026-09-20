import type { DoctorDocumentType } from "@prisma/client";

// Tipos de documento de credencialización que el médico debe aportar. `required`
// marca los mínimos para enviar a revisión; los diplomados son opcionales pero
// pueden ser necesarios para avalar rubros como TRH.
export const DOCUMENT_TYPES: {
  value: DoctorDocumentType;
  label: string;
  hint: string;
  required: boolean;
}[] = [
  { value: "OFFICIAL_ID", label: "Identificación oficial", hint: "INE o pasaporte vigente", required: true },
  { value: "MEDICAL_DEGREE", label: "Título / cédula de médico general", hint: "Título o cédula profesional de medicina", required: true },
  { value: "SPECIALTY_DEGREE", label: "Título de especialidad", hint: "Cuando aplique al rubro que atiendes", required: false },
  { value: "DIPLOMA", label: "Diplomados / constancias", hint: "Que avalen tu práctica (p. ej. TRH, péptidos)", required: false },
];

export const DOCUMENT_LABEL: Record<DoctorDocumentType, string> = {
  OFFICIAL_ID: "Identificación oficial",
  MEDICAL_DEGREE: "Título / cédula de médico general",
  SPECIALTY_DEGREE: "Título de especialidad",
  DIPLOMA: "Diplomado / constancia",
};

export function isValidDocumentType(v: string): v is DoctorDocumentType {
  return DOCUMENT_TYPES.some((d) => d.value === v);
}
