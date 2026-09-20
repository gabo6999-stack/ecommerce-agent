"use server";

import { prisma } from "@/lib/prisma";
import { auth } from "@/auth";
import { revalidatePath } from "next/cache";
import { redirect } from "next/navigation";

export type TimeBlock = { start: string; end: string };

export type DaySchedule = {
  dayOfWeek: number;
  blocks: TimeBlock[];
};

export async function saveSchedule(days: DaySchedule[]) {
  const session = await auth();
  if (!session?.user?.email) throw new Error("No autenticado");

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session.user.email } },
  });
  if (!doctor) throw new Error("Médico no encontrado");

  await prisma.doctorSchedule.deleteMany({ where: { doctorId: doctor.id } });

  if (days.length > 0) {
    await prisma.doctorSchedule.createMany({
      data: days.map((d) => ({
        doctorId: doctor.id,
        dayOfWeek: d.dayOfWeek,
        blocks: d.blocks,
      })),
    });
  }

  revalidatePath("/doctor/disponibilidad");
}

export async function saveException(date: string, blocks: TimeBlock[]) {
  const session = await auth();
  if (!session?.user?.email) throw new Error("No autenticado");

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session.user.email } },
  });
  if (!doctor) throw new Error("Médico no encontrado");

  const dateObj = new Date(date + "T00:00:00.000Z");

  await prisma.doctorException.upsert({
    where: { doctorId_date: { doctorId: doctor.id, date: dateObj } },
    create: { doctorId: doctor.id, date: dateObj, blocks },
    update: { blocks },
  });

  revalidatePath("/doctor/disponibilidad");
}

export async function deleteException(date: string) {
  const session = await auth();
  if (!session?.user?.email) throw new Error("No autenticado");

  const doctor = await prisma.doctor.findFirst({
    where: { user: { email: session.user.email } },
  });
  if (!doctor) throw new Error("Médico no encontrado");

  const dateObj = new Date(date + "T00:00:00.000Z");

  await prisma.doctorException.deleteMany({
    where: { doctorId: doctor.id, date: dateObj },
  });

  revalidatePath("/doctor/disponibilidad");
}

export async function bookConsultation(
  doctorId: string,
  scheduledAt: string,
  durationMinutes: number
) {
  const session = await auth();
  if (!session?.user?.email) throw new Error("No autenticado");

  const patient = await prisma.patient.findFirst({
    where: { user: { email: session.user.email } },
  });
  if (!patient) throw new Error("Paciente no encontrado");

  const slotStart = new Date(scheduledAt).getTime();
  const slotEnd = slotStart + durationMinutes * 60 * 1000;

  const upcoming = await prisma.consultation.findMany({
    where: {
      doctorId,
      status: { in: ["SCHEDULED", "IN_PROGRESS"] },
      scheduledAt: {
        gte: new Date(slotStart - 60 * 60 * 1000),
        lte: new Date(slotEnd),
      },
    },
    select: { scheduledAt: true, durationMinutes: true },
  });

  const conflict = upcoming.some((c) => {
    const bookedStart = c.scheduledAt.getTime();
    const bookedEnd = bookedStart + c.durationMinutes * 60 * 1000;
    return bookedStart < slotEnd && bookedEnd > slotStart;
  });

  if (conflict) throw new Error("Este horario ya fue tomado, elige otro.");

  await prisma.consultation.create({
    data: {
      patientId: patient.id,
      doctorId,
      scheduledAt: new Date(scheduledAt),
      durationMinutes,
      status: "SCHEDULED",
      program: patient.program ?? "WEIGHT_LOSS",
    },
  });

  revalidatePath("/patient/consultas");
  revalidatePath("/patient/agendar");
  redirect("/patient/consultas");
}
