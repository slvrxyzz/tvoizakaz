import { NextRequest, NextResponse } from 'next/server'

import { getApiUrl } from '@/utils/config'

export async function GET(request: NextRequest) {
  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const { searchParams } = new URL(request.url)
  const page = parseInt(searchParams.get('page') ?? '1', 10)
  const limit = parseInt(searchParams.get('limit') ?? '20', 10)

  const backendUrl = new URL(`${getApiUrl()}/api/v1/admin/support/requests`)
  backendUrl.searchParams.set('page', String(page))
  backendUrl.searchParams.set('page_size', String(limit))

  try {
    const response = await fetch(backendUrl.toString(), {
      headers: {
        Cookie: request.headers.get('cookie') ?? '',
      },
      cache: 'no-store',
    })

    const payload = await response.json().catch(() => null)

    if (!response.ok) {
      return NextResponse.json(
        payload ?? { detail: 'Failed to load support requests' },
        { status: response.status }
      )
    }

    return NextResponse.json({
      data: payload?.data ?? [],
      total: payload?.total ?? 0,
      page: payload?.page ?? page,
      pageSize: payload?.page_size ?? limit,
      totalPages: payload?.total_pages ?? 1,
    })
  } catch (error) {
    console.error('Support requests proxy error:', error)
    return NextResponse.json({ detail: 'Internal server error' }, { status: 500 })
  }
}