"use client";

import { useState, useTransition } from "react";
import { saveSchedule, saveException, deleteException, type TimeBlock } from "@/app/actions/schedule";

// ─── Constants ────────────────────────────────────────────────────────────────

const DAYS = [
  { label: "Lunes", value: 1 },
  { label: "Martes", value: 2 },
  { label: "Miércoles", value: 3 },
  { label: "Jueves", value: 4 },
  { label: "Viernes", value: 5 },
  { label: "Sábado", value: 6 },
  { label: "Domingo", value: 0 },
];

const TIMES: string[] = [];
for (let h = 6; h <= 22; h++) {
  TIMES.push(`${String(h).padStart(2, "0")}:00`);
  if (h < 22) TIMES.push(`${String(h).padStart(2, "0")}:30`);
}

const MONTH_NAMES = ["Enero","Febrero","Marzo","Abril","Mayo","Junio","Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"];

// ─── Types ────────────────────────────────────────────────────────────────────

type DayConfig = {
  active: boolean;
  morningStart: string;
  morningEnd: string;
  breakEnd: string;
  hasAfternoon: boolean;
  afternoonEnd: string;
};

type ScheduleState = Record<number, DayConfig>;
type ExceptionMap = Record<string, TimeBlock[]>;

// ─── Helpers ─────────────────────────────────────────────────────────────────

const DEFAULT: Omit<DayConfig, "active"> = {
  morningStart: "08:00",
  morningEnd: "13:00",
  breakEnd: "15:00",
  hasAfternoon: true,
  afternoonEnd: "19:00",
};

function configToBlocks(c: DayConfig): TimeBlock[] {
  if (!c.active) return [];
  if (!c.hasAfternoon) return [{ start: c.morningStart, end: c.morningEnd }];
  return [
    { start: c.morningStart, end: c.morningEnd },
    { start: c.breakEnd, end: c.afternoonEnd },
  ];
}

function buildInitial(saved: { dayOfWeek: number; blocks: TimeBlock[] }[]): ScheduleState {
  const state: ScheduleState = {};
  for (const d of DAYS) {
    const found = saved.find((s) => s.dayOfWeek === d.value);
    if (found && found.blocks.length > 0) {
      const b = found.blocks;
      state[d.value] = {
        active: true,
        morningStart: b[0].start,
        morningEnd: b[0].end,
        breakEnd: b.length > 1 ? b[1].start : "15:00",
        hasAfternoon: b.length > 1,
        afternoonEnd: b.length > 1 ? b[1].end : "19:00",
      };
    } else {
      state[d.value] = { active: false, ...DEFAULT };
    }
  }
  return state;
}

function slotCount(c: DayConfig): number {
  if (!c.active) return 0;
  const mins = (t: string) => { const [h, m] = t.split(":").map(Number); return h * 60 + m; };
  let count = Math.floor((mins(c.morningEnd) - mins(c.morningStart)) / 60);
  if (c.hasAfternoon) count += Math.floor((mins(c.afternoonEnd) - mins(c.breakEnd)) / 60);
  return Math.max(0, count);
}

function toDateKey(d: Date) {
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
}

// ─── TimeSelect ───────────────────────────────────────────────────────────────

function TimeSelect({ value, onChange, after }: { value: string; onChange: (v: string) => void; after?: string }) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className="px-2 py-1.5 rounded-lg border border-[var(--border)] text-sm bg-[var(--card)] text-[var(--foreground)] focus:outline-none focus:border-[var(--primary)] cursor-pointer"
    >
      {TIMES.filter((t) => !after || t > after).map((t) => (
        <option key={t} value={t}>{t}</option>
      ))}
    </select>
  );
}

// ─── DayCard ─────────────────────────────────────────────────────────────────

function DayCard({ day, config, onChange }: {
  day: { label: string; value: number };
  config: DayConfig;
  onChange: (c: DayConfig) => void;
}) {
  const count = slotCount(config);
  const set = (patch: Partial<DayConfig>) => onChange({ ...config, ...patch });

  return (
    <div className={`rounded-xl border p-4 transition-all ${
      config.active
        ? "border-[var(--primary)]/30 bg-[var(--card)]"
        : "border-[var(--border)] bg-[var(--muted)] opacity-60"
    }`}>
      {/* Day header */}
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-3">
          <button type="button" onClick={() => set({ active: !config.active })}
            className={`relative w-10 h-5 rounded-full transition-colors flex-shrink-0 ${
              config.active ? "bg-[var(--primary)]" : "bg-[var(--border)]"
            }`}
          >
            <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${
              config.active ? "translate-x-5" : "translate-x-0.5"
            }`} />
          </button>
          <span className={`font-semibold text-sm ${config.active ? "text-[var(--foreground)]" : "text-[var(--text-muted)]"}`}>
            {day.label}
          </span>
        </div>
        {config.active && count > 0 && (
          <span className="text-xs text-[var(--text-muted)]">
            {count} consulta{count !== 1 ? "s" : ""} posible{count !== 1 ? "s" : ""}
          </span>
        )}
      </div>

      {config.active ? (
        <div className="grid grid-cols-3 gap-3">

          {/* Matutino */}
          <div className="bg-[var(--muted)] rounded-xl p-3 space-y-2">
            <p className="text-xs font-semibold text-[var(--primary)]">🌅 Matutino</p>
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                <span className="w-9">Inicio</span>
                <TimeSelect value={config.morningStart} onChange={(v) => set({ morningStart: v })} />
              </div>
              <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                <span className="w-9">Fin</span>
                <TimeSelect value={config.morningEnd} after={config.morningStart} onChange={(v) => {
                  const patch: Partial<DayConfig> = { morningEnd: v };
                  if (v >= config.breakEnd) patch.breakEnd = TIMES.find(t => t > v) ?? v;
                  onChange({ ...config, ...patch });
                }} />
              </div>
            </div>
          </div>

          {/* Descanso */}
          <div className="bg-[var(--muted)] rounded-xl p-3 space-y-2">
            <p className="text-xs font-semibold text-[var(--text-muted)]">🍽 Descanso</p>
            <div className="flex flex-col gap-1.5">
              <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                <span className="w-9">Inicio</span>
                <span className="px-2 py-1.5 rounded-lg border border-[var(--border)] text-sm bg-[var(--muted)] text-[var(--text-muted)] select-none">
                  {config.morningEnd}
                </span>
              </div>
              <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                <span className="w-9">Fin</span>
                <TimeSelect value={config.breakEnd} after={config.morningEnd} onChange={(v) => {
                  const patch: Partial<DayConfig> = { breakEnd: v };
                  if (config.hasAfternoon && v >= config.afternoonEnd) {
                    patch.afternoonEnd = TIMES.find(t => t > v) ?? v;
                  }
                  onChange({ ...config, ...patch });
                }} />
              </div>
            </div>
          </div>

          {/* Vespertino */}
          <div className="bg-[var(--muted)] rounded-xl p-3 space-y-2">
            <div className="flex items-center justify-between">
              <p className={`text-xs font-semibold ${config.hasAfternoon ? "text-[var(--primary)]" : "text-[var(--text-muted)]"}`}>
                🌆 Vespertino
              </p>
              <button type="button" onClick={() => set({ hasAfternoon: !config.hasAfternoon })}
                className={`text-xs font-medium transition-colors ${
                  config.hasAfternoon ? "text-red-400 hover:text-red-300" : "text-[var(--primary)] hover:text-[var(--primary-light)]"
                }`}
              >
                {config.hasAfternoon ? "× quitar" : "+ agregar"}
              </button>
            </div>
            {config.hasAfternoon ? (
              <div className="flex flex-col gap-1.5">
                <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                  <span className="w-9">Inicio</span>
                  <span className="px-2 py-1.5 rounded-lg border border-[var(--border)] text-sm bg-[var(--muted)] text-[var(--text-muted)] select-none">
                    {config.breakEnd}
                  </span>
                </div>
                <div className="flex items-center gap-1.5 text-xs text-[var(--text-muted)]">
                  <span className="w-9">Fin</span>
                  <TimeSelect value={config.afternoonEnd} after={config.breakEnd} onChange={(v) => set({ afternoonEnd: v })} />
                </div>
              </div>
            ) : (
              <p className="text-xs text-[var(--text-muted)] italic pt-1">Sin turno vespertino</p>
            )}
          </div>

        </div>
      ) : (
        <p className="text-xs text-[var(--text-muted)] italic">No disponible este día</p>
      )}
    </div>
  );
}

// ─── ExceptionEditor ─────────────────────────────────────────────────────────

function ExceptionEditor({ dateKey, initial, onSave, onCancel }: {
  dateKey: string; initial: TimeBlock[] | null;
  onSave: (blocks: TimeBlock[]) => void; onCancel: () => void;
}) {
  const [type, setType] = useState<"off" | "custom">(
    initial !== null && initial.length > 0 ? "custom" : "off"
  );
  const [morningStart, setMorningStart] = useState(
    initial && initial.length > 0 ? initial[0].start : "09:00"
  );
  const [morningEnd, setMorningEnd] = useState(
    initial && initial.length > 0 ? initial[0].end : "13:00"
  );
  const [breakEnd, setBreakEnd] = useState(
    initial && initial.length > 1 ? initial[1].start : "15:00"
  );
  const [hasAfternoon, setHasAfternoon] = useState(
    initial ? initial.length > 1 : false
  );
  const [afternoonEnd, setAfternoonEnd] = useState(
    initial && initial.length > 1 ? initial[1].end : "19:00"
  );

  const d = new Date(dateKey + "T12:00:00");
  const label = d.toLocaleDateString("es-MX", { weekday: "long", day: "numeric", month: "long" });

  function handleSave() {
    if (type === "off") { onSave([]); return; }
    const blocks: TimeBlock[] = [{ start: morningStart, end: morningEnd }];
    if (hasAfternoon) blocks.push({ start: breakEnd, end: afternoonEnd });
    onSave(blocks);
  }

  return (
    <div className="bg-[var(--card)] border border-[var(--primary)]/40 rounded-xl p-4 shadow-xl">
      <p className="text-sm font-semibold text-[var(--foreground)] mb-3 capitalize">{label}</p>

      <div className="flex gap-2 mb-4">
        {(["off", "custom"] as const).map((t) => (
          <button key={t} type="button" onClick={() => setType(t)}
            className={`flex-1 py-2 rounded-lg text-xs font-medium border transition-colors ${
              type === t
                ? "bg-[var(--primary)] text-[var(--primary-dark)] border-[var(--primary)]"
                : "border-[var(--border)] text-[var(--text-muted)] hover:border-[var(--primary)]"
            }`}
          >
            {t === "off" ? "🚫 Día libre" : "⏰ Horario especial"}
          </button>
        ))}
      </div>

      {type === "custom" && (
        <div className="grid grid-cols-3 gap-2 mb-3">
          <div className="space-y-1">
            <p className="text-xs font-semibold text-[var(--primary)]">🌅 Matutino</p>
            <TimeSelect value={morningStart} onChange={setMorningStart} />
            <TimeSelect value={morningEnd} after={morningStart} onChange={setMorningEnd} />
          </div>
          <div className="space-y-1">
            <p className="text-xs font-semibold text-[var(--text-muted)]">🍽 Descanso</p>
            <span className="block px-2 py-1.5 rounded-lg border border-[var(--border)] text-xs text-[var(--text-muted)]">{morningEnd}</span>
            <TimeSelect value={breakEnd} after={morningEnd} onChange={setBreakEnd} />
          </div>
          <div className="space-y-1">
            <div className="flex items-center justify-between">
              <p className={`text-xs font-semibold ${hasAfternoon ? "text-[var(--primary)]" : "text-[var(--text-muted)]"}`}>🌆 Vespertino</p>
              <button type="button" onClick={() => setHasAfternoon(!hasAfternoon)}
                className="text-[9px] text-[var(--primary)] hover:underline">{hasAfternoon ? "× quitar" : "+ agregar"}</button>
            </div>
            {hasAfternoon ? (
              <>
                <span className="block px-2 py-1.5 rounded-lg border border-[var(--border)] text-xs text-[var(--text-muted)]">{breakEnd}</span>
                <TimeSelect value={afternoonEnd} after={breakEnd} onChange={setAfternoonEnd} />
              </>
            ) : (
              <p className="text-xs text-[var(--text-muted)] italic pt-2">Sin vespertino</p>
            )}
          </div>
        </div>
      )}

      <div className="flex gap-2 mt-3">
        <button type="button" onClick={onCancel}
          className="flex-1 py-1.5 text-xs rounded-lg border border-[var(--border)] text-[var(--text-muted)] hover:bg-[var(--muted)]">
          Cancelar
        </button>
        <button type="button" onClick={handleSave}
          className="flex-1 py-1.5 text-xs rounded-lg bg-[var(--primary)] text-[var(--primary-dark)] font-semibold hover:bg-[var(--primary-light)]">
          Guardar
        </button>
      </div>
    </div>
  );
}

// ─── ExceptionsPanel ─────────────────────────────────────────────────────────

function ExceptionsPanel({ exceptions, onSave, onDelete }: {
  exceptions: ExceptionMap;
  onSave: (date: string, blocks: TimeBlock[]) => void;
  onDelete: (date: string) => void;
}) {
  const today = new Date(); today.setHours(0, 0, 0, 0);
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const [editing, setEditing] = useState<string | null>(null);

  function prevMonth() {
    if (viewMonth === 0) { setViewYear(y => y - 1); setViewMonth(11); }
    else setViewMonth(m => m - 1);
  }
  function nextMonth() {
    if (viewMonth === 11) { setViewYear(y => y + 1); setViewMonth(0); }
    else setViewMonth(m => m + 1);
  }

  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  const startDow = (new Date(viewYear, viewMonth, 1).getDay() + 6) % 7;
  const cells: (Date | null)[] = [
    ...Array(startDow).fill(null),
    ...Array.from({ length: daysInMonth }, (_, i) => new Date(viewYear, viewMonth, i + 1)),
  ];
  while (cells.length % 7 !== 0) cells.push(null);

  return (
    <div>
      <div className="flex items-center justify-between mb-4">
        <button type="button" onClick={prevMonth}
          className="p-1.5 rounded-lg hover:bg-[var(--muted)] text-[var(--text-muted)]">‹</button>
        <span className="font-semibold text-[var(--foreground)] text-sm">
          {MONTH_NAMES[viewMonth]} {viewYear}
        </span>
        <button type="button" onClick={nextMonth}
          className="p-1.5 rounded-lg hover:bg-[var(--muted)] text-[var(--text-muted)]">›</button>
      </div>

      <div className="grid grid-cols-7 mb-1">
        {["Lun","Mar","Mié","Jue","Vie","Sáb","Dom"].map((d) => (
          <div key={d} className="text-center text-xs font-semibold text-[var(--text-muted)] py-1">{d}</div>
        ))}
      </div>

      <div className="grid grid-cols-7 gap-1 mb-6">
        {cells.map((date, i) => {
          if (!date) return <div key={i} />;
          const key = toDateKey(date);
          const isPast = date < today;
          const isToday = date.toDateString() === today.toDateString();
          const exc = exceptions[key];
          const isOff = key in exceptions && exc.length === 0;
          const isCustom = key in exceptions && exc.length > 0;

          return (
            <div key={key} className="relative">
              <button type="button" disabled={isPast}
                onClick={() => setEditing(editing === key ? null : key)}
                className={`w-full aspect-square rounded-lg text-xs font-medium transition-colors flex flex-col items-center justify-center gap-0.5
                  ${isPast ? "text-[var(--text-muted)]/30 cursor-default" : "cursor-pointer hover:bg-[var(--primary)]/10 text-[var(--foreground)]"}
                  ${isToday ? "ring-2 ring-[var(--primary)]" : ""}
                  ${isOff ? "bg-red-500/15 !text-red-400" : ""}
                  ${isCustom ? "bg-[var(--primary)]/15 !text-[var(--primary)]" : ""}
                  ${editing === key ? "!bg-[var(--primary)] !text-[var(--primary-dark)]" : ""}
                `}
              >
                <span>{date.getDate()}</span>
                {isOff && <span className="text-[8px] leading-none">libre</span>}
                {isCustom && <span className="text-[8px] leading-none">especial</span>}
              </button>
              {editing === key && (
                <div className="absolute top-full left-0 z-20 w-72 mt-1">
                  <ExceptionEditor
                    dateKey={key}
                    initial={key in exceptions ? exc : null}
                    onSave={(blocks) => { onSave(key, blocks); setEditing(null); }}
                    onCancel={() => setEditing(null)}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>

      {Object.keys(exceptions).length > 0 ? (
        <div>
          <p className="text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wide mb-2">Excepciones activas</p>
          <div className="space-y-2">
            {Object.entries(exceptions).sort(([a], [b]) => a.localeCompare(b)).map(([key, blocks]) => {
              const d = new Date(key + "T12:00:00");
              return (
                <div key={key} className="flex items-center justify-between px-3 py-2 rounded-lg border border-[var(--border)] bg-[var(--muted)] text-sm">
                  <div>
                    <span className="font-medium text-[var(--foreground)] capitalize">
                      {d.toLocaleDateString("es-MX", { weekday: "short", day: "numeric", month: "short" })}
                    </span>
                    <span className="ml-2 text-[var(--text-muted)] text-xs">
                      {blocks.length === 0 ? "🚫 Día libre" : blocks.map(b => `${b.start}–${b.end}`).join(" · ")}
                    </span>
                  </div>
                  <button type="button" onClick={() => onDelete(key)}
                    className="text-[var(--text-muted)] hover:text-red-400 text-xs ml-3">✕</button>
                </div>
              );
            })}
          </div>
        </div>
      ) : (
        <p className="text-xs text-[var(--text-muted)] text-center py-3">
          Haz clic en un día futuro para agregar una excepción
        </p>
      )}
    </div>
  );
}

// ─── Main ─────────────────────────────────────────────────────────────────────

export default function ScheduleEditor({
  savedSchedule,
  savedExceptions,
}: {
  savedSchedule: { dayOfWeek: number; blocks: TimeBlock[] }[];
  savedExceptions: { date: string; blocks: TimeBlock[] }[];
}) {
  const [schedule, setSchedule] = useState<ScheduleState>(() => buildInitial(savedSchedule));
  const [exceptions, setExceptions] = useState<ExceptionMap>(() =>
    Object.fromEntries(savedExceptions.map((e) => [e.date, e.blocks]))
  );
  const [status, setStatus] = useState<"idle" | "ok" | "error">("idle");
  const [isPending, startTransition] = useTransition();

  function handleSave() {
    const days = DAYS.filter((d) => schedule[d.value].active).map((d) => ({
      dayOfWeek: d.value,
      blocks: configToBlocks(schedule[d.value]),
    }));
    startTransition(async () => {
      try {
        await saveSchedule(days);
        setStatus("ok");
      } catch {
        setStatus("error");
      }
    });
  }

  function handleSaveException(date: string, blocks: TimeBlock[]) {
    startTransition(async () => {
      try {
        await saveException(date, blocks);
        setExceptions((p) => ({ ...p, [date]: blocks }));
      } catch (e) { console.error(e); }
    });
  }

  function handleDeleteException(date: string) {
    startTransition(async () => {
      try {
        await deleteException(date);
        setExceptions((p) => { const n = { ...p }; delete n[date]; return n; });
      } catch (e) { console.error(e); }
    });
  }

  return (
    <div className="space-y-6">

      {/* ── Plantilla semanal ── */}
      <div className="bg-[var(--card)] rounded-xl border border-[var(--border)] p-6">
        <h2 className="font-bold text-[var(--foreground)] mb-1">Plantilla semanal</h2>
        <p className="text-sm text-[var(--text-muted)] mb-5">
          Activa los días que atiendes y define tu turno matutino, descanso y vespertino (opcional).
        </p>

        <div className="space-y-3">
          {DAYS.map((d) => (
            <DayCard
              key={d.value}
              day={d}
              config={schedule[d.value]}
              onChange={(c) => {
                setSchedule((p) => ({ ...p, [d.value]: c }));
                setStatus("idle");
              }}
            />
          ))}
        </div>

        <div className="flex items-center gap-4 mt-6">
          <button onClick={handleSave} disabled={isPending}
            className="px-6 py-2.5 rounded-xl font-semibold text-sm text-[var(--primary-dark)] bg-[var(--primary)] hover:bg-[var(--primary-light)] disabled:opacity-50 transition-colors">
            {isPending ? "Guardando..." : "Guardar plantilla"}
          </button>
          {status === "ok" && <span className="text-sm text-green-400 font-medium">✓ Guardado</span>}
          {status === "error" && <span className="text-sm text-red-400 font-medium">Error al guardar</span>}
        </div>
      </div>

      {/* ── Excepciones ── */}
      <div className="bg-[var(--card)] rounded-xl border border-[var(--border)] p-6">
        <h2 className="font-bold text-[var(--foreground)] mb-1">Excepciones</h2>
        <p className="text-sm text-[var(--text-muted)] mb-5">
          Haz clic en un día futuro para marcarlo como{" "}
          <strong className="text-[var(--foreground)]">día libre</strong> o asignarle un{" "}
          <strong className="text-[var(--foreground)]">horario especial</strong> que reemplazará tu plantilla ese día.
        </p>
        <ExceptionsPanel
          exceptions={exceptions}
          onSave={handleSaveException}
          onDelete={handleDeleteException}
        />
      </div>

    </div>
  );
}
