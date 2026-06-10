/** Server-side proxy to the FastAPI backend (Docker: http://backend:8000). */
export function getBackendUrl(): string {
  return (
    process.env.BACKEND_INTERNAL_URL ||
    process.env.NEXT_PUBLIC_API_URL ||
    'http://backend:8000'
  )
}

export async function proxyToBackend(
  request: Request,
  backendPath: string,
): Promise<Response> {
  const backend = getBackendUrl().replace(/\/$/, '')
  const incoming = new URL(request.url)
  const target = `${backend}${backendPath}${incoming.search}`

  const headers = new Headers()
  const contentType = request.headers.get('content-type')
  if (contentType) headers.set('content-type', contentType)

  const init: RequestInit = {
    method: request.method,
    headers,
    cache: 'no-store',
  }

  if (request.method !== 'GET' && request.method !== 'HEAD') {
    init.body = await request.arrayBuffer()
  }

  const res = await fetch(target, init)
  const body = await res.arrayBuffer()
  return new Response(body, {
    status: res.status,
    statusText: res.statusText,
    headers: {
      'content-type': res.headers.get('content-type') || 'application/json',
    },
  })
}
