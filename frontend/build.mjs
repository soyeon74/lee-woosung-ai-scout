import { mkdir, copyFile, writeFile } from 'node:fs/promises';
import { join } from 'node:path';
const dest = join(process.cwd(), 'dist');
const base = process.env.API_BASE_URL || 'https://lee-woosung-ai-scout.onrender.com';
if (!/^https:\/\/[^\s/]+(?:\/[^\s]*)?$/.test(base)) {
  throw new Error('API_BASE_URL must be a valid HTTPS URL');
}
await mkdir(dest, { recursive: true });
for (const file of ['index.html', 'styles.css', 'app.js']) {
  await copyFile(join(process.cwd(),file), join(dest,file));
}
await writeFile(join(dest,'config.js'), `// Public backend URL only; NEVER include credentials here.\nwindow.API_BASE_URL = ${JSON.stringify(base.replace(/\/$/, ''))};\n`, 'utf8');
console.log('Vercel static build complete');
