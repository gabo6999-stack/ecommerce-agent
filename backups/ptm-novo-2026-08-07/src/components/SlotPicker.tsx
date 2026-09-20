"use client";

import { useState, useTransition } from "react";
import { bookConsultation } from "@/app/actions/schedule";

// ─── Types ────────────────────────────────────────────────────────────────────

type TimeBlock = { start: string; end: string };
type BookedSlot = { scheduledAt: string; durationMinutes: number };

type DoctorData = {
  doctorId: string;
  doctorName: string;
  schedules: { dayOfWeek: number; blocks: TimeBlock[] }[];
  exceptions: { date: string; blocks: TimeBlock[] }[];
  bookedSlots: BookedSlot[];
};

type Slot = {
  doctorId: string;
  doctorName: string;
  iso: string;
  label: string;
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

function toDateKey(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

function generateSlots(doctor: DoctorData, date: Date, slotDuration: number): Slot[] {
  const dateKey = toDateKey(date);

  // Exceptions override the weekly template
  const exception = doctor.exceptions.find((e) => e.date === dateKey);
  let blocks: TimeBlock[];

  if (exception) {
    if (exception.blocks.length === 0) return []; // day off
    blocks = exception.blocks;
  } else {
    const schedule = doctor.schedules.find((s) => s.dayOfWeek === date.getDay());
    if (!schedule || schedule.blocks.length === 0) return [];
    blocks = schedule.blocks;
  }

  const slots: Slot[] = [];

  for (const block of blocks) {
    const [sh, sm] = block.start.split(":").map(Number);
    const [eh, em] = block.end.split(":").map(Number);
    const startMins = sh * 60 + sm;
    const endMins = eh * 60 + em;

    for (let mins = startMins; mins + slotDuration <= endMins; mins += slotDuration) {
      const slotDate = new Date(date);
      slotDate.setHours(Math.floor(mins / 60), mins % 60, 0, 0);
      const slotStart = slotDate.getTime();
      const slotEnd = slotStart + slotDuration * 60 * 1000;

      const isBooked = doctor.bookedSlots.some((b) => {
        const bookedStart = new Date(b.scheduledAt).getTime();
        const bookedEnd = bookedStart + b.durationMinutes * 60 * 1000;
        return bookedStart < slotEnd && bookedEnd > slotStart;
      });

      if (!isBooked) {
        const h = String(Math.floor(mins / 60)).padStart(2, "0");
        const m = String(mins % 60).padStart(2, "0");
        slots.push({
          doctorId: doctor.doctorId,
          doctorName: doctor.doctorName,
          iso: slotDate.toISOString(),
          label: `${h}:${m}`,
        });
      }
    }
  }

  return slots;
}

function getNext14Days(): Date[] {
  const days: Date[] = [];
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  for (let i = 1; i <= 14; i++) {
    const d = new Date(today);
    d.setDate(today.getDate() + i);
    days.push(d);
  }
  return days;
}

const DAY_SHORT = ["Dom", "Lun", "Mar", "Mié", "Jue", "Vie", "Sáb"];
const MONTH_SHORT = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"];

// ─── Component ────────────────────────────────────────────────────────────────

export default function SlotPicker({
  doctors,
  slotDuration,
}: {
  doctors: DoctorData[];
  slotDuration: number;
}) {
  const days = getNext14Days();
  const [selectedDay, setSelectedDay] = useState<Date>(days[0]);
  const [confirming, setConfirming] = useState<Slot | null>(null);
  const [error, setError] = useState("");
  const [isPending, startTransition] = useTransition();

  const slotsForDay = doctors.flatMap((d) => generateSlots(d, selectedDay, slotDuration));

  function handleBook(slot: Slot) {
    setError("");
    setConfirming(slot);
  }

  function confirmBook() {
    if (!confirming) return;
    startTransition(async () => {
      try {
        await bookConsultation(confirming.doctorId, confirming.iso, slotDuration);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Error al reservar");
        setConfirming(null);
      }
    });
  }

  return (
    <div>
      {/* Date selector */}
      <div className="flex gap-2 overflow-x-auto pb-2 mb-6">
        {days.map((d) => {
          const isSelected = d.toDateString() === selectedDay.toDateString();
          const hasSlots = doctors.some((doc) => generateSlots(doc, d, slotDuration).length > 0);
          return (
            <button
              key={d.toISOString()}
              onClick={() => { setSelectedDay(d); setError(""); }}
              disabled={!hasSlots && !isSelected}
              className={`flex-shrink-0 w-16 py-3 rounded-xl text-center transition-colors border ${
                isSelected
                  ? "bg-[var(--primary)] text-white border-[var(--primary)]"
                  : hasSlots
                  ? "bg-white border-[var(--border)] hover:border-[var(--primary)] text-gray-900"
                  : "bg-[var(--muted)] border-[var(--border)] text-gray-400 cursor-default opacity-50"
              }`}
            >
              <p className="text-xs font-medium">{DAY_SHORT[d.getDay()]}</p>
              <p className="text-lg font-bold leading-tight">{d.getDate()}</p>
              <p className="text-xs">{MONTH_SHORT[d.getMonth()]}</p>
            </button>
          );
        })}
      </div>

      {/* Slots grid */}
      <div className="bg-white rounded-xl border border-[var(--border)] p-6">
        <h2 className="font-semibold text-gray-900 mb-4">
          {DAY_SHORT[selectedDay.getDay()]} {selectedDay.getDate()} de {MONTH_SHORT[selectedDay.getMonth()]}
          <span className="text-sm font-normal text-gray-500 ml-2">
            — {slotsForDay.length} horario{slotsForDay.length !== 1 ? "s" : ""} disponible{slotsForDay.length !== 1 ? "s" : ""}
          </span>
        </h2>

        {error && (
          <div className="mb-4 px-4 py-3 rounded-xl bg-red-50 border border-red-200 text-sm text-red-700">
            {error}
          </div>
        )}

        {slotsForDay.length === 0 ? (
          <div className="text-center py-10 text-gray-400">
            <p className="text-2xl mb-2">🗓️</p>
            <p className="text-sm">Sin horarios disponibles este día</p>
          </div>
        ) : (
          <div className="grid grid-cols-4 gap-3">
            {slotsForDay.map((slot) => (
              <button
                key={`${slot.doctorId}-${slot.iso}`}
                onClick={() => handleBook(slot)}
                className="flex flex-col items-center gap-1 p-4 rounded-xl border border-[var(--border)] hover:border-[var(--primary)] hover:bg-[var(--accent-light)] transition-colors group"
              >
                <span className="text-xl font-bold text-gray-900 group-hover:text-[var(--primary)]">
                  {slot.label}
                </span>
                <span className="text-xs text-gray-500">{slotDuration} min</span>
                <span className="text-xs text-gray-400">Dr. {slot.doctorName.split(" ")[0]}</span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Confirmation modal */}
      {confirming && (
        <div className="fixed inset-0 bg-black/40 flex items-center justify-center z-50 px-4">
          <div className="bg-white rounded-2xl p-6 max-w-sm w-full shadow-xl">
            <h3 className="text-lg font-bold text-gray-900 mb-1">Confirmar orientación médica</h3>
            <p className="text-sm text-gray-500 mb-5">Revisa los detalles antes de confirmar</p>

            <div className="bg-[var(--muted)] rounded-xl p-4 mb-5 space-y-2.5">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Tipo</span>
                <span className="font-medium text-gray-900">
                  {slotDuration === 60 ? "🩺 Primera orientación médica" : "🔄 Seguimiento"}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Médico</span>
                <span className="font-medium text-gray-900">Dr. {confirming.doctorName}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Fecha</span>
                <span className="font-medium text-gray-900">
                  {new Date(confirming.iso).toLocaleDateString("es-MX", {
                    weekday: "long", day: "numeric", month: "long",
                  })}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Hora</span>
                <span className="font-medium text-gray-900">{confirming.label} hrs</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Duración</span>
                <span className="font-medium text-gray-900">{slotDuration} minutos</span>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={() => setConfirming(null)}
                disabled={isPending}
                className="flex-1 py-2.5 rounded-xl border border-[var(--border)] text-sm font-medium text-gray-700 hover:bg-[var(--muted)] transition-colors"
              >
                Cancelar
              </button>
              <button
                onClick={confirmBook}
                disabled={isPending}
                className="flex-1 py-2.5 rounded-xl text-sm font-bold text-white bg-[var(--primary)] hover:bg-[var(--primary-light)] disabled:opacity-50 transition-colors"
              >
                {isPending ? "Reservando..." : "Confirmar cita"}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
