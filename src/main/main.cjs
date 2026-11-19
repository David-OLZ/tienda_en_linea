'use strict';
const { app, BrowserWindow, ipcMain, dialog } = require('electron');
const path = require('path');
const { startBackend } = require('./backend-process.cjs');
const { createClient } = require('./backend-client.cjs');

let backend = null;

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 900,
    minHeight: 600,
    title: 'Tienda en línea',
    webPreferences: {
      preload: path.join(__dirname, '..', 'preload', 'preload.cjs'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, '..', 'renderer', 'index.html'));
}

app.whenReady().then(async () => {
  try {
    const backendDir = path.join(app.isPackaged ? process.resourcesPath : app.getAppPath(), 'backend');
    backend = await startBackend({
      dbPath: path.join(app.getPath('userData'), 'tienda.db'),
      backendDir,
    });
    const client = createClient(backend.baseUrl);
    ipcMain.handle('api:request', (_event, req) => client.request(req));
    createWindow();
  } catch (err) {
    dialog.showErrorBox('No se pudo iniciar la tienda', err.message);
    app.quit();
  }
});

app.on('before-quit', () => { if (backend) backend.stop(); });
app.on('window-all-closed', () => app.quit());
