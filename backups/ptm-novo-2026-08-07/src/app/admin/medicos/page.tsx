import { prisma } from "@/lib/prisma";
import { revalidatePath } from "next/cache";
import bcrypt from "bcryptjs";
import Link from "next/link";
import { THERAPY_AREAS, AREA_LABEL, parseTherapyAreas } from "@/lib/therapyAreas";

const VERIF_BADGE = {
  NOT_SUBMITTED: { label: "Sin verificar", cls: "bg-gray-100 text-gray-500" },
  PENDING_REVIEW: { label: "⏳ En revisión", cls: "bg-yellow-100 text-yellow-700" },
  APPROVED: { label: "✅ Verificado", cls: "bg-green-100 text-green-700" },
  REJECTED: { label: "⚠️ Rechazado", cls: "bg-red-100 text-red-700" },
} as const;

export default async function AdminMedicosPage() {
  const doctors = await prisma.doctor.findMany({
    include: {
      user: true,
      _count: { select: { consultations: true } },
      consultations: {
        where: { status: "COMPLETED" },
        select: { id: true },
      },
    },
    orderBy: { createdAt: "asc" },
  });

  async function addDoctor(formData: FormData) {
    "use server";
    const name = formData.get("name") as string;
    const email = formData.get("email") as string;
    const password = formData.get("password") as string;
    const license = formData.get("license") as string;
    const specialty = (formData.get("specialty") as string) || "Peptide Therapy";
    // Rubros marcados (checkboxes con name="therapyAreas").
    const therapyAreas = parseTherapyAreas(formData.getAll("therapyAreas") as string[]);

    if (!name || !email || !password || !license) return;

    const hashed = await bcrypt.hash(password, 10);

    const existing = await prisma.user.findUnique({ where: { email } });
    if (existing) return;

    const user = await prisma.user.create({
      data: { name, email, password: hashed, role: "DOCTOR" },
    });

    await prisma.doctor.create({
      data: { userId: user.id, licenseNumber: license, specialty, therapyAreas },
    });

    revalidatePath("/admin/medicos");
  }

  async function toggleActive(formData: FormData) {
    "use server";
    const doctorId = formData.get("doctorId") as string;
    const current = formData.get("current") === "true";

    await prisma.doctor.update({
      where: { id: doctorId },
      data: { isActive: !current },
    });

    revalidatePath("/admin/medicos");
  }

  return (
    <div>
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-900">Médicos</h1>
        <p className="text-gray-500 text-sm mt-1">{doctors.length} registrado{doctors.length !== 1 ? "s" : ""}</p>
      </div>

      {/* Doctors table */}
      <div className="bg-white rounded-xl border border-[var(--border)] overflow-hidden mb-6">
        {doctors.length === 0 ? (
          <div className="text-center py-12 text-gray-400">
            <p className="text-3xl mb-2">👨‍⚕️</p>
            <p className="text-sm">Sin médicos registrados. Agrega el primero abajo.</p>
          </div>
        ) : (
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--border)] bg-[var(--muted)]">
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Médico
                </th>
                <th className="text-left px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Licencia
                </th>
                <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Consultas
                </th>
                <th className="text-right px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Ganado ($1,000 c/u)
                </th>
                <th className="text-center px-5 py-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
                <th className="px-5 py-3" />
              </tr>
            </thead>
            <tbody className="divide-y divide-[var(--border)]">
              {doctors.map((d) => {
                const completed = d.consultations.length;
                // Split fijo del modelo limpio: $1,000 MXN por consulta completada.
                const earnings = completed * 1000;
                return (
                  <tr key={d.id} className="hover:bg-[var(--muted)] transition-colors">
                    <td className="px-5 py-4">
                      <div className="flex items-center gap-3">
                        <div className="w-9 h-9 rounded-full bg-[var(--accent-light)] flex items-center justify-center text-[var(--primary)] font-bold text-sm shrink-0">
                          {d.user.name.charAt(0).toUpperCase()}
                        </div>
                        <div>
                          <p className="font-medium text-gray-900">Dr. {d.user.name}</p>
                          <p className="text-xs text-gray-400">{d.user.email}</p>
                          {d.therapyAreas.length > 0 && (
                            <div className="flex flex-wrap gap-1 mt-1.5">
                              {d.therapyAreas.map((area) => (
                                <span
                                  key={area}
                                  className="px-2 py-0.5 rounded-full bg-[var(--muted)] text-[10px] font-medium text-gray-600"
                                >
                                  {AREA_LABEL[area]}
                                </span>
                              ))}
                            </div>
                          )}
                          {d.areasReviewPending && (
                            <Link
                              href={`/admin/medicos/${d.id}`}
                              className="inline-block mt-1.5 px-2 py-0.5 rounded-full bg-yellow-100 text-yellow-700 text-[10px] font-semibold hover:bg-yellow-200 transition-colors"
                            >
                              ⏳ Cambio de rubros pendiente
                            </Link>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-5 py-4 text-gray-600 font-mono text-xs">{d.licenseNumber}</td>
                    <td className="px-5 py-4 text-center">
                      <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-[var(--muted)] text-xs font-bold text-gray-700">
                        {d._count.consultations}
                      </span>
                    </td>
                    <td className="px-5 py-4 text-right font-semibold text-gray-800">
                      ${earnings.toLocaleString()} MXN
                    </td>
                    <td className="px-5 py-4 text-center">
                      <div className="flex flex-col items-center gap-1">
                        <span
                          className={`px-2.5 py-1 rounded-full text-xs font-semibold ${
                            d.isActive
                              ? "bg-green-100 text-green-700"
                              : "bg-gray-100 text-gray-500"
                          }`}
                        >
                          {d.isActive ? "Activo" : "Inactivo"}
                        </span>
                        <span
                          className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${VERIF_BADGE[d.verificationStatus].cls}`}
                        >
                          {VERIF_BADGE[d.verificationStatus].label}
                        </span>
                      </div>
                    </td>
                    <td className="px-5 py-4">
                      <div className="flex items-center justify-end gap-3">
                        <Link
                          href={`/admin/medicos/${d.id}`}
                          className="text-xs text-gray-500 hover:text-gray-900 font-medium transition-colors"
                        >
                          Editar
                        </Link>
                        <form action={toggleActive}>
                          <input type="hidden" name="doctorId" value={d.id} />
                          <input type="hidden" name="current" value={String(d.isActive)} />
                          <button
                            type="submit"
                            className="text-xs text-gray-400 hover:text-gray-700 transition-colors"
                          >
                            {d.isActive ? "Desactivar" : "Activar"}
                          </button>
                        </form>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        )}
      </div>

      {/* Add doctor form */}
      <div className="bg-white rounded-xl border border-[var(--border)] p-6">
        <h2 className="font-bold text-gray-900 mb-1">Agregar médico</h2>
        <p className="text-sm text-gray-500 mb-5">
          Crea la cuenta del médico. Le debes compartir el email y contraseña para que acceda al portal.
        </p>

        <form action={addDoctor} className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Nombre completo</label>
            <input
              type="text"
              name="name"
              required
              placeholder="Dra. Ana García López"
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Correo electrónico</label>
            <input
              type="email"
              name="email"
              required
              placeholder="doctora@correo.com"
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Contraseña temporal</label>
            <input
              type="password"
              name="password"
              required
              minLength={8}
              placeholder="Mínimo 8 caracteres"
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Número de cédula / licencia
            </label>
            <input
              type="text"
              name="license"
              required
              placeholder="12345678"
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
              placeholder="Peptide Therapy"
              className="w-full px-4 py-3 rounded-xl border border-[var(--border)] text-sm focus:outline-none focus:border-gray-500 transition-colors"
            />
          </div>

          {/* Rubros de terapia que atiende (multi-selección) */}
          <div className="col-span-2">
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

          <div className="col-span-2 flex items-end">
            <button
              type="submit"
              className="w-full py-3 rounded-xl font-semibold text-white text-sm bg-gray-900 hover:bg-gray-700 transition-colors"
            >
              Crear médico →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
