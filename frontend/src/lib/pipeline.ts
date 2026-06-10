import type { LucideIcon } from 'lucide-react'
import {
  BookOpen,
  Brain,
  FileSearch,
  GitBranch,
  Network,
  Shield,
  Skull,
  Wallet,
} from 'lucide-react'

export type PipelineTabId =
  | 'overview'
  | 'static'
  | 'dynamic'
  | 'mitre'
  | 'graph'
  | 'story'
  | 'twin'
  | 'fraud'
  | 'reverse'

export interface PipelineStep {
  id: string
  title: string
  summary: string
  icon: LucideIcon
  tab?: PipelineTabId
  phase?: string
  details: string[]
  outputs: string[]
}

export const INVESTIGATION_PIPELINE: PipelineStep[] = [
  {
    id: 'ingest',
    title: 'Ingest & fingerprint',
    summary: 'Hash, deduplicate, and queue the sample for autonomous analysis.',
    icon: Shield,
    phase: 'queued',
    details: [
      'SHA-256 fingerprinting and duplicate detection',
      'Secure storage on the analysis worker',
      'Background job scheduled across static → dynamic → AI phases',
    ],
    outputs: ['File hash', 'Upload timestamp', 'Investigation job ID'],
  },
  {
    id: 'static',
    title: 'Static analysis',
    summary: 'Extract manifest, permissions, IOCs, certificates, and code indicators.',
    icon: FileSearch,
    tab: 'static',
    phase: 'static_analysis',
    details: [
      'AndroidManifest permissions and dangerous API usage',
      'Embedded URLs, IPs, domains, and certificate metadata',
      'Obfuscation signals and suspicious string patterns',
    ],
    outputs: ['Permission list', 'Network IOCs', 'Cert chain', 'Obfuscation score'],
  },
  {
    id: 'dynamic',
    title: 'Dynamic sandbox',
    summary: 'Optional runtime telemetry when an ADB sandbox is available.',
    icon: Network,
    tab: 'dynamic',
    phase: 'dynamic_analysis',
    details: [
      'Observed network connections and DNS lookups',
      'SMS, accessibility, overlay, and banking-hook behaviors',
      'C2 beaconing and exfiltration attempts',
    ],
    outputs: ['Runtime events', 'C2 indicators', 'Behavior timeline'],
  },
  {
    id: 'risk',
    title: 'Risk scoring',
    summary: 'ML-weighted score from permissions, network, APIs, and C2 signals.',
    icon: Shield,
    tab: 'overview',
    phase: 'risk_scoring',
    details: [
      'Feature fusion from static and dynamic findings',
      'XGBoost model when available; heuristic fallback otherwise',
      'Risk level band: low → critical',
    ],
    outputs: ['Numeric risk score', 'Risk level', 'Top contributing factors'],
  },
  {
    id: 'ai',
    title: 'AI threat reasoning',
    summary: 'LLM narrative, MITRE mapping, and threat-intel correlation.',
    icon: Brain,
    tab: 'overview',
    phase: 'ai_reasoning',
    details: [
      'Analyst-style explanation of malicious intent',
      'MITRE ATT&CK mobile technique mapping',
      'Cross-reference with known families and IOC feeds',
    ],
    outputs: ['Analyst narrative', 'MITRE table', 'TI correlations'],
  },
  {
    id: 'intel',
    title: 'Advanced intelligence',
    summary: 'Threat graph, malware story, digital twin, and fraud impact.',
    icon: GitBranch,
    tab: 'graph',
    phase: 'persisting',
    details: [
      'Relationship graph linking APK, IOCs, certs, and techniques',
      'Malware story chapters (install → impact)',
      'Digital twin predictions and organizational fraud estimate',
    ],
    outputs: ['Threat graph', 'Story mode', 'Twin predictions', 'Fraud range'],
  },
  {
    id: 'mitre',
    title: 'MITRE ATT&CK',
    summary: 'Tactics and techniques observed in this sample.',
    icon: Skull,
    tab: 'mitre',
    details: [
      'Techniques derived from permissions and API abuse',
      'Aligned to mobile-relevant ATT&CK entries',
    ],
    outputs: ['Tactic / technique pairs', 'Detection records'],
  },
  {
    id: 'report',
    title: 'SOC report',
    summary: 'Exportable investigation summary for incident response.',
    icon: BookOpen,
    tab: 'overview',
    details: [
      'Executive summary and technical appendix',
      'IOCs, remediation steps, and timeline',
    ],
    outputs: ['PDF/Markdown report', 'Shareable case bundle'],
  },
]

export const PLATFORM_CAPABILITIES: PipelineStep[] = [
  ...INVESTIGATION_PIPELINE.filter((s) =>
    ['static', 'dynamic', 'ai', 'mitre', 'intel'].includes(s.id),
  ),
  {
    id: 'story',
    title: 'Malware story',
    summary: 'Narrative from install to fraud impact.',
    icon: BookOpen,
    tab: 'story',
    details: ['Chapter-based attack storyline for briefings.'],
    outputs: ['Story chapters'],
  },
  {
    id: 'twin',
    title: 'Digital twin',
    summary: 'Predicted next-stage behaviors.',
    icon: Brain,
    tab: 'twin',
    details: ['Likelihood-scored future actions based on observed TTPs.'],
    outputs: ['Behavior predictions'],
  },
  {
    id: 'fraud',
    title: 'Fraud impact',
    summary: 'Estimated financial and organizational damage.',
    icon: Wallet,
    tab: 'fraud',
    details: ['Per-device and org-level loss estimates with recommended actions.'],
    outputs: ['Loss range', 'Remediation list'],
  },
]
