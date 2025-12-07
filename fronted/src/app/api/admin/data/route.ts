import { NextRequest, NextResponse } from 'next/server'

import { getApiUrl } from '@/utils/config'

const typeToEndpoint: Record<string, string> = {
  users: '/api/v1/admin/users',
  orders: '/api/v1/admin/orders',
  offers: '/api/v1/admin/offers',
}

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url)
  const page = parseInt(searchParams.get('page') ?? '1', 10)
  const limit = parseInt(searchParams.get('limit') ?? '10', 10)
  const type = searchParams.get('type') ?? 'users'

  const endpoint = typeToEndpoint[type]
  if (!endpoint) {
    return NextResponse.json({ detail: 'Invalid type parameter' }, { status: 400 })
  }

  const accessCookie = request.cookies.get('access_token')
  if (!accessCookie) {
    return NextResponse.json({ detail: 'Unauthorized' }, { status: 401 })
  }

  const backendUrl = new URL(`${getApiUrl()}${endpoint}`)
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
        payload ?? { detail: 'Failed to load admin data' },
        { status: response.status }
      )
    }

    const total = payload?.total ?? 0
    const totalPages = payload?.total_pages ?? payload?.totalPages ?? 1
    const backendPage = payload?.page ?? page
    const backendPageSize = payload?.page_size ?? payload?.pageSize ?? limit

    return NextResponse.json({
      data: payload?.data ?? [],
      total,
      page: backendPage,
      pageSize: backendPageSize,
      totalPages,
    })
  } catch (error) {
    console.error('Admin data proxy error:', error)
    return NextResponse.json({ detail: 'Internal server error' }, { status: 500 })
  }
}