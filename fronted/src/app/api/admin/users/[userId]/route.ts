import { NextRequest, NextResponse } from 'next/server'

import { getApiUrl } from '@/utils/config'

const ensureAuth = (request: NextRequest) => {
  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }
  return request.headers.get('cookie') ?? ''
}

export async function PUT(request: NextRequest, { params }: { params: { userId: string } }) {
  const cookieHeader = ensureAuth(request)
  if (cookieHeader instanceof NextResponse) {
    return cookieHeader
  }

  const body = await request.json().catch(() => null)
  if (!body || typeof body !== 'object') {
    return NextResponse.json({ detail: 'Invalid payload' }, { status: 400 })
  }

  const backendResponse = await fetch(`${getApiUrl()}/api/v1/admin/users/${params.userId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Cookie: cookieHeader,
    },
    body: JSON.stringify(body),
    cache: 'no-store',
  })

  const payload = await backendResponse.json().catch(() => null)
  return NextResponse.json(payload ?? { success: backendResponse.ok }, { status: backendResponse.status })
}

export async function DELETE(request: NextRequest, { params }: { params: { userId: string } }) {
  const cookieHeader = ensureAuth(request)
  if (cookieHeader instanceof NextResponse) {
    return cookieHeader
  }

  const backendResponse = await fetch(`${getApiUrl()}/api/v1/admin/users/${params.userId}`, {
    method: 'DELETE',
    headers: {
      Cookie: cookieHeader,
    },
    cache: 'no-store',
  })

  const payload = await backendResponse.json().catch(() => null)
  return NextResponse.json(payload ?? { success: backendResponse.ok }, { status: backendResponse.status })
}

