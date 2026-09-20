import NextAuth from "next-auth";
import { authConfig } from "./auth.config";
import { NextResponse } from "next/server";

const { auth } = NextAuth(authConfig);

export default auth((req) => {
  const { pathname } = req.nextUrl;
  const role = req.auth?.user?.role as string | undefined;

  if (pathname.startsWith("/doctor") && role !== "DOCTOR" && role !== "ADMIN") {
    return NextResponse.redirect(new URL("/login?from=doctor", req.url));
  }

  if (pathname.startsWith("/admin") && role !== "ADMIN") {
    return NextResponse.redirect(new URL("/login?from=admin", req.url));
  }

  if (pathname.startsWith("/patient") && role !== "PATIENT" && role !== "ADMIN") {
    return NextResponse.redirect(new URL("/login?from=patient", req.url));
  }

  return NextResponse.next();
});

export const config = {
  matcher: ["/doctor/:path*", "/admin/:path*", "/patient/:path*"],
};
