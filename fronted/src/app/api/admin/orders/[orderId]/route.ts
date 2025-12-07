import { NextRequest, NextResponse } from 'next/server'

import { getApiUrl } from '@/utils/config'

export async function DELETE(request: NextRequest, { params }: { params: { orderId: string } }) {
  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const backendResponse = await fetch(`${getApiUrl()}/api/v1/admin/orders/${params.orderId}`, {
    method: 'DELETE',
    headers: {
      Cookie: request.headers.get('cookie') ?? '',
    },
    cache: 'no-store',
  })

  const payload = await backendResponse.json().catch(() => null)
  return NextResponse.json(payload ?? { success: backendResponse.ok }, { status: backendResponse.status })
}

export async function PUT(request: NextRequest, { params }: { params: { orderId: string } }) {
  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const body = await request.json().catch(() => null)
  if (!body || typeof body !== 'object') {
    return NextResponse.json({ detail: 'Invalid payload' }, { status: 400 })
  }

  const backendResponse = await fetch(`${getApiUrl()}/api/v1/admin/orders/${params.orderId}`, {
    method: 'PUT',
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

