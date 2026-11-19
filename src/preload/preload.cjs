'use strict';
const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('tiendaApi', {
  request: (req) => ipcRenderer.invoke('api:request', req),
});
