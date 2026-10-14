/** DSH pre-step adapter. Dependencies are supplied by the profile bridge. */
export function createAdapter({ createUserMessage, renderSkillContent, isUserInvocable }, aliases) {
  return {
    name: 'ease-command-aliases',
    inject: ['agents', 'skills'],
    apply(ctx) {
      ctx.on('agent/pre-step', async ({ agent, messages, signal }, next) => {
        const decision = await next();
        if (decision.kind === 'reject') return decision;
        const requested = new Set();
        for (const message of messages) {
          if (message.source?.kind !== 'user') continue;
          for (const block of message.content) {
            if (block.type !== 'text') continue;
            // Deliberately only leading commands, not code fences, quoted docs,
            // assistant prose, unknown ease commands, or arbitrary namespaces.
            const match = /^\s*\/(ease:[a-z0-9]+(?:-[a-z0-9]+)*)(?=\s|$)/.exec(block.text);
            if (match && Object.hasOwn(aliases, match[1])) requested.add(aliases[match[1]]);
          }
        }
        const injections = [];
        for (const name of requested) {
          signal.throwIfAborted();
          const skill = await ctx.skills.get(name, { cwd: agent.session.header.cwd, signal, scope: agent });
          signal.throwIfAborted();
          if (!skill || !isUserInvocable(skill)) {
            throw new Error(`Ease command unavailable: ${name}. Check the Ease skill provider and invocation policy.`);
          }
          if (decision.messages.some(m => m.source?.kind === 'skill-invocation' && m.source.name === name)) continue;
          injections.push(createUserMessage({
            content: [{ type: 'text', text: renderSkillContent(skill) }],
            source: { kind: 'skill-invocation', name, form: 'instructions' },
          }));
        }
        return injections.length ? { kind: 'enter', messages: [...decision.messages, ...injections] } : decision;
      });
    },
  };
}
