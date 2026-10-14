// Claude Code mod: draws Secret Handoff tool calls in the transcript as a
// branded card. The card only shows what the tool call already holds (the
// agent's reason, the policy, the result text). It has no Input element: the
// secret is typed only on the local page, never in the chat (threat model
// T-48, docs/plans/claude-code-mod-check.md in the Secret Handoff repository).
import type { Register } from 'claude-code'

// The same Clear Passage geometry and color roles as the public site. SVGs
// are isolated images, so the host's selected appearance is passed explicitly.
const HANDOFF_MARK = 'M8 8h12v16h14l-8 12h-6v20H8V8Zm36 0h12v48H44V40H30l8-12h6V8Z'
const SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,sans-serif"
const COLORS = {
  light: { surface: '#FFFFFF', ink: '#171C27', muted: '#566174', line: '#D9DFE8', accent: '#3154E8', mark: '#3154E8', soft: '#EEF1FF', success: '#246B50', error: '#B42332' },
  dark: { surface: '#171E2C', ink: '#EDF1FA', muted: '#AFBBD0', line: '#303C51', accent: '#9DADFF', mark: '#6680FF', soft: '#202F50', success: '#A2D9BA', error: '#FFADB8' },
}

export type Appearance = 'light' | 'dark' | 'system'

export function appearanceOf(value: unknown): Appearance {
  if (typeof value === 'string' && /^light(?:-|$)/.test(value)) return 'light'
  if (typeof value === 'string' && /^dark(?:-|$)/.test(value)) return 'dark'
  return 'system'
}

export async function hostAppearance(settings: Promise<{ key: string; value: unknown }[]>): Promise<Appearance> {
  try {
    return appearanceOf((await settings).find(row => row.key === 'theme')?.value)
  } catch {
    // Older hosts may not expose a setting. The SVG can still follow the
    // system; terminal colors then use the user's ANSI palette.
    return 'system'
  }
}

function appearanceCss(appearance: Appearance): string {
  const rules = (scheme: 'light' | 'dark') => {
    const c = COLORS[scheme]
    return `.bg{fill:${c.surface};stroke:${c.line}}.brand,.title,.value,.reason,.mono,.code,.band-text{fill:${c.ink}}.label,.hint,.foot,.stop{fill:${c.muted}}.rule{stroke:${c.line}}.logo{fill:${c.mark}}.wait{fill:${c.accent}}.ok{fill:${c.success}}.error{fill:${c.error}}.band-bg{fill:${c.soft};stroke:${c.line}}`
  }
  return appearance === 'system' ? `${rules('light')}@media (prefers-color-scheme: dark){${rules('dark')}}` : rules(appearance)
}

function terminalColors(appearance: Appearance) {
  return appearance === 'system' ? { accent: 'blue', success: 'green', error: 'red' } : COLORS[appearance]
}

function markSvg(appearance: Appearance): string {
  return `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 64 64"><style>${appearanceCss(appearance)}</style><path d="${HANDOFF_MARK}" class="logo"/></svg>`
}

// Plugin tools are named mcp__plugin_<plugin>_<server>__<tool>; a server
// added by hand is mcp__<server>__<tool>.
const TOOL = /^mcp__(?:plugin_secrethandoff_)?secrethandoff__(request_secret|wait_for_secret|run_with_secret|confirm_secret)$/

export type Tone = 'wait' | 'ok' | 'stop' | 'error'
export type Status = { tone: Tone; text: string; code?: string }

export function toolKind(tool: string): string | undefined {
  return TOOL.exec(tool)?.[1]
}

// The text of a tool result, whatever form the surface stores it in: a
// string, MCP content blocks, or an object that holds them.
export function resultText(output: unknown): string {
  if (typeof output === 'string') return output
  const blocks = Array.isArray(output)
    ? output
    : output && typeof output === 'object' && Array.isArray((output as { content?: unknown }).content)
      ? (output as { content: unknown[] }).content
      : undefined
  if (blocks) {
    return blocks
      .map(b => (b && typeof b === 'object' && typeof (b as { text?: unknown }).text === 'string' ? (b as { text: string }).text : ''))
      .join('\n')
  }
  return ''
}

// Hosts that preserve structuredContent need no prose parsing. Older hosts
// still use the compatibility text below.
export function resultState(output: unknown): unknown {
  return output && typeof output === 'object' ? (output as { structuredContent?: unknown }).structuredContent : undefined
}

function firstSentence(text: string): string {
  const m = /^.*?[.!?](?=\s|$)/s.exec(text.trim())
  return (m ? m[0] : text.trim()).slice(0, 300)
}

// The card's status line, from the row's state and the binary's result text.
export function statusOf(kind: string, isRunning: boolean, isErrored: boolean, isInterrupted: boolean, text: string, data?: unknown): Status {
  if (isInterrupted) return { tone: 'stop', text: 'Interrupted.' }
  if (isRunning) {
    return kind === 'run_with_secret'
      ? { tone: 'wait', text: 'Waiting for your command approval.' }
      : { tone: 'wait', text: 'Waiting for Secret Handoff.' }
  }
  const state = data && typeof data === 'object' ? data as Record<string, unknown> : undefined
  if (kind === 'run_with_secret') {
    switch (state?.status) {
      case 'command_finished':
        if (state.executed === true && Number.isInteger(state.exit_code)) {
          const exit = `Exit code ${state.exit_code}.`
          if (state.timed_out) return { tone: 'error', text: `The command timed out and was stopped. ${exit}` }
          if (state.cancelled) return { tone: 'stop', text: `The command was cancelled and stopped. ${exit}` }
          return { tone: state.exit_code === 0 ? 'ok' : 'error', text: `The command ran. ${exit}` }
        }
        break
      case 'command_pending': return { tone: 'wait', text: 'Waiting for you to approve the command on the page in your browser.' }
      case 'command_denied': return { tone: 'stop', text: 'You denied the command. It did not run.' }
      case 'command_expired': return { tone: 'stop', text: 'Approval expired. The command did not run.' }
      case 'command_cancelled': return { tone: 'stop', text: 'The call was cancelled. The command did not run.' }
      case 'command_not_started': return { tone: 'error', text: firstSentence(typeof state.message === 'string' ? state.message : text) || 'The command could not start.' }
    }
  }
  if (isErrored) return { tone: 'error', text: firstSentence(text || (typeof state?.message === 'string' ? state.message : '')) || 'The call failed.' }
  const pairing = /pairing code ([0-9A-Z]{5}-[0-9A-Z]{4}-[0-9A-Z]{4})/.exec(text)?.[1]
  switch (state?.status) {
    case 'ready': return { tone: 'ok', text: 'Ready. The agent uses the secret by name and never sees it.' }
    case 'pending': return state.presentation === 'browser_page'
      ? { tone: 'wait', text: 'Still waiting for you on the Secret Handoff page in your browser.' }
      : state.presentation === 'client_prompt' || state.presentation === 'remote_link'
        ? { tone: 'wait', text: 'Waiting for you on the Secret Handoff page on your other device.', code: pairing }
        : { tone: 'wait', text: 'Waiting for Secret Handoff.' }
    case 'confirmation_required': return { tone: 'wait', text: 'Filled. Read the confirmation code on your page to the agent.' }
    case 'declined': return { tone: 'stop', text: 'You declined. The agent did not get a secret.' }
    case 'cancelled': return { tone: 'stop', text: 'Cancelled. Any value was discarded.' }
    case 'expired': return { tone: 'stop', text: 'The request expired.' }
    case 'forgotten': return { tone: 'stop', text: 'The secret was forgotten. Any open request was cancelled.' }
    case 'missing': return { tone: 'stop', text: 'No request or secret exists with this name.' }
    case 'error': return { tone: 'error', text: firstSentence(text) || 'The call failed.' }
  }
  if (/ is ready\./.test(text)) return { tone: 'ok', text: 'Ready. The agent uses the secret by name and never sees it.' }
  if (/confirmation code/.test(text)) return { tone: 'wait', text: 'Filled. Read the confirmation code on your page to the agent.' }
  if (/has no browser/.test(text) || /agent client is showing a page/.test(text)) {
    return { tone: 'wait', text: 'Open the link on your phone or another computer. Continue only if it shows this pairing code.', code: pairing }
  }
  if (/^Waiting for the user.*other device/.test(text)) return { tone: 'wait', text: 'Still waiting for you on the Secret Handoff page on your other device.' }
  if (/^Waiting for the user to approve/.test(text)) return { tone: 'wait', text: 'Waiting for you to approve the command on the page in your browser.' }
  if (/^Waiting for the user/.test(text)) return { tone: 'wait', text: 'Still waiting for you on the page in your browser.' }
  if (/declined|did not approve/.test(text)) return { tone: 'stop', text: kind === 'run_with_secret' ? 'You denied the command. It did not run.' : 'You declined. The agent did not get a secret.' }
  if (/cancelled/.test(text)) return { tone: 'stop', text: 'Cancelled. Any value was discarded.' }
  if (/expired/.test(text)) return { tone: 'stop', text: 'The request expired.' }
  if (/did not finish within/.test(text)) return { tone: 'error', text: firstSentence(text) }
  const exit = /^exit code: (-?\d+)/m.exec(text)?.[1]
  if (exit !== undefined) return exit === '0' ? { tone: 'ok', text: 'The command ran. Exit code 0.' } : { tone: 'error', text: `The command ran. Exit code ${exit}.` }
  return { tone: 'ok', text: firstSentence(text) }
}

type Policy = { hosts?: unknown; methods?: unknown; paths?: unknown }

function list(v: unknown): string[] {
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : []
}

export function policyLine(p: unknown): string {
  if (!p || typeof p !== 'object') return ''
  const { hosts, methods, paths } = p as Policy
  const h = list(hosts)
  if (h.length === 0) return ''
  const m = list(methods)
  const ps = list(paths)
  return [h.join(', '), m.length ? m.join(', ') : 'any method', ps.length ? ps.join(', ') : 'any path'].join(' · ')
}

function str(v: unknown): string {
  return typeof v === 'string' ? v : ''
}

const toneColor = (t: Tone, appearance: Appearance) => {
  const c = terminalColors(appearance)
  return t === 'ok' ? c.success : t === 'wait' ? c.accent : t === 'stop' ? undefined : c.error
}
const toneMark = (t: Tone) => (t === 'ok' ? '✓' : t === 'wait' ? '●' : t === 'stop' ? '–' : '!')

export type Card = {
  title: string
  rows: { label: string; value: string; style?: 'reason' | 'mono' }[]
  status: Status
}

// What a card says, from the tool call alone. The same for every surface.
export function cardOf(kind: string, input: Record<string, unknown>, status: Status): Card {
  if (kind === 'run_with_secret') {
    return {
      title: 'Command with secrets',
      rows: [
        { label: 'Command', value: list(input.command).join(' '), style: 'mono' },
        { label: 'Folder', value: str(input.dir), style: 'mono' },
        { label: 'Secrets', value: list(input.secrets).join(', '), style: 'mono' },
      ],
      status,
    }
  }
  if (kind === 'wait_for_secret') return { title: `Wait for ${str(input.name)}`, rows: [], status }
  if (kind === 'confirm_secret') return { title: `Confirm ${str(input.name)}`, rows: [], status }
  return {
    title: str(input.name) || 'Secret request',
    rows: [
      { label: 'Reason', value: str(input.reason) ? `“${str(input.reason)}”` : '(no reason given)', style: 'reason' },
      { label: 'Can go to', value: policyLine(input.policy) },
    ],
    status,
  }
}

function esc(s: string): string {
  return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;').replace(/'/g, '&#39;')
}

// wrap breaks text into lines of at most max characters, at spaces where it
// can and inside a long word where it must.
export function wrap(text: string, max: number, maxLines = 6): string[] {
  const lines: string[] = []
  let line = ''
  for (const word of text.split(/\s+/).filter(Boolean)) {
    let w = word
    while (w.length > max) {
      if (line) { lines.push(line); line = '' }
      lines.push(w.slice(0, max))
      w = w.slice(max)
    }
    if (!line) line = w
    else if (line.length + 1 + w.length <= max) line += ' ' + w
    else { lines.push(line); line = w }
  }
  if (line) lines.push(line)
  if (lines.length > maxLines) {
    const kept = lines.slice(0, maxLines)
    kept[maxLines - 1] = kept[maxLines - 1]!.slice(0, max - 1) + '…'
    return kept
  }
  return lines
}

const W = 560

// cardSvg draws the card as one SVG document, for the surfaces that draw
// SVG as an isolated image (measured, wide desktop only). Every text from the
// tool call is escaped. The host appearance wins; system is the fallback.
export function cardSvg(card: Card, appearance: Appearance = 'system'): string {
  const parts: string[] = []
  let y = 70
  const title = card.title.length > 44 ? card.title.slice(0, 43) + '…' : card.title
  parts.push(`<text x="20" y="${y}" class="title">${esc(title)}</text>`)
  y += 16
  for (const row of card.rows) {
    if (!row.value) continue
    const lines = wrap(row.value, row.style === 'mono' ? 56 : 62)
    y += 20
    parts.push(`<text x="20" y="${y}" class="label">${esc(row.label)}</text>`)
    lines.forEach((l, i) => parts.push(`<text x="112" y="${y + i * 19}" class="${row.style ?? 'value'}">${esc(l)}</text>`))
    if (row.style === 'reason') parts.push(`<text x="112" y="${y + lines.length * 19}" class="hint">Written by the agent</text>`)
    y += (lines.length - 1) * 19 + (row.style === 'reason' ? 19 : 0)
  }
  y += 18
  parts.push(`<line x1="20" x2="${W - 20}" y1="${y}" y2="${y}" class="rule"/>`)
  y += 24
  const tone = card.status.tone
  const statusLines = wrap(card.status.text, 76, 3)
  parts.push(`<text x="20" y="${y}" class="mark ${tone}">${toneMark(tone)}</text>`)
  statusLines.forEach((l, i) => parts.push(`<text x="40" y="${y + i * 19}" class="status ${tone}">${esc(l)}</text>`))
  y += (statusLines.length - 1) * 19
  if (card.status.code) {
    y += 30
    parts.push(`<text x="40" y="${y}" class="code">${esc(card.status.code)}</text>`)
  }
  if (tone === 'wait') {
    y += 26
    parts.push(`<text x="20" y="${y}" class="foot">Enter secrets only on the Secret Handoff page.</text>`)
  }
  const h = y + 18
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${W}" height="${h}" viewBox="0 0 ${W} ${h}" role="img">
<style>
.brand{font:600 14px ${SANS};letter-spacing:-.2px}.title{font:600 19px ${SANS};letter-spacing:-.3px}
.label{font:500 11.5px ${SANS}}.value,.reason,.status{font:13.5px ${SANS}}
.hint,.foot{font:11.5px ${SANS}}.mono{font:12.5px ui-monospace,SFMono-Regular,Menlo,monospace}
.mark{font:700 14px ${SANS}}.code{font:700 19px ui-monospace,SFMono-Regular,Menlo,monospace;letter-spacing:1.5px}
${appearanceCss(appearance)}
</style>
<rect x="0.5" y="0.5" width="${W - 1}" height="${h - 1}" rx="10" class="bg"/>
<path transform="translate(16 15) scale(.4375)" d="${HANDOFF_MARK}" class="logo"/>
<text x="52" y="34" class="brand">Secret Handoff</text>
${parts.join('\n')}
</svg>`
}

export function altOf(card: Card): string {
  return [`Secret Handoff: ${card.title}.`, ...card.rows.filter(r => r.value).map(r => `${r.label}${r.style === 'reason' ? ' (written by the agent)' : ''}: ${r.value}.`), card.status.text, card.status.code ? `Pairing code ${card.status.code}.` : '', card.status.tone === 'wait' ? 'Enter secrets only on the Secret Handoff page.' : '']
    .filter(Boolean)
    .join(' ')
}

// A call that waits for the human, keyed by tool_use_id. Module state: the
// band only needs it while the call runs, and a reload ends the call's wait.
type Waiting = { kind: string; name: string; hosts: string; command: string }
const waiting = new Map<string, Waiting>()
let nextKey = 0

export function bandText(w: Waiting): string {
  if (w.kind === 'run_with_secret') return `Waiting for approval outside this status card: ${w.command}`
  return `Enter ${w.name || 'the secret'} on the Secret Handoff page.${w.hosts ? ` It can go only to ${w.hosts}.` : ''}`
}

const BW = 560
export function bandSvg(w: Waiting, more: number, appearance: Appearance = 'system'): string {
  const lines = wrap(bandText(w), 80, 2)
  const h = 44 + lines.length * 18 + (more ? 16 : 0)
  const text = lines.map((l, i) => `<text x="46" y="${45 + i * 18}" class="band-text">${esc(l)}</text>`).join('')
  const extra = more ? `<text x="46" y="${45 + lines.length * 18 + 2}" class="foot">${more} more waiting</text>` : ''
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${BW}" height="${h}" viewBox="0 0 ${BW} ${h}" role="img">
<style>.brand{font:600 13px ${SANS}}.band-text{font:13px ${SANS}}.foot{font:11.5px ${SANS}}
${appearanceCss(appearance)}
</style>
<rect x="0.5" y="0.5" width="${BW - 1}" height="${h - 1}" rx="8" class="band-bg"/>
<path transform="translate(12 7) scale(.375)" d="${HANDOFF_MARK}" class="logo"/>
<text x="46" y="24" class="brand">Secret Handoff · waiting for you</text>${text}${extra}
</svg>`
}

export const register: Register = on => {
  on('config.set', { key: 'theme' }, async ($, e, next) => {
    const result = await next(e)
    if (!result.deny) $.ui.invalidate('ui.render')
    return result
  })

  // Note each call that waits for the human, so the band above the prompt
  // can show it while the transcript row may be folded away.
  on('tool.call', async ($, e, next) => {
    const kind = toolKind(e.tool)
    if (kind !== 'request_secret' && kind !== 'wait_for_secret' && kind !== 'run_with_secret') return next(e)
    const args = e as unknown as Record<string, unknown>
    const key = e.tool_use_id ?? `call-${nextKey++}`
    waiting.set(key, {
      kind,
      name: str(args.name),
      hosts: list((args.policy as Policy | undefined)?.hosts).join(', '),
      command: list(args.command).join(' '),
    })
    $.ui.invalidate('ui.render')
    try {
      return await next(e)
    } finally {
      waiting.delete(key)
      $.ui.invalidate('ui.render')
    }
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const first = waiting.values().next().value as Waiting | undefined
    if (e.props.hasSurvey || !first) return next(e)
    const more = waiting.size - 1
    const appearance = await hostAppearance($.config.list())
    // The API reports cells, not CSS slot pixels. Native text is the safe
    // fallback for a narrow band; a whole SVG would shrink its text to fit.
    if (e.surface === 'desktop' && e.props.bodyColumns >= 80) {
      const { Svg } = $.ui.resolve(e)
      return <Svg key="band" source={bandSvg(first, more, appearance)} alt={`Secret Handoff is waiting for you. ${bandText(first)}${more ? ` ${more} more waiting.` : ''}`} />
    }
    const { Box, Text } = $.ui.resolve(e)
    let logo = <Text color={terminalColors(appearance).accent} bold>H</Text>
    if (e.surface === 'desktop') {
      const { Svg } = $.ui.resolve(e)
      logo = <Svg key="mark" source={markSvg(appearance)} width={24} height={24} alt="" />
    }
    return (
      <Box key="band" flexDirection="column">
        <Box key="head" gap={1} alignItems="center">{logo}<Text bold>Secret Handoff</Text></Box>
        <Text wrap="wrap">{bandText(first)}{more ? ` (${more} more waiting)` : ''}</Text>
      </Box>
    )
  })

  on('ui.render', { component: 'ToolUse' }, async ($, e, next) => {
    const kind = toolKind(e.props.tool)
    if (!kind) return next(e)
    const input = (e.props.input ?? {}) as Record<string, unknown>
    const status = statusOf(kind, e.props.isRunning, e.props.isErrored, e.props.isInterrupted, resultText(e.props.output), resultState(e.props.output))
    const card = cardOf(kind, input, status)
    const appearance = await hostAppearance($.config.list())

    // A remote surface may report its width in monospace cells, but not the
    // pixel size of this row. Keep the fixed SVG to generous desktop slots.
    // Native Box/Text wraps at the host's font size on mobile, editor, narrow
    // desktop, and desktop hosts that have not measured their viewport.
    if (e.surface === 'desktop' && (e.viewport?.columns ?? 0) >= 80) {
      const { Svg } = $.ui.resolve(e)
      return <Svg key="card" source={cardSvg(card, appearance)} alt={altOf(card)} />
    }

    const { Box, Text } = $.ui.resolve(e)
    let logo = <Text color={terminalColors(appearance).accent} bold>H</Text>
    if (e.surface !== 'terminal') {
      const { Svg } = $.ui.resolve(e)
      logo = <Svg key="mark" source={markSvg(appearance)} width={24} height={24} alt="" />
    }
    const stacked = e.surface !== 'terminal' || (e.viewport?.columns ?? 80) < 64
    return (
      <Box key="card" flexDirection="column" borderStyle="round" borderColor={terminalColors(appearance).accent} paddingX={1}>
        <Box key="head" gap={1} alignItems="center">
          {logo}
          <Text bold>Secret Handoff</Text>
          {!stacked ? <Text dimColor wrap="wrap">· {card.title}</Text> : null}
        </Box>
        {stacked ? <Text bold wrap="wrap">{card.title}</Text> : null}
        {card.rows
          .filter(r => r.value)
          .map(r => (
            <Box key={r.label} flexDirection={stacked ? 'column' : 'row'} gap={stacked ? 0 : 1}>
              <Text dimColor>{stacked ? r.label : r.label.padEnd(9)}</Text>
              <Text wrap="wrap">{r.style === 'reason' ? `${r.value}  (written by the agent)` : r.value}</Text>
            </Box>
          ))}
        <Box key="status" gap={1}>
          <Text color={toneColor(status.tone, appearance)} bold>{toneMark(status.tone)}</Text>
          <Text color={toneColor(status.tone, appearance)} dimColor={status.tone === 'stop'} wrap="wrap">{status.text}</Text>
        </Box>
        {status.code ? (
          <Box key="pairing" gap={1}>
            <Text dimColor>{'Pairing'.padEnd(9)}</Text>
            <Text bold>{status.code}</Text>
          </Box>
        ) : null}
      </Box>
    )
  })

  // A run of calls can be folded into one count line, which draws no
  // ToolUse row and so no card. Unfold a group that holds a request.
  on('ui.render', { component: 'ToolGroup' }, async ($, e, next) => {
    if (e.props.isExpanded || !e.props.calls.some(c => toolKind(c.tool))) return next(e)
    return next({ ...e, props: { ...e.props, isExpanded: true } })
  })

  // The card already says what request_secret's result says, so its plain
  // result block is not drawn again. Command output (run_with_secret) stays.
  on('ui.render', { component: 'ToolResult' }, async ($, e, next) => {
    const kind = toolKind(e.props.tool)
    if (kind !== 'request_secret' && kind !== 'wait_for_secret' && kind !== 'confirm_secret') return next(e)
    if (e.props.isErrored) return next(e)
    const { Box } = $.ui.resolve(e)
    return <Box key="none" />
  })
}
