import Link from "next/link";
import Image from "next/image";
import { auth, signOut } from "@/auth";
import { redirect } from "next/navigation";

export default async function AdminLayout({ children }: { children: React.ReactNode }) {
  const session = await auth();
  if (!session?.user || session.user.role !== "ADMIN") {
    redirect("/login");
  }

  return (
    <div className="flex min-h-screen bg-[var(--muted)]">
      <aside className="w-64 bg-[var(--sidebar)] text-white flex flex-col fixed h-full border-r border-[var(--border)]">
        {/* Brand */}
        <div className="px-5 py-6 border-b border-white/10 flex flex-col items-center text-center">
          <Image
            src="/logo.jpg"
            alt="Peptide Technologies México"
            width={120}
            height={120}
            className="rounded-full object-cover ring-2 ring-[var(--primary)]/40 shadow-lg shadow-[var(--primary)]/20 mb-3"
          />
          <p className="text-xs text-[var(--text-muted)] uppercase tracking-widest">Panel Admin</p>
        </div>

        {/* User */}
        <div className="px-5 py-4 border-b border-white/10">
          <p className="text-sm text-white font-semibold">{session.user.name}</p>
          <p className="text-xs text-[var(--text-muted)]">Administrador</p>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-0.5">
          {[
            { href: "/admin", label: "Dashboard", icon: "▦" },
            { href: "/admin/medicos", label: "Médicos", icon: "◈" },
            { href: "/admin/pacientes", label: "Pacientes", icon: "◉" },
            { href: "/admin/ingresos", label: "Ingresos", icon: "◎" },
          ].map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-[var(--text-muted)] hover:bg-[var(--primary)]/10 hover:text-[var(--primary)] transition-all"
            >
              <span className="text-base">{item.icon}</span>
              {item.label}
            </Link>
          ))}
        </nav>

        {/* Sign out */}
        <div className="px-4 py-4 border-t border-white/10">
          <form
            action={async () => {
              "use server";
              await signOut({ redirectTo: "/login" });
            }}
          >
            <button
              type="submit"
              className="w-full text-left flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm text-[var(--text-muted)] hover:bg-red-500/10 hover:text-red-400 transition-all"
            >
              <span>↩</span> Cerrar sesión
            </button>
          </form>
        </div>
      </aside>

      <main className="ml-64 flex-1 p-8">{children}</main>
    </div>
  );
}
