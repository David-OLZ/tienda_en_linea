'use strict';
// Lanza el backend de Python y espera la línea "TIENDA_BACKEND_READY port=NNNN".
const { spawn } = require('child_process');
const path = require('path');

const READY = /TIENDA_BACKEND_READY port=(\d+)/;

function pythonCandidates(platform = process.platform, envPython = process.env.TIENDA_PYTHON) {
  const list = [];
  if (envPython) list.push({ cmd: envPython, args: [] });
  if (platform === 'win32') {
    list.push({ cmd: 'py', args: ['-3'] }, { cmd: 'python', args: [] });
  } else {
    list.push({ cmd: 'python3', args: [] }, { cmd: 'python', args: [] });
  }
  return list;
}

function trySpawn(candidate, backendDir, dbPath, timeoutMs = 10000) {
  return new Promise((resolve, reject) => {
    const child = spawn(
      candidate.cmd,
      [...candidate.args, path.join(backendDir, 'main.py'), '--db', dbPath, '--port', '0'],
      {
        cwd: backendDir,
        windowsHide: true,
        env: { ...process.env, PYTHONIOENCODING: 'utf-8', PYTHONUNBUFFERED: '1' },
      }
    );
    let out = '';
    let err = '';
    let settled = false;
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(timer);
      fn(value);
    };
    const timer = setTimeout(() => {
      child.kill();
      finish(reject, new Error('Tiempo de espera agotado al iniciar el backend.'));
    }, timeoutMs);

    child.stdout.on('data', (chunk) => {
      out += chunk.toString();
      const match = READY.exec(out);
      if (match) finish(resolve, { child, port: Number(match[1]) });
    });
    child.stderr.on('data', (chunk) => { err += chunk.toString(); });
    child.on('error', (e) => finish(reject, e));
    child.on('exit', (code) => finish(reject, new Error(`Python terminó con código ${code}. ${err.trim()}`)));
  });
}

async function startBackend({ dbPath, backendDir }) {
  const problems = [];
  for (const candidate of pythonCandidates()) {
    try {
      const { child, port } = await trySpawn(candidate, backendDir, dbPath);
      return { baseUrl: `http://127.0.0.1:${port}`, stop: () => child.kill() };
    } catch (e) {
      problems.push(`${candidate.cmd}: ${e.message}`);
    }
  }
  throw new Error(
    'No se pudo iniciar el backend. Instala Python 3.9+ o define la variable TIENDA_PYTHON.\n\n' +
    problems.join('\n')
  );
}

module.exports = { startBackend, pythonCandidates };
