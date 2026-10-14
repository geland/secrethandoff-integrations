import { describe, expect, test } from 'claude-code/testing'

import { altOf, appearanceOf, bandSvg, cardOf, cardSvg, hostAppearance, policyLine, resultState, resultText, statusOf, toolKind, wrap } from '../hooks/card'

const TOOL = 'mcp__plugin_secrethandoff_secrethandoff__request_secret'
const INPUT = {
  name: 'GITHUB_TOKEN',
  reason: 'List your repositories.',
  policy: { hosts: ['api.github.com'], methods: ['GET'] },
}
const SURFACES = ['terminal', 'desktop'] as const

function row(over: Partial<{ tool: string; input: unknown; isRunning: boolean; isErrored: boolean; output: unknown }> = {}) {
  return {
    component: 'ToolUse' as const,
    props: { tool_use_id: 'toolu_1', tool: TOOL, input: INPUT, isRunning: false, isErrored: false, isInterrupted: false, ...over },
  }
}

describe('helpers', () => {
  test('tool names', async () => {
    expect(toolKind(TOOL)).toBe('request_secret')
    expect(toolKind('mcp__secrethandoff__run_with_secret')).toBe('run_with_secret')
    expect(toolKind('mcp__secrethandoff__wait_for_secret')).toBe('wait_for_secret')
    expect(toolKind('mcp__other__request_secret')).toBe(undefined)
    expect(toolKind('Bash')).toBe(undefined)
  })
  test('result text from each stored form', async () => {
    expect(resultText('a')).toBe('a')
    expect(resultText([{ type: 'text', text: 'a' }])).toBe('a')
    expect(resultText({ content: [{ type: 'text', text: 'b' }] })).toBe('b')
    expect(resultText(undefined)).toBe('')
  })
  test('policy line', async () => {
    expect(policyLine(INPUT.policy)).toBe('api.github.com · GET · any path')
    expect(policyLine(undefined)).toBe('')
  })
  test('status from the binary result text', async () => {
    expect(statusOf('request_secret', false, false, false, 'GITHUB_TOKEN is ready. Sent only to x.').tone).toBe('ok')
    expect(statusOf('request_secret', false, false, false, 'The user declined to give X.').text).toMatch(/declined/)
    expect(statusOf('request_secret', false, false, false, 'Waiting for the user to fill X on the page').text).toMatch(/Still waiting/)
    expect(statusOf('request_secret', false, false, false, 'The request for X expired.').text).toMatch(/expired/)
    expect(statusOf('run_with_secret', false, false, false, 'exit code: 3\n--- stdout ---').text).toBe('The command ran. Exit code 3.')
    const remote = statusOf('request_secret', false, false, false, 'This computer has no browser. Ask the user ... pairing code ABCDE-FGHJ-KMNP:\nhttps://x')
    expect(remote.code).toBe('ABCDE-FGHJ-KMNP')
  })
  test('host appearance supports host variants and falls back when unavailable', async () => {
    expect(appearanceOf('light')).toBe('light')
    expect(appearanceOf('light-ansi')).toBe('light')
    expect(appearanceOf('dark-daltonized')).toBe('dark')
    expect(appearanceOf('system')).toBe('system')
    expect(appearanceOf(undefined)).toBe('system')
    expect(await hostAppearance(Promise.resolve([{ key: 'theme', value: 'dark' }]))).toBe('dark')
    expect(await hostAppearance(Promise.resolve([]))).toBe('system')
    expect(await hostAppearance(Promise.reject(new Error('Setting unavailable')))).toBe('system')
  })
})

test('explicit host appearance overrides the system in both SVG surfaces', async () => {
  const card = cardOf('request_secret', INPUT, { tone: 'wait', text: 'Waiting.' })
  const waiting = { kind: 'request_secret', name: INPUT.name, hosts: 'api.github.com', command: '' }
  for (const render of [(mode: 'light' | 'dark' | 'system') => cardSvg(card, mode), (mode: 'light' | 'dark' | 'system') => bandSvg(waiting, 0, mode)]) {
    expect(render('light')).toMatch(/fill:#171C27/)
    expect(render('dark')).toMatch(/fill:#EDF1FA/)
    expect(render('light').includes('prefers-color-scheme')).toBe(false)
    expect(render('dark').includes('prefers-color-scheme')).toBe(false)
    expect(render('system')).toMatch(/prefers-color-scheme: dark/)
  }
})

test('accessible card text retains content when the visual preview is shortened', async () => {
  const name = 'REPORT_'.repeat(10)
  const reason = 'Review the export permissions. '.repeat(30)
  const card = cardOf('request_secret', { ...INPUT, name, reason }, { tone: 'wait', text: 'Waiting.', code: 'ABCDE-FGHJ-KMNP' })
  expect(cardSvg(card)).toMatch(/…/)
  expect(altOf(card).includes(name)).toBe(true)
  expect(altOf(card).includes(reason)).toBe(true)
  expect(altOf(card)).toMatch(/Reason \(written by the agent\)/)
  expect(altOf(card)).toMatch(/Pairing code ABCDE-FGHJ-KMNP/)
  expect(altOf(card)).toMatch(/Enter secrets only on the Secret Handoff page/)
})

test('the pending band escapes command text and shows additional waiting requests', async () => {
  const source = bandSvg({ kind: 'run_with_secret', name: '', hosts: '', command: 'tool <report> --label "review" & check' }, 2, 'dark')
  expect(source).toMatch(/&lt;report&gt;/)
  expect(source).toMatch(/--label &quot;review&quot; &amp; check/)
  expect(source).toMatch(/2 more waiting/)
  expect(/<script|<foreignObject|on[a-z]+=/i.test(source)).toBe(false)
})

test('the terminal draws a text card', async $ => {
  const ui = await $.ui.mount({ plugin: 'secrethandoff', surface: 'terminal', ...row({ isRunning: true }) })
  expect(await ui.find({ type: 'Text', text: 'Secret Handoff' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /GITHUB_TOKEN/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /written by the agent/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: 'api.github.com · GET · any path' })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /Waiting for Secret Handoff/ })).toBeDefined()
  expect(await ui.find({ type: 'Input' })).toBeUndefined()
  await ui.unmount()
})

test('the desktop draws the card as an escaped SVG', async $ => {
  const reason = 'Create a <test> charge & check "it".'
  const ui = await $.ui.mount({ plugin: 'secrethandoff', surface: 'desktop', viewport: { columns: 100, rows: 40 }, ...row({ isRunning: true, input: { ...INPUT, reason } }) })
  const svg = await ui.find({ type: 'Svg' })
  expect(svg).toBeDefined()
  const props = (svg as unknown as { props: { source: string; alt: string } }).props
  expect(props.alt).toMatch(/GITHUB_TOKEN/)
  expect(props.alt).toMatch(/Waiting for Secret Handoff/)
  expect(props.source).toMatch(/&lt;test&gt; charge &amp; check &quot;it&quot;/)
  expect(props.source.includes('<test>')).toBe(false)
  expect(/<script|<foreignObject|on[a-z]+=/i.test(props.source)).toBe(false)
  expect(await ui.find({ type: 'Input' })).toBeUndefined()
  await ui.unmount()
})

test('mobile, editor, and narrow or unmeasured desktop keep text native and complete', async $ => {
  const name = 'REPORT_EXPORT_CONFIRMATION_CODE_FOR_THIS_WORKFLOW'
  const reason = 'Confirm the report export and check its permissions. '.repeat(8)
  for (const [surface, viewport] of [
    ['mobile', { columns: 43, rows: 90 }],
    ['vscode', { columns: 43, rows: 90 }],
    ['desktop', { columns: 43, rows: 90 }],
    ['desktop', undefined],
  ] as const) {
    const ui = await $.ui.mount({ plugin: 'secrethandoff', surface, viewport, ...row({ isRunning: true, input: { ...INPUT, name, reason } }) })
    expect(await ui.find({ type: 'Text', text: name })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: `“${reason}”  (written by the agent)` })).toBeDefined()
    expect(await ui.find({ type: 'Text', text: 'api.github.com · GET · any path' })).toBeDefined()
    const mark = await ui.find({ type: 'Svg' })
    const props = (mark as unknown as { props: { source: string; width: number; height: number } }).props
    expect(props.width).toBe(24)
    expect(props.height).toBe(24)
    expect(props.source.includes('<text')).toBe(false)
    expect(await ui.find({ type: 'Input' })).toBeUndefined()
    await ui.unmount()
  }
})

test('a ready request says the agent never sees the value', async $ => {
  const ui = await $.ui.mount({ plugin: 'secrethandoff', surface: 'terminal', ...row({ output: [{ type: 'text', text: 'GITHUB_TOKEN is ready. Sent only to api.github.com.' }] }) })
  expect(await ui.find({ type: 'Text', text: /never sees it/ })).toBeDefined()
  await ui.unmount()
})

test('wrap keeps lines short and cuts long words', async () => {
  expect(wrap('aaa bbb ccc', 7)).toEqual(['aaa bbb', 'ccc'])
  expect(wrap('x'.repeat(10), 4)).toEqual(['xxxx', 'xxxx', 'xx'])
  expect(wrap('a b c d e f g', 1, 3)).toEqual(['a', 'b', '…'])
})

test('a folded group that holds a request is unfolded', async ($, on) => {
  let seen: boolean | undefined
  on('ui.render', { component: 'ToolGroup' }, async ($, e) => {
    seen = e.props.isExpanded
    const { Text } = $.ui.resolve(e)
    return <Text key="engine">group</Text>
  })
  const call = { tool_use_id: 'toolu_1', tool: TOOL, input: INPUT, isRunning: true, isErrored: false, isInterrupted: false }
  for (const [calls, want] of [[[call], true], [[{ ...call, tool: 'Read' }], false]] as const) {
    const ui = await $.ui.mount({ plugin: 'secrethandoff', surface: 'desktop', component: 'ToolGroup', props: { calls, isActive: true, isExpanded: false } })
    expect(seen).toBe(want)
    await ui.unmount()
  }
})

test('the result block of request_secret is not drawn twice', async $ => {
  for (const surface of SURFACES) {
    const ui = await $.ui.mount({
      plugin: 'secrethandoff', surface, component: 'ToolResult',
      props: { tool_use_id: 'toolu_1', tool: TOOL, output: 'GITHUB_TOKEN is ready.', isErrored: false },
    })
    expect(await ui.find({ type: 'Text', text: /ready/ })).toBeUndefined()
    await ui.unmount()
  }
})

test('other tools keep their own rows', async ($, on) => {
  // Stands for the engine's own row beneath the plugin.
  on('ui.render', { component: 'ToolUse' }, async ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text key="engine">engine row</Text>
  })
  const ui = await $.ui.mount({ plugin: 'secrethandoff', surface: 'terminal', ...row({ tool: 'mcp__other__request_secret' }) })
  expect(await ui.find({ type: 'Text', text: 'Secret Handoff' })).toBeUndefined()
  expect(await ui.find({ type: 'Text', text: 'engine row' })).toBeDefined()
  await ui.unmount()
})

test('the band above the prompt shows a waiting request until it ends', async ($, on) => {
  let release: () => void = () => {}
  // Stands for the engine running the MCP call: it waits until released.
  on('tool.call', async () => {
    await new Promise<void>(r => (release = r))
    return { result: [{ type: 'text', text: 'GITHUB_TOKEN is ready.' }] } as never
  })
  on('ui.render', { component: 'AbovePrompt' }, async ($, e) => {
    const { Text } = $.ui.resolve(e)
    return <Text key="engine">empty band</Text>
  })
  const band = { component: 'AbovePrompt' as const, props: { hasSurvey: false, isWorking: true, maxRows: 6, bodyColumns: 100 } as never }

  const call = $.tool.call({ tool: TOOL, tool_use_id: 'toolu_9', ...INPUT } as never)
  await new Promise(r => setTimeout(r, 10))
  let ui = await $.ui.mount({ plugin: 'secrethandoff', surface: 'terminal', ...band })
  expect(await ui.find({ type: 'Text', text: /Enter GITHUB_TOKEN on the Secret Handoff page/ })).toBeDefined()
  expect(await ui.find({ type: 'Text', text: /api\.github\.com/ })).toBeDefined()
  await ui.unmount()
  const desktopUi = await $.ui.mount({ plugin: 'secrethandoff', surface: 'desktop', ...band })
  expect(await desktopUi.find({ type: 'Svg' })).toBeDefined()
  await desktopUi.unmount()
  const narrowUi = await $.ui.mount({ plugin: 'secrethandoff', surface: 'desktop', ...band, props: { hasSurvey: false, isWorking: true, maxRows: 6, bodyColumns: 43 } as never })
  expect(await narrowUi.find({ type: 'Text', text: /Enter GITHUB_TOKEN on the Secret Handoff page/ })).toBeDefined()
  const narrowMark = await narrowUi.find({ type: 'Svg' })
  expect((narrowMark as unknown as { props: { width: number } }).props.width).toBe(24)
  await narrowUi.unmount()

  release()
  await call
  ui = await $.ui.mount({ plugin: 'secrethandoff', surface: 'terminal', ...band })
  expect(await ui.find({ type: 'Text', text: 'empty band' })).toBeDefined()
  await ui.unmount()
})
