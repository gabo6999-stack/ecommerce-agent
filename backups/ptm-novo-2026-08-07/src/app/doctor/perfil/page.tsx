import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";
import { THERAPY_AREAS, AREA_LABEL, parseTherapyAreas } from "@/lib/therapyAreas";
import { DOCUMENT_TYPES, DOCUMENT_LABEL, isValidDocumentType } from "@/lib/doctorDocuments";
import { storeDoctorDocument } from "@/lib/storage";

function sameSet(a: string[], b: string[]) {
  if (a.length !== b.length) return false;
  const setB = new Set(b);
  return a.every((x) => setB.has(x));
}

const VERIF_UI = {
  NOT_SUBMITTED: { badge: "Sin enviar", cls: "bg-gray-100 text-gray-600" },
  PENDING_REVIEW: { badge: "⏳ En revisión", cls: "bg-yellow-100 text-yellow-700" },
  APPROVED: { badge: "✅ Verificado", cls: "bg-green-100 text-green-700" },
  REJECTED: { badge: "⚠️ Rechazado", cls: "bg-red-100 text-red-700" },
} as const;

const DOC_STATUS_UI = {
  PENDING: { label: "Pendiente", cls: "bg-yellow-100 text-yellow-700" },
  APPROVED: { label: "Aprobado", cls: "bg-green-100 text-green-700" },
  REJECTED: { label: "Rechazado", cls: "bg-red-100 text-red-700" },
} as const;

export default async function DoctorPerfilPage({
  searchParams,
}: {
  searchParams: Promise<{ enviado?: string }>;
}) {
  const { enviado } = await searchParams;
  const session = await auth();

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session!.user!.email! } },
    include: { documents: { orderBy: { uploadedAt: "desc" } } },
  });

  if (!doctor) {
    return (
      <div className="max-w-xl">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">Mi perfil</h1>
        <p className="text-gray-500 text-sm">Tu cuenta no tiene un perfil de médico asociado.</p>
      </div>
    );
  }

  // ---- Server actions ----
  async function requestAreas(formData: FormData) {
    "use server";
    const requested = parseTherapyAreas(formData.getAll("therapyAreas") as string[]);
    const noChange = sameSet(requested, doctor!.therapyAreas);
    await prisma.doctor.update({
      where: { id: doctor!.id },
      data: {
        pendingTherapyAreas: noChange ? [] : requested,
        areasReviewPending: !noChange,
      },
    });
    revalidatePath("/doctor/perfil");
    redirect("/doctor/perfil?enviado=areas");
  }

  async function uploadDocument(formData: FormData) {
    "use server";
    const type = formData.get("type") as string;
    const file = formData.get("file") as File | null;
    if (!type || !isValidDocumentType(type) || !file || file.size === 0) return;

    const { fileKey, originalName } = await storeDoctorDocument({
      doctorId: doctor!.id,
      type,
      file,
    });

    await prisma.doctorDocument.create({
      data: { doctorId: doctor!.id, type, fileKey, originalName, status: "PENDING" },
    });

    revalidatePath("/doctor/perfil");
    redirect("/doctor/perfil?enviado=doc");
  }

  async function deleteDocument(formData: FormData) {
    "use server";
    const docId = formData.get("docId") as string;
    // Solo puede borrar sus propios documentos.
    await prisma.doctorDocument.deleteMany({ where: { id: docId, doctorId: doctor!.id } });
    revalidatePath("/doctor/perfil");
    redirect("/doctor/perfil");
  }

  async function submitForReview() {
    "use server";
    await prisma.doctor.update({
      where: { id: doctor!.id },
      data: { verificationStatus: "PENDING_REVIEW", verificationNotes: null },
    });
    revalidatePath("/doctor/perfil");
    redirect("/doctor/perfil?enviado=revision");
  }

  // ---- Datos derivados ----
  const preChecked = new Set(
    doctor.areasReviewPending ? doctor.pendingTherapyAreas : doctor.therapyAreas
  );
  const verif = VERIF_UI[doctor.verificationStatus];
  // Mínimos para poder enviar a revisión: ID + título de médico general.
  const requiredTypes = DOCUMENT_TYPES.filter((d) => d.required).map((d) => d.value);
  const uploadedTypes = new Set(doctor.documents.map((d) => d.type));
  const hasRequired = requiredTypes.every((t) => uploadedTypes.has(t));
  const canSubmit =
    hasRequired &&
    (doctor.verificationStatus === "NOT_SUBMITTED" || doctor.verificationStatus === "REJECTED");

  return (
    <div className="max-w-2xl">
      <h1 className="text-2xl font-bold text-gray-900 mb-1">Mi perfil</h1>
      <p className="text-gray-500 text-sm mb-6">Credencialización y rubros de terapia.</p>

      {enviado === "areas" && (
        <div className="mb-5 bg-blue-50 border border-blue-200 text-blue-700 text-sm rounded-xl px-4 py-3">
          ✅ Tu solicitud de rubros se envió. Se actualizará cuando el administrador la apruebe.
        </div>
      )}
      {enviado === "doc" && (
        <div className="mb-5 bg-blue-50 border border-blue-200 text-blue-700 text-sm rounded-xl px-4 py-3">
          ✅ Documento cargado. Cuando tengas tus documentos listos, envíalos a revisión.
        </div>
      )}
      {enviado === "revision" && (
        <div className="mb-5 bg-blue-50 border border-blue-200 text-blue-700 text-sm rounded-xl px-4 py-3">
          ✅ Documentos enviados a revisión. El administrador validará tu credencialización.
        </div>
      )}

      {/* Estado de verificación */}
      <div className="bg-white rounded-2xl border border-[var(--border)] p-6 mb-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-semibold text-gray-700">Estado de credencialización</p>
            <p className="text-xs text-gray-400 mt-0.5">
              Debes estar verificado para atender pacientes.
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${verif.cls}`}>
            {verif.badge}
          </span>
        </div>
        {doctor.verificationStatus === "REJECTED" && doctor.verificationNotes && (
          <p className="mt-3 text-xs text-red-600 bg-red-50 rounded-lg px-3 py-2">
            Motivo: {doctor.verificationNotes}
          </p>
        )}
      </div>

      {/* Documentos */}
      <div className="bg-white rounded-2xl border border-[var(--border)] p-6 mb-5">
        <p className="text-sm font-semibold text-gray-700 mb-1">Documentos</p>
        <p className="text-xs text-gray-400 mb-4">
          Sube tu identificación y los documentos que avalen tu formación para los rubros que atiendes.
        </p>

        {/* Documentos ya cargados */}
        {doctor.documents.length > 0 && (
          <div className="space-y-2 mb-5">
            {doctor.documents.map((d) => {
              const st = DOC_STATUS_UI[d.status];
              return (
                <div
                  key={d.id}
                  className="flex items-center justify-between gap-3 p-3 rounded-xl border border-[var(--border)]"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-800 truncate">
                      {DOCUMENT_LABEL[d.type]}
                    </p>
                    <p className="text-xs text-gray-400 truncate">{d.originalName}</p>
                  </div>
                  <div className="flex items-center gap-3 shrink-0">
                    <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${st.cls}`}>
                      {st.label}
                    </span>
                    {d.status === "PENDING" && (
                      <form action={deleteDocument}>
                        <input type="hidden" name="docId" value={d.id} />
                        <button
                          type="submit"
                          className="text-xs text-gray-400 hover:text-red-600 transition-colors"
                        >
                          Quitar
                        </button>
                      </form>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Subir nuevo documento */}
        <form action={uploadDocument} className="border-t border-[var(--border)] pt-4 space-y-3">
          <div className="grid grid-cols-2 gap-3">
            <select
              name="type"
              required
              defaultValue=""
              className="px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 bg-white"
            >
              <option value="" disabled>
                Tipo de documento…
              </option>
              {DOCUMENT_TYPES.map((t) => (
                <option key={t.value} value={t.value}>
                  {t.label}
                  {t.required ? " *" : ""}
                </option>
              ))}
            </select>
            <input
              type="file"
              name="file"
              required
              accept="image/*,application/pdf"
              className="text-sm text-gray-600 file:mr-3 file:py-2 file:px-3 file:rounded-lg file:border-0 file:text-xs file:font-semibold file:bg-gray-900 file:text-white hover:file:bg-gray-700"
            />
          </div>
          <button
            type="submit"
            className="px-5 py-2.5 rounded-xl font-semibold text-white text-sm bg-gray-900 hover:bg-gray-700 transition-colors"
          >
            Cargar documento
          </button>
        </form>

        {/* Enviar a revisión */}
        <div className="border-t border-[var(--border)] mt-5 pt-4">
          {!hasRequired && (
            <p className="text-xs text-gray-400 mb-3">
              Para enviar a revisión necesitas al menos: identificación oficial y título/cédula de
              médico general.
            </p>
          )}
          <form action={submitForReview}>
            <button
              type="submit"
              disabled={!canSubmit}
              className="px-5 py-2.5 rounded-xl font-semibold text-white text-sm bg-[var(--primary)] hover:opacity-90 transition disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {doctor.verificationStatus === "PENDING_REVIEW"
                ? "En revisión…"
                : "Enviar documentos a revisión"}
            </button>
          </form>
        </div>
      </div>

      {/* Rubros aprobados */}
      <div className="bg-white rounded-2xl border border-[var(--border)] p-6 mb-5">
        <p className="text-sm font-semibold text-gray-700 mb-3">Rubros activos (aprobados)</p>
        {doctor.therapyAreas.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {doctor.therapyAreas.map((area) => (
              <span
                key={area}
                className="px-3 py-1 rounded-full bg-green-50 text-green-700 text-xs font-medium"
              >
                {AREA_LABEL[area]}
              </span>
            ))}
          </div>
        ) : (
          <p className="text-sm text-gray-400">Aún no tienes rubros asignados.</p>
        )}
      </div>

      {/* Solicitud de rubros pendiente */}
      {doctor.areasReviewPending && (
        <div className="mb-5 bg-yellow-50 border border-yellow-200 rounded-2xl px-5 py-4">
          <p className="text-sm font-semibold text-yellow-800 mb-2">⏳ Cambio de rubros pendiente</p>
          <p className="text-xs text-yellow-700 mb-3">
            Solicitaste estos rubros. El administrador debe aprobarlos para que entren en vigor.
          </p>
          <div className="flex flex-wrap gap-2">
            {doctor.pendingTherapyAreas.length > 0 ? (
              doctor.pendingTherapyAreas.map((area) => (
                <span
                  key={area}
                  className="px-3 py-1 rounded-full bg-yellow-100 text-yellow-800 text-xs font-medium"
                >
                  {AREA_LABEL[area]}
                </span>
              ))
            ) : (
              <span className="text-xs text-yellow-700">Ningún rubro.</span>
            )}
          </div>
        </div>
      )}

      {/* Solicitar cambio de rubros */}
      <form action={requestAreas} className="bg-white rounded-2xl border border-[var(--border)] p-6">
        <p className="text-sm font-semibold text-gray-700 mb-1">Solicitar cambio de rubros</p>
        <p className="text-xs text-gray-400 mb-4">
          Marca los rubros que atiendes. Quedará pendiente hasta que el administrador lo apruebe.
        </p>
        <div className="grid grid-cols-2 gap-3 mb-5">
          {THERAPY_AREAS.map((area) => (
            <label
              key={area.value}
              className="flex items-start gap-3 p-3 rounded-xl border border-[var(--border)] cursor-pointer hover:border-gray-500 transition-colors has-[:checked]:border-gray-800 has-[:checked]:bg-[var(--muted)]"
            >
              <input
                type="checkbox"
                name="therapyAreas"
                value={area.value}
                defaultChecked={preChecked.has(area.value)}
                className="mt-0.5 w-4 h-4 accent-gray-900 flex-shrink-0 cursor-pointer"
              />
              <span>
                <span className="block text-sm font-medium text-gray-900">
                  {area.icon} {area.label}
                </span>
                <span className="block text-xs text-gray-400 leading-snug">{area.desc}</span>
              </span>
            </label>
          ))}
        </div>
        <button
          type="submit"
          className="px-6 py-3 rounded-xl font-semibold text-white text-sm bg-gray-900 hover:bg-gray-700 transition-colors"
        >
          Enviar solicitud
        </button>
      </form>
    </div>
  );
}
