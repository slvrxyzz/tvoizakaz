import { NextRequest, NextResponse } from 'next/server'

import { getApiUrl } from '@/utils/config'

export async function DELETE(request: NextRequest, { params }: { params: { offerId: string } }) {
  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const backendResponse = await fetch(`${getApiUrl()}/api/v1/admin/offers/${params.offerId}`, {
    method: 'DELETE',
    headers: {
      Cookie: request.headers.get('cookie') ?? '',
    },
    cache: 'no-store',
  })

  const payload = await backendResponse.json().catch(() => null)
  return NextResponse.json(payload ?? { success: backendResponse.ok }, { status: backendResponse.status })
}

