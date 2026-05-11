import { promises as fs } from 'node:fs';
import path from 'node:path';

const root = process.cwd();
const srcDir = path.join(root, 'src');
const allowedColorFiles = [
  `${path.sep}theme${path.sep}`,
  `${path.sep}context${path.sep}ThemeContext`,
  `${path.sep}index.css`,
  `${path.sep}App.css`,
];
const ignoredFragments = [
  `${path.sep}i18n${path.sep}`,
  `${path.sep}locales${path.sep}`,
  `${path.sep}pages${path.sep}debug${path.sep}`,
  '.test.',
  '.spec.',
  `${path.sep}e2e${path.sep}`,
  `${path.sep}scripts${path.sep}`,
  'reportWebVitals',
  'react-app-env.d.ts',
];
const filePattern = /\.(tsx|ts|jsx|js|css)$/;
const colorPattern = /#(?:[0-9a-fA-F]{3,8})\b|rgba?\(|hsla?\(/g;
const literalTextPattern = />\s*([A-Za-z][^<{}`]{2,})\s*</g;
const allowedTextSnippets = ['http://', 'https://'];

async function walk(dir) {
  const entries = await fs.readdir(dir, { withFileTypes: true });
  const nested = await Promise.all(entries.map(async (entry) => {
    const fullPath = path.join(dir, entry.name);
    if (entry.isDirectory()) {
      return walk(fullPath);
    }
    return [fullPath];
  }));
  return nested.flat();
}

function shouldIgnore(filePath) {
  return ignoredFragments.some((fragment) => filePath.includes(fragment));
}

function allowsColorLiterals(filePath) {
  return allowedColorFiles.some((fragment) => filePath.includes(fragment));
}

function formatIssue(filePath, lineNumber, message) {
  return `${path.relative(root, filePath)}:${lineNumber} ${message}`;
}

async function main() {
  const files = (await walk(srcDir)).filter((filePath) => filePattern.test(filePath));
  const issues = [];

  for (const filePath of files) {
    if (shouldIgnore(filePath)) {
      continue;
    }

    const raw = await fs.readFile(filePath, 'utf8');
    const lines = raw.split('\n');

    if (!allowsColorLiterals(filePath)) {
      lines.forEach((line, index) => {
        if (colorPattern.test(line)) {
          issues.push(formatIssue(filePath, index + 1, 'hard-coded color literal; route colors through theme tokens or CSS variables'));
        }
        colorPattern.lastIndex = 0;
      });
    }

    if (/\.(tsx|jsx)$/.test(filePath)) {
      lines.forEach((line, index) => {
        const matches = [...line.matchAll(literalTextPattern)];
        for (const match of matches) {
          const text = (match[1] || '').trim();
          if (!text) {
            continue;
          }
          if (allowedTextSnippets.some((snippet) => text.includes(snippet))) {
            continue;
          }
          if (text.includes('t(') || text.includes('{') || text.includes('}')) {
            continue;
          }
          issues.push(formatIssue(filePath, index + 1, `hard-coded JSX text "${text}"`));
        }
      });
    }
  }

  if (issues.length > 0) {
    console.error('UI guardrail violations found:\n');
    issues.forEach((issue) => console.error(`- ${issue}`));
    process.exit(1);
  }

  console.log('UI guardrails passed');
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
