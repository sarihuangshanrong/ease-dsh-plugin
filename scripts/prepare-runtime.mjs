#!/usr/bin/env node
/** Create a disposable DSH overlay without modifying an installed profile. */
import { createRequire } from 'node:module';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { resolve, dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { homedir } from 'node:os';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const args = process.argv.slice(2);
const options = {};
for (let i = 0; i < args.length; i += 2) {
  if (!['--modules', '--out'].includes(args[i]) || !args[i + 1]) throw new Error('Usage: prepare-runtime.mjs [--modules <profile parent>] [--out <directory>]');
  options[args[i]] = resolve(args[i + 1]);
}
const moduleRoot = options['--modules'] ?? join(process.env.DSH_HOME ?? join(homedir(), '.dsh'), 'profiles');
const out = options['--out'] ?? join(root, '.runtime');
const require = createRequire(join(moduleRoot, 'package.json'));
const llm = pathToFileURL(require.resolve('@deepseek-ai/dsh-llm')).href;
const skill = pathToFileURL(require.resolve('@deepseek-ai/dsh-skill')).href;
const filesystem = require.resolve('@deepseek-ai/dsh-skill-filesystem');
const aliases = JSON.parse(await readFile(join(root, 'skills/ease-manifest.json'), 'utf8')).commands;
const moduleUrl = pathToFileURL(join(root, 'runtime/aliases.mjs')).href;
await mkdir(out, { recursive: true });
await writeFile(join(out, 'plugin.mjs'), `import { createUserMessage } from ${JSON.stringify(llm)};
import { renderSkillContent, isUserInvocable } from ${JSON.stringify(skill)};
import { createAdapter } from ${JSON.stringify(moduleUrl)};
const plugin = createAdapter({ createUserMessage, renderSkillContent, isUserInvocable }, ${JSON.stringify(aliases)});
export const { name, inject, apply } = plugin;
`);
// JSON is valid YAML. New IDs avoid replacing user provider configuration.
const patch = [{ insert: [
  { id: 'ease-skill-filesystem', name: filesystem, config: { providerName: 'ease', includeDefaultRoots: false, customSkillDirs: [join(root, 'skills')] } },
  { id: 'ease-command-aliases', name: join(out, 'plugin.mjs') },
] }];
await writeFile(join(out, 'ease.patch.yml'), JSON.stringify(patch, null, 2) + '\n');
console.log(join(out, 'ease.patch.yml'));
