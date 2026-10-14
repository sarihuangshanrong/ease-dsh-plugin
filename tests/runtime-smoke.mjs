// Uses the installed DSH packages. No model invocation or profile mutation.
import assert from 'node:assert/strict';
import { createRequire } from 'node:module';
import { readFile } from 'node:fs/promises';
import { resolve, join } from 'node:path';
import { homedir } from 'node:os';
import { pathToFileURL } from 'node:url';
import { createAdapter } from '../runtime/aliases.mjs';
const moduleRoot = process.env.EASE_DSH_MODULE_ROOT ?? join(process.env.DSH_HOME ?? join(homedir(), '.dsh'), 'profiles');
const require = createRequire(join(moduleRoot, 'package.json'));
const load = name => import(pathToFileURL(require.resolve(name)).href);
const { Context } = await load('@deepseek-ai/cordis');
const skillLib = await load('@deepseek-ai/dsh-skill');
const filesystem = await load('@deepseek-ai/dsh-skill-filesystem');
const { createUserMessage } = await load('@deepseek-ai/dsh-llm');
const root = resolve(import.meta.dirname, '..');
const aliases = JSON.parse(await readFile(join(root, 'skills/ease-manifest.json'), 'utf8')).commands;
const ctx = new Context();
const skillFiber = await ctx.plugin(skillLib.default);
const fsFiber = await ctx.plugin(filesystem, { providerName: 'ease-test', includeDefaultRoots: false, customSkillDirs: [join(root, 'skills')], watch: false });
try {
  assert.equal(skillLib.isSkillName('ease:starter'), false);
  const catalog = await ctx.skills.list({ cwd: root });
  assert.deepEqual(catalog.map(s => s.name).sort(), Object.values(aliases).sort());
  let hook;
  const controller = new AbortController();
  const agent = { session: { header: { cwd: root } } };
  // The real registry's scope needs a Context, so leave the mock agent scope
  // out of the lookup while retaining cwd/signal. Hook behavior stays intact.
  const registry = ctx.skills;
  let lookupCount = 0;
  createAdapter({ ...skillLib, createUserMessage }, aliases).apply({
    skills: { async get(name, { cwd, signal }) { lookupCount++; return registry.get(name, { cwd, signal }); } },
    on(event, fn) { hook = fn; },
  });
  async function run(text, source = { kind: 'user' }, decision) {
    const messages = [createUserMessage({ content: [{ type: 'text', text }], source })];
    return hook({ agent, messages, signal: controller.signal }, async () => decision ?? { kind: 'enter', messages });
  }
  for (const [alias, name] of Object.entries(aliases)) {
    const result = await run(`/${alias} docs/需求 文档.md --resume`);
    assert.equal(result.messages.length, 2);
    assert.equal(result.messages[0].content[0].text, `/${alias} docs/需求 文档.md --resume`);
    assert.equal(result.messages[1].source.name, name);
    assert.match(result.messages[1].content[0].text, /Base directory for this skill:/);
    assert.match(result.messages[1].content[0].text, /ease-resources/);
  }
  for (const text of ['/ease:unknown', '/ease:starter-extra', '请解释 /ease:starter', '```\n/ease:starter\n```', '/other:starter']) {
    assert.equal((await run(text)).messages.length, 1);
  }
  assert.equal((await run('/ease:starter', { kind: 'tool' })).messages.length, 1);
  const count = lookupCount;
  const rejection = { kind: 'reject', reason: 'test rejection' };
  assert.equal(await run('/ease:starter', { kind: 'user' }, rejection), rejection);
  assert.equal(count, lookupCount);
  const existing = createUserMessage({ content: [{ type: 'text', text: 'already injected' }], source: { kind: 'skill-invocation', name: 'ease-starter', form: 'instructions' } });
  assert.equal((await run('/ease:starter', { kind: 'user' }, { kind: 'enter', messages: [existing] })).messages.length, 1);
  for (const found of [undefined, { invocation: { userInvocable: false } }]) {
    createAdapter({ ...skillLib, createUserMessage }, aliases).apply({
      skills: { async get() { return found; } }, on(event, fn) { hook = fn; },
    });
    await assert.rejects(() => run('/ease:starter'), /Ease command unavailable/);
  }
  const { default: AgentRegistry, agentEvents } = await load('@deepseek-ai/dsh-agent');
  const { default: SystemPrompt } = await load('@deepseek-ai/dsh-system-prompt');
  const { default: ToolRuntime } = await load('@deepseek-ai/dsh-tools');
  const { Session, SessionId } = await load('@deepseek-ai/dsh-session');
  await ctx.plugin(SystemPrompt);
  await ctx.plugin(ToolRuntime);
  await ctx.plugin(AgentRegistry);
  const bridge = await import(pathToFileURL(join(root, '.runtime/plugin.mjs')).href);
  const adapterFiber = await ctx.plugin(bridge);
  const id = SessionId('ease-runtime-smoke');
  const realAgent = { ctx: new Context(), id, options: {}, session: Session.create(id, [], { version: 0, id, createdAt: 0, cwd: root }) };
  const message = createUserMessage({ content: [{ type: 'text', text: '/ease:starter docs/brd.md' }], source: { kind: 'user' } });
  const eventResult = await agentEvents(ctx, realAgent).waterfall('agent/pre-step',
    { messages: [message], turn: 1, step: 1, signal: controller.signal },
    async () => ({ kind: 'enter', messages: [message] }));
  assert.equal(eventResult.messages.at(-1).source.name, 'ease-starter');
  await adapterFiber.dispose();
  console.log('PASS: actual Cordis plugin registration and agent pre-step event.');
  console.log('PASS: real DSH discovery (9 skills), all colon aliases, argument preservation, source filtering, unknown aliases and reject propagation.');
} finally { await fsFiber.dispose(); await skillFiber.dispose(); }
