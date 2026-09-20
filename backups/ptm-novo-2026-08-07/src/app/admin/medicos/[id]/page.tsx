import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import { redirect, notFound } from "next/navigation";
import Link from "next/link";
import { THERAPY_AREAS, AREA_LABEL, parseTherapyAreas } from "@/lib/therapyAreas";
import { DOCUMENT_LABEL } from "@/lib/doctorDocuments";
import { getDocumentUrl } from "@/lib/storage";

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

export default async function EditDoctorPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;

  const doctor = await prisma.doctor.findUnique({
    where: { id },
    include: { user: true, documents: { orderBy: { uploadedAt: "desc" } } },
  });

  if (!doctor) notFound();

  // URLs (firmadas) de cada documento; null mientras no haya storage real.
  const docUrls = await Promise.all(doctor.documents.map((d) => getDocumentUrl(d.fileKey)));

  async function updateDoctor(formData: FormData) {
    "use server";
    const name = (formData.get("name") as string)?.trim();
    const license = (formData.get("license") as string)?.trim();
    const specialty = (formData.get("specialty") as string)?.trim() || "Peptide Therapy";
    const bio = (formData.get("bio") as string)?.trim() || null;
    const isActive = formData.get("isActive") === "on";
    const therapyAreas = parseTherapyAreas(formData.getAll("therapyAreas") as string[]);

    if (!name || !license) return;

    await prisma.doctor.update({
      where: { id },
      data: {
        licenseNumber: license,
        specialty,
        bio,
        isActive,
        therapyAreas,
        // El admin guarda directo (autoritativo): descarta cualquier solicitud
        // pendiente del médico.
        pendingTherapyAreas: [],
        areasReviewPending: false,
        user: { update: { name } },
      },
    });

    revalidatePath("/admin/medicos");
    redirect("/admin/medicos");
  }

  async function approveAreas() {
    "use server";
    const d = await prisma.doctor.findUnique({ where: { id } });
    if (!d) return;
    await prisma.doctor.update({
      where: { id },
      data: {
        therapyAreas: d.pendingTherapyAreas,
        pendingTherapyAreas: [],
        areasReviewPending: false,
      },
    });
    revalidatePath("/admin/medicos");
    redirect("/admin/medicos");
  }

  async function rejectAreas() {
    "use server";
    await prisma.doctor.update({
      where: { id },
      data: { pendingTherapyAreas: [], areasReviewPending: false },
    });
    revalidatePath(`/admin/medicos/${id}`);
    redirect(`/admin/medicos/${id}`);
  }

  async function reviewDocument(formData: FormData) {
    "use server";
    const docId = formData.get("docId") as string;
    const decision = formData.get("decision") as string; // "APPROVED" | "REJECTED"
    if (decision !== "APPROVED" && decision !== "REJECTED") return;
    await prisma.doctorDocument.updateMany({
      where: { id: docId, doctorId: id },
      data: { status: decision, reviewedAt: new Date() },
    });
    revalidatePath(`/admin/medicos/${id}`);
    redirect(`/admin/medicos/${id}`);
  }

  async function setVerification(formData: FormData) {
    "use server";
    const decision = formData.get("decision") as string; // "APPROVED" | "REJECTED"
    const notes = ((formData.get("notes") as string) || "").trim() || null;
    if (decision !== "APPROVED" && decision !== "REJECTED") return;
    await prisma.doctor.update({
      where: { id },
      data: {
        verificationStatus: decision,
        verificationNotes: decision === "REJECTED" ? notes : null,
      },
    });
    revalidatePath(`/admin/medicos/${id}`);
    redirect(`/admin/medicos/${id}`);
  }

  const selected = new Set(doctor.therapyAreas);
  const verif = VERIF_UI[doctor.verificationStatus];

  return (
    <div className="max-w-2xl">
      <Link
        href="/admin/medicos"
        className="text-sm text-gray-500 hover:text-gray-900 mb-6 inline-block"
      >
        ← Volver a Médicos
      </Link>

      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Editar médico</h1>
        <p className="text-gray-500 text-sm mt-1">{doctor.user.email}</p>
      </div>

      {/* Credencialización (KYC médico) */}
      <div className="bg-white rounded-xl border border-[var(--border)] p-6 mb-5">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="font-bold text-gray-900">Credencialización</h2>
            <p className="text-xs text-gray-400 mt-0.5">
              Verifica los documentos que avalan la práctica del médico antes de aprobar sus rubros.
            </p>
          </div>
          <span className={`px-3 py-1 rounded-full text-xs font-semibold ${verif.cls}`}>
            {verif.badge}
          </span>
        </div>

        {/* Documentos */}
        {doctor.documents.length === 0 ? (
          <p className="text-sm text-gray-400">El médico aún no ha cargado documentos.</p>
        ) : (
          <div className="space-y-2">
            {doctor.documents.map((d, i) => {
              const st = DOC_STATUS_UI[d.status];
              const url = docUrls[i];
              return (
                <div
                  key={d.id}
                  className="flex items-center justify-between gap-3 p-3 rounded-xl border border-[var(--border)]"
                >
                  <div className="min-w-0">
                    <p className="text-sm font-medium text-gray-800">{DOCUMENT_LABEL[d.type]}</p>
                    <p className="text-xs text-gray-400 truncate">
                      {url ? (
                        <a href={url} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline">
                          {d.originalName}
                        </a>
                      ) : (
                        <span title="Vista previa disponible al conectar el almacenamiento">
                          {d.originalName} · (sin vista previa)
                        </span>
                      )}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <span className={`px-2.5 py-1 rounded-full text-[11px] font-semibold ${st.cls}`}>
                      {st.label}
                    </span>
                    <form action={reviewDocument}>
                      <input type="hidden" name="docId" value={d.id} />
                      <input type="hidden" name="decision" value="APPROVED" />
                      <button type="submit" className="text-xs text-green-600 hover:text-green-800 font-medium">
                        Aprobar
                      </button>
                    </form>
                    <form action={reviewDocument}>
                      <input type="hidden" name="docId" value={d.id} />
                      <input type="hidden" name="decision" value="REJECTED" />
                      <button type="submit" className="text-xs text-gray-400 hover:text-red-600">
                        Rechazar
                      </button>
                    </form>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Decisión de verificación global */}
        <div className="border-t border-[var(--border)] mt-5 pt-4">
          <form action={setVerification} className="space-y-3">
            <textarea
              name="notes"
              rows={2}
              placeholder="Motivo (si rechazas la verificación)…"
              className="w-full px-4 py-2.5 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 resize-none"
            />
            <div className="flex items-center gap-3">
              <button
                type="submit"
                name="decision"
                value="APPROVED"
                className="px-4 py-2 rounded-lg font-semibold text-white text-xs bg-green-600 hover:bg-green-700 transition-colors"
              >
                Aprobar verificación
              </button>
              <button
                type="submit"
                name="decision"
                value="REJECTED"
                className="px-4 py-2 rounded-lg font-medium text-xs text-red-600 hover:bg-red-50 transition-colors"
              >
                Rechazar verificación
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* Solicitud de cambio de rubros pendiente (hecha por el médico) */}
      {doctor.areasReviewPending && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-xl p-5 mb-5">
          <p className="text-sm font-semibold text-yellow-800 mb-1">
            ⏳ El médico solicitó cambiar sus rubros
          </p>
          <p className="text-xs text-yellow-700 mb-3">
            Rubros solicitados (reemplazarán a los aprobados si los apruebas):
          </p>
          <div className="flex flex-wrap gap-2 mb-4">
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
              <span className="text-xs text-yellow-700">Ningún rubro (solicitud para quedar sin rubros).</span>
            )}
          </div>
          <div className="flex items-center gap-3">
            <form action={approveAreas}>
              <button
                type="submit"
                className="px-4 py-2 rounded-lg font-semibold text-white text-xs bg-green-600 hover:bg-green-700 transition-colors"
              >
                Aprobar solicitud
              </button>
            </form>
            <form action={rejectAreas}>
              <button
                type="submit"
                className="px-4 py-2 rounded-lg font-medium text-xs text-gray-600 hover:bg-gray-100 transition-colors"
              >
                Rechazar
              </button>
            </form>
          </div>
        </div>
      )}

      <form action={updateDoctor} className="bg-white rounded-xl border border-[var(--border)] p-6 space-y-5">
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre completo</label>
            <input
              type="text"
              name="name"
              required
              defaultValue={doctor.user.name}
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Correo <span className="text-gray-400 font-normal">(no editable)</span>
            </label>
            <input
              type="email"
              value={doctor.user.email}
              disabled
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] bg-[var(--muted)] text-sm text-gray-500 cursor-not-allowed"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Número de cédula / licencia</label>
            <input
              type="text"
              name="license"
              required
              defaultValue={doctor.licenseNumber}
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Especialidad <span className="text-gray-400 font-normal">(opcional)</span>
            </label>
            <input
              type="text"
              name="specialty"
              defaultValue={doctor.specialty}
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Bio <span className="text-gray-400 font-normal">(opcional)</span>
          </label>
          <textarea
            name="bio"
            rows={3}
            defaultValue={doctor.bio ?? ""}
            placeholder="Breve presentación del médico..."
            className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors resize-none"
          />
        </div>

        {/* Rubros de terapia */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Rubros que atiende <span className="text-gray-400 font-normal">(puede elegir varios)</span>
          </label>
          <div className="grid grid-cols-2 gap-3">
            {THERAPY_AREAS.map((area) => (
              <label
                key={area.value}
                className="flex items-start gap-3 p-3 rounded-xl border border-[var(--border)] cursor-pointer hover:border-gray-500 transition-colors has-[:checked]:border-gray-800 has-[:checked]:bg-[var(--muted)]"
              >
                <input
                  type="checkbox"
                  name="therapyAreas"
                  value={area.value}
                  defaultChecked={selected.has(area.value)}
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
        </div>

        {/* Estado activo */}
        <label className="flex items-center gap-3 cursor-pointer">
          <input
            type="checkbox"
            name="isActive"
            defaultChecked={doctor.isActive}
            className="w-4 h-4 accent-gray-900 cursor-pointer"
          />
          <span className="text-sm text-gray-700">Médico activo (puede recibir asignaciones)</span>
        </label>

        <div className="flex items-center gap-3 pt-2">
          <button
            type="submit"
            className="px-6 py-3 rounded-xl font-semibold text-white text-sm bg-gray-900 hover:bg-gray-700 transition-colors"
          >
            Guardar cambios
          </button>
          <Link
            href="/admin/medicos"
            className="px-6 py-3 rounded-xl font-medium text-sm text-gray-600 hover:bg-[var(--muted)] transition-colors"
          >
            Cancelar
          </Link>
        </div>
      </form>
    </div>
  );
}
