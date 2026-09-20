import { auth } from "@/auth";
import { prisma } from "@/lib/prisma";
import ScheduleEditor from "@/components/ScheduleEditor";
import type { TimeBlock } from "@/app/actions/schedule";

export default async function DisponibilidadPage() {
  const session = await auth();

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session!.user!.email! } },
    include: {
      schedules: { orderBy: { dayOfWeek: "asc" } },
      exceptions: { orderBy: { date: "asc" } },
    },
  });

  const savedSchedule = doctor?.schedules.map((s) => ({
    dayOfWeek: s.dayOfWeek,
    blocks: s.blocks as TimeBlock[],
  })) ?? [];

  const savedExceptions = doctor?.exceptions.map((e) => ({
    date: e.date.toISOString().slice(0, 10),
    blocks: e.blocks as TimeBlock[],
  })) ?? [];

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Mi disponibilidad</h1>
        <p className="text-sm text-gray-500 mt-0.5">
          Define los días y horarios en que puedes atender consultas
        </p>
      </div>

      <ScheduleEditor savedSchedule={savedSchedule} savedExceptions={savedExceptions} />
    </div>
  );
}
