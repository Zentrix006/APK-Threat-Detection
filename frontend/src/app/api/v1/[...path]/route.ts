import { proxyToBackend } from '@/lib/backend-proxy'

type Ctx = { params: Promise<{ path: string[] }> }

async function handler(request: Request, ctx: Ctx) {
  const { path } = await ctx.params
  return proxyToBackend(request, `/api/v1/${path.join('/')}`)
}

export const GET = handler
export const POST = handler
export const PUT = handler
export const PATCH = handler
export const DELETE = handler
