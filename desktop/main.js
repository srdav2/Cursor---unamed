const { app, BrowserWindow, dialog } = require('electron');
const path = require('path');
const execa = require('execa');

let backendProcess = null;

async function startBackend(projectRoot) {
  try {
    const venvPath = path.join(projectRoot, 'backend', 'venv');
    const requirements = path.join(projectRoot, 'backend', 'requirements.txt');
    // Create venv if missing
    await execa('python3', ['-m', 'venv', venvPath], { cwd: projectRoot, stdio: 'ignore' }).catch(() => {});
    // Install requirements
    const pipBin = path.join(venvPath, 'bin', 'pip');
    await execa(pipBin, ['install', '--upgrade', 'pip'], { cwd: projectRoot, stdio: 'ignore' });
    await execa(pipBin, ['install', '-r', requirements], { cwd: projectRoot, stdio: 'inherit' });
    // Start flask
    const pythonBin = path.join(venvPath, 'bin', 'python');
    backendProcess = execa(pythonBin, ['-m', 'flask', 'run', '--port', '5000'], {
      cwd: projectRoot,
      env: { ...process.env, FLASK_APP: 'backend/main.py' },
      stdio: 'inherit'
    });
  } catch (err) {
    dialog.showErrorBox('Backend failed to start', String(err));
  }
}

function createWindow(projectRoot) {
  const win = new BrowserWindow({
    width: 1400,
    height: 900,
    webPreferences: { nodeIntegration: false, contextIsolation: true }
  });
  const indexPath = path.join(projectRoot, 'frontend', 'index.html');
  win.loadFile(indexPath);
}

app.whenReady().then(async () => {
  const projectRoot = path.join(__dirname, '..');
  await startBackend(projectRoot);
  createWindow(projectRoot);

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow(projectRoot);
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('quit', async () => {
  try { if (backendProcess) backendProcess.kill(); } catch (_) {}
});


