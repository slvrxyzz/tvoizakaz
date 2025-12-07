import { NextRequest, NextResponse } from 'next/server'

import { getApiUrl } from '@/utils/config'

export async function POST(request: NextRequest) {
  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const body = await request.json().catch(() => null)
  if (!body || typeof body !== 'object' || typeof body.message !== 'string') {
    return NextResponse.json({ detail: 'Message is required' }, { status: 400 })
  }

  const backendResponse = await fetch(`${getApiUrl()}/api/v1/admin/support/broadcast`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Cookie: request.headers.get('cookie') ?? '',
    },
    body: JSON.stringify(body),
    cache: 'no-store',
  })

  const payload = await backendResponse.json().catch(() => null)
  return NextResponse.json(payload ?? { success: backendResponse.ok }, { status: backendResponse.status })
}

