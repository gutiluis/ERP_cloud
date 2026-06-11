import { loadEnv } from './modules/envLoader'
loadEnv()

import { app } from 'electron'
import { WindowManager } from './modules/windowManager'

const gotLock = app.requestSingleInstanceLock()

if (!gotLock) {
  console.log("Process env:", process.env.MAIN_DB_PATH)
  app.quit()
  process.exit(0)
}


const windowManager = new WindowManager()

app.on('second-instance', () => {
  const win = windowManager.getMainWindow()
  if (win) {
    if (win.isMinimized()) win.restore()
    win.focus()
  }
})

app.whenReady().then(() => {
  windowManager.createMainWindow()

  if (process.platform === 'darwin') {
    app.dock?.show()
  }
})

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit()
})

app.on('activate', () => {
  if (!windowManager.getMainWindow()) {
    windowManager.createMainWindow()
  }
})

app.on('before-quit', () => {
  console.log('App is quitting')
})


process.on('uncaughtException', (err) => {
  console.error('Uncaught Exception:', err)
})