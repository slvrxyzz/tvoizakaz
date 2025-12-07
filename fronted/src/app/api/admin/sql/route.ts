import { NextRequest, NextResponse } from 'next/server'

import { getApiUrl } from '@/utils/config'

export async function POST(request: NextRequest) {
  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const body = await request.json().catch(() => null)
  if (!body || typeof body.query !== 'string') {
    return NextResponse.json({ detail: 'SQL query is required' }, { status: 400 })
  }

  const backendResponse = await fetch(`${getApiUrl()}/api/v1/admin/sql`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Cookie: request.headers.get('cookie') ?? '',
    },
    body: JSON.stringify({ query: body.query }),
    cache: 'no-store',
  })

  const payload = await backendResponse.json().catch(() => null)
  return NextResponse.json(
    payload ?? { success: backendResponse.ok },
    { status: backendResponse.status }
  )
}

