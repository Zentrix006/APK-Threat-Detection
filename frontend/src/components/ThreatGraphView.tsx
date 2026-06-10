'use client'

import { useCallback, useMemo, useState } from 'react'
import { Maximize2, Minimize2, X } from 'lucide-react'
import { useLanguage } from '@/contexts/LanguageContext'

interface GraphNode {
  id: string
  type: string
  label: string
  data?: Record<string, unknown>
}

interface GraphEdge {
  source: string
  target: string
  type?: string
}

interface ThreatGraphViewProps {
  nodes: GraphNode[]
  edges: GraphEdge[]
}

const TYPE_COLORS: Record<string, string> = {
  apk: '#0ea5e9',
  permission: '#f59e0b',
  url: '#8b5cf6',
  ip: '#ef4444',
  certificate: '#10b981',
  technique: '#e11d48',
  malware_family: '#1e293b',
}

const TYPE_LABELS: Record<string, string> = {
  apk: 'APK',
  permission: 'Permission',
  url: 'URL',
  ip: 'IP',
  certificate: 'Certificate',
  technique: 'MITRE technique',
  malware_family: 'Malware family',
}

interface LayoutNode extends GraphNode {
  x: number
  y: number
  r: number
  labelX: number
  labelY: number
  textAnchor: 'start' | 'middle' | 'end'
}

function computeLayout(nodes: GraphNode[]): {
  layoutNodes: LayoutNode[]
  width: number
  height: number
} {
  if (!nodes.length) {
    return { layoutNodes: [], width: 640, height: 420 }
  }

  const apkNode = nodes.find((n) => n.type === 'apk') || nodes[0]
  const satellites = nodes.filter((n) => n.id !== apkNode.id)
  const count = Math.max(satellites.length, 1)

  const width = Math.min(960, Math.max(560, 320 + count * 36))
  const height = Math.min(720, Math.max(380, 240 + count * 22))
  const cx = width / 2
  const cy = height / 2
  const radius = Math.min(width, height) * (0.28 + Math.min(count, 24) * 0.008)
  const labelRadius = radius + 56

  const layoutNodes: LayoutNode[] = []

  layoutNodes.push({
    ...apkNode,
    x: cx,
    y: cy,
    r: 32,
    labelX: cx,
    labelY: cy + 48,
    textAnchor: 'middle',
  })

  satellites.forEach((node, i) => {
    const angle = (2 * Math.PI * i) / satellites.length - Math.PI / 2
    const x = cx + radius * Math.cos(angle)
    const y = cy + radius * Math.sin(angle)
    const lx = cx + labelRadius * Math.cos(angle)
    const ly = cy + labelRadius * Math.sin(angle)
    const cos = Math.cos(angle)
    const textAnchor: 'start' | 'middle' | 'end' =
      cos > 0.25 ? 'start' : cos < -0.25 ? 'end' : 'middle'

    layoutNodes.push({
      ...node,
      x,
      y,
      r: node.type === 'technique' ? 20 : 16,
      labelX: lx,
      labelY: ly,
      textAnchor,
    })
  })

  return { layoutNodes, width, height }
}

function shortLabel(label: string, max = 18): string {
  const clean = label.replace(/\s+/g, ' ').trim()
  if (clean.length <= max) return clean
  return `${clean.slice(0, max - 1)}…`
}

export default function ThreatGraphView({ nodes, edges }: ThreatGraphViewProps) {
  const { t } = useLanguage()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [hoverId, setHoverId] = useState<string | null>(null)
  const [expanded, setExpanded] = useState(false)

  const { layoutNodes, width, height } = useMemo(() => computeLayout(nodes), [nodes])

  const posMap = useMemo(() => {
    const m: Record<string, LayoutNode> = {}
    layoutNodes.forEach((n) => {
      m[n.id] = n
    })
    return m
  }, [layoutNodes])

  const selected = selectedId ? posMap[selectedId] : null
  const showLabelFor = useCallback(
    (id: string) => id === selectedId || id === hoverId || posMap[id]?.type === 'apk',
    [selectedId, hoverId, posMap],
  )

  const connectedIds = useMemo(() => {
    if (!selectedId) return new Set<string>()
    const set = new Set<string>([selectedId])
    edges.forEach((e) => {
      if (e.source === selectedId) set.add(e.target)
      if (e.target === selectedId) set.add(e.source)
    })
    return set
  }, [selectedId, edges])

  if (!nodes?.length) {
    return (
      <p className="text-sm text-slate-500 py-12 text-center">{t('graph.empty')}</p>
    )
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <p className="text-xs text-slate-500">{t('graph.hint')}</p>
        <button
          type="button"
          onClick={() => setExpanded((e) => !e)}
          className="inline-flex items-center gap-1.5 text-xs font-medium text-indigo-700 hover:text-indigo-900"
        >
          {expanded ? <Minimize2 size={14} /> : <Maximize2 size={14} />}
          {expanded ? t('graph.compact') : t('graph.expand')}
        </button>
      </div>

      <div
        className={`overflow-hidden rounded-xl border border-slate-200/80 bg-gradient-to-br from-slate-900 via-slate-900 to-indigo-950 shadow-inner ${
          expanded ? 'min-h-[520px]' : 'min-h-[360px]'
        }`}
      >
        <svg
          viewBox={`0 0 ${width} ${height}`}
          className="w-full h-auto"
          style={{ minHeight: expanded ? 480 : 340 }}
          role="img"
          aria-label="Threat relationship graph"
        >
          <defs>
            <radialGradient id="graphGlow" cx="50%" cy="50%" r="50%">
              <stop offset="0%" stopColor="#6366f1" stopOpacity="0.15" />
              <stop offset="100%" stopColor="#0f172a" stopOpacity="0" />
            </radialGradient>
          </defs>
          <rect width={width} height={height} fill="url(#graphGlow)" />

          {edges.map((e, i) => {
            const s = posMap[e.source]
            const t = posMap[e.target]
            if (!s || !t) return null
            const dimmed =
              selectedId && !connectedIds.has(e.source) && !connectedIds.has(e.target)
            return (
              <line
                key={`${e.source}-${e.target}-${i}`}
                x1={s.x}
                y1={s.y}
                x2={t.x}
                y2={t.y}
                stroke={dimmed ? '#334155' : '#64748b'}
                strokeWidth={dimmed ? 0.8 : 1.2}
                strokeOpacity={dimmed ? 0.25 : 0.55}
              />
            )
          })}

          {layoutNodes.map((node) => {
            const fill = TYPE_COLORS[node.type] || '#94a3b8'
            const isSelected = selectedId === node.id
            const isHover = hoverId === node.id
            const dimmed = selectedId && !connectedIds.has(node.id)
            const showLabel = showLabelFor(node.id)

            return (
              <g
                key={node.id}
                style={{ cursor: 'pointer', opacity: dimmed ? 0.35 : 1 }}
                onMouseEnter={() => setHoverId(node.id)}
                onMouseLeave={() => setHoverId(null)}
                onClick={() => setSelectedId((id) => (id === node.id ? null : node.id))}
              >
                {(isSelected || isHover) && (
                  <circle
                    cx={node.x}
                    cy={node.y}
                    r={node.r + 8}
                    fill="none"
                    stroke={fill}
                    strokeWidth={2}
                    strokeOpacity={0.5}
                  />
                )}
                <circle
                  cx={node.x}
                  cy={node.y}
                  r={node.r}
                  fill={fill}
                  stroke={isSelected ? '#fff' : 'transparent'}
                  strokeWidth={2}
                />
                {node.type === 'apk' && (
                  <text
                    x={node.x}
                    y={node.y + 4}
                    textAnchor="middle"
                    fill="#fff"
                    fontSize={9}
                    fontWeight={700}
                  >
                    APK
                  </text>
                )}
                {showLabel && (
                  <text
                    x={node.labelX}
                    y={node.labelY}
                    textAnchor={node.textAnchor}
                    fill="#e2e8f0"
                    fontSize={10}
                    fontWeight={isSelected ? 600 : 400}
                    style={{ pointerEvents: 'none' }}
                  >
                    {shortLabel(node.label, isSelected ? 42 : 22)}
                  </text>
                )}
              </g>
            )
          })}
        </svg>
      </div>

      <div className="flex flex-wrap gap-2 justify-center">
        {Object.entries(TYPE_COLORS).map(([type, color]) => (
          <span
            key={type}
            className="inline-flex items-center gap-1.5 rounded-full bg-white border border-slate-200 px-2.5 py-1 text-[10px] font-medium text-slate-600"
          >
            <span className="w-2 h-2 rounded-full" style={{ background: color }} />
            {TYPE_LABELS[type] || type}
          </span>
        ))}
      </div>

      {selected && (
        <div className="rounded-xl border border-indigo-200 bg-gradient-to-r from-indigo-50 to-white p-4 shadow-sm">
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="text-[10px] font-bold uppercase tracking-wider text-indigo-600">
                {TYPE_LABELS[selected.type] || selected.type}
              </p>
              <p className="font-semibold text-slate-900 mt-1 break-all">{selected.label}</p>
              <p className="text-xs font-mono text-slate-500 mt-1">{selected.id}</p>
            </div>
            <button
              type="button"
              onClick={() => setSelectedId(null)}
              className="p-1 rounded-md hover:bg-slate-100 text-slate-500"
              aria-label="Close details"
            >
              <X size={16} />
            </button>
          </div>
          {selected.data && Object.keys(selected.data).length > 0 && (
            <dl className="mt-3 grid grid-cols-1 sm:grid-cols-2 gap-2 text-sm">
              {Object.entries(selected.data).map(([k, v]) => (
                <div key={k} className="bg-white/80 rounded-lg px-3 py-2 border border-slate-100">
                  <dt className="text-[10px] uppercase text-slate-500 font-semibold">{k}</dt>
                  <dd className="text-slate-800 font-mono text-xs mt-0.5 break-all">
                    {String(v ?? '—')}
                  </dd>
                </div>
              ))}
            </dl>
          )}
          <p className="text-xs text-slate-500 mt-3">
            {t('graph.relationships', {
              count: edges.filter((e) => e.source === selected.id || e.target === selected.id).length,
            })}
          </p>
        </div>
      )}
    </div>
  )
}
