import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function proxy(request: NextRequest) {
  // Check for session cookies set by the backend
  const hasToken = request.cookies.has('access_token') || request.cookies.has('refresh_token');

  // Protect /drive routes
  if (request.nextUrl.pathname.startsWith('/drive') && !hasToken) {
    // Redirect unauthenticated users to the landing page
    return NextResponse.redirect(new URL('/', request.url));
  }

  // Redirect authenticated users away from the landing page to their drive
  if (request.nextUrl.pathname === '/' && hasToken) {
    return NextResponse.redirect(new URL('/drive', request.url));
  }

  return NextResponse.next();
}

export const config = {
  matcher: ['/', '/drive/:path*'],
};
