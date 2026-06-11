import { BrowserWindow, screen } from 'electron'
import { join } from 'path'

/**
 * Manages the main application window
 * Modular window management - keeps index.ts clean
 */
export class WindowManager {
  private mainWindow: BrowserWindow | null = null

  public createMainWindow(): BrowserWindow {
    if (this.mainWindow) return this.mainWindow

    this.mainWindow = this.buildMainWindow()
    this.registerEvents(this.mainWindow)

    return this.mainWindow
  }

  private buildMainWindow(): BrowserWindow {
    const { width, height } = screen.getPrimaryDisplay().workAreaSize

    return new BrowserWindow({
      width: Math.min(1400, width),
      height: Math.min(900, height),
      minWidth: 1000,
      minHeight: 700,
      show: false,
      webPreferences: {
        preload: join(__dirname, '../preload/index.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: true,
      },
    })
  }

  private registerEvents(window: BrowserWindow) {
    window.once('ready-to-show', () => window.show())
    window.on('closed', () => {
      this.mainWindow = null
    })
  }

  public getMainWindow(): BrowserWindow | null {
    return this.mainWindow
  }
}