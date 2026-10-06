import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check for session cookies set by the backend
  const hasToken = request.cookies.has('access_token') || request.cookies.has('refresh_token');

  // Only protect /drive — unauthenticated users get sent to landing page
  if (pathname.startsWith('/drive') && !hasToken) {
    return NextResponse.redirect(new URL('/', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/drive/:path*'],
};
