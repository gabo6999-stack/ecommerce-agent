import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import SlotPicker from "@/components/SlotPicker";
import type { TimeBlock } from "@/app/actions/schedule";

export default async function AgendarPage() {
  const session = await auth();

  const patient = await prisma.patient.findFirst({
    where: { user: { email: session!.user!.email! } },
    include: {
      _count: {
        select: {
          consultations: { where: { status: { not: "CANCELLED" } } },
        },
      },
    },
  });

  const isFirstConsultation = !patient || patient._count.consultations === 0;
  const slotDuration = isFirstConsultation ? 60 : 30;

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  const windowEnd = new Date(today);
  windowEnd.setDate(today.getDate() + 15);

  const activeDoctors = await prisma.doctor.findMany({
    where: { isActive: true, schedules: { some: {} } },
    include: {
      user: { select: { name: true } },
      schedules: { select: { dayOfWeek: true, blocks: true } },
      exceptions: {
        where: { date: { gte: today, lte: windowEnd } },
        select: { date: true, blocks: true },
      },
      consultations: {
        where: {
          scheduledAt: { gte: today, lte: windowEnd },
          status: { in: ["SCHEDULED", "IN_PROGRESS"] },
        },
        select: { scheduledAt: true, durationMinutes: true },
      },
    },
  });

  const doctors = activeDoctors.map((d) => ({
    doctorId: d.id,
    doctorName: d.user.name,
    schedules: d.schedules.map((s) => ({
      dayOfWeek: s.dayOfWeek,
      blocks: s.blocks as TimeBlock[],
    })),
    exceptions: d.exceptions.map((e) => ({
      date: e.date.toISOString().slice(0, 10),
      blocks: e.blocks as TimeBlock[],
    })),
    bookedSlots: d.consultations.map((c) => ({
      scheduledAt: c.scheduledAt.toISOString(),
      durationMinutes: c.durationMinutes,
    })),
  }));

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Agendar orientación médica</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Selecciona el día y horario que mejor te convenga
        </p>
      </div>

      {/* Consultation type badge */}
      <div
        className={`inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium mb-6 ${
          isFirstConsultation
            ? "bg-blue-50 text-blue-700 border border-blue-200"
            : "bg-purple-50 text-purple-700 border border-purple-200"
        }`}
      >
        <span>{isFirstConsultation ? "🩺" : "🔄"}</span>
        {isFirstConsultation
          ? "Primera orientación médica — 60 minutos (evaluación inicial)"
          : "Orientación médica de seguimiento — 30 minutos"}
      </div>

      {doctors.length === 0 ? (
        <div className="bg-white rounded-xl border border-[var(--border)] p-16 text-center text-gray-400">
          <p className="text-3xl mb-3">🗓️</p>
          <p className="text-sm font-medium">No hay horarios disponibles por el momento</p>
          <p className="text-xs mt-1">Los médicos aún no han configurado su disponibilidad</p>
        </div>
      ) : (
        <SlotPicker doctors={doctors} slotDuration={slotDuration} />
      )}
    </div>
  );
}
