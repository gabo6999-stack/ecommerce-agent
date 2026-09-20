import { auth } from "@/auth";
import { redirect } from "next/navigation";

export default async function AuthRedirectPage() {
  const session = await auth();

  if (!session?.user) redirect("/login");

  const role = session.user.role as string;

  if (role === "ADMIN") redirect("/admin");
  if (role === "DOCTOR") redirect("/doctor");
  if (role === "PATIENT") redirect("/patient");

  redirect("/");
}
