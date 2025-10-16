#!/usr/bin/env node

// Simple Node generator that writes a placeholder PNG file.

const fs = require('node:fs');

const PLACEHOLDER_PNG = Buffer.from(
  'iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAAOklEQVR4nO3BAQEAAACCIP+vbkcKBQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAADwGgAB9gABNDBthQAAAABJRU5ErkJggg==',
  'base64',
);

function parseArgs(argv) {
  const result = {};
  for (let i = 0; i < argv.length; i += 1) {
    const current = argv[i];
    if (current.startsWith('--')) {
      const key = current.slice(2);
      const value = argv[i + 1];
      result[key] = value;
      i += 1;
    }
  }
  return result;
}

const args = parseArgs(process.argv.slice(2));

if (!args.output) {
  console.error('Missing required --output argument.');
  process.exit(1);
}

try {
  fs.writeFileSync(args.output, PLACEHOLDER_PNG);
  process.exit(0);
} catch (error) {
  console.error('Failed to write output:', error);
  process.exit(1);
}
