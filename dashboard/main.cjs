const { app, BrowserWindow } = require('electron');
const path = require('path');
const isDev = require('electron-is-dev');

function createWindow() {
  const win = new BrowserWindow({
    width: 1280,
    height: 800,
    title: "MIJA Sovereign Dashboard",
    backgroundColor: "#020617",
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  setTimeout(() => {
    win.loadURL(
      isDev
        ? 'http://localhost:5173'
        : `file://${path.join(__dirname, '../dist/index.html')}`
    );
  }, 3000);

  win.setMenuBarVisibility(false);
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});
