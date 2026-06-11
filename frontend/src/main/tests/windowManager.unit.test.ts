import { describe, it, expect, beforeEach, vi } from 'vitest'
import { WindowManager } from '../modules/windowManager'

vi.mock('electron', () => {
  class MockBrowserWindow {
    loadURL = vi.fn()
    loadFile = vi.fn()
    webContents = { openDevTools: vi.fn() }
    once = vi.fn()
    on = vi.fn()
    show = vi.fn()
  }

  return {
    BrowserWindow: MockBrowserWindow,
    screen: {
      getPrimaryDisplay: () => ({ workAreaSize: { width: 1200, height: 800 } }),
    },
    app: { dock: { show: vi.fn() }, on: vi.fn() },
  }
})

import { BrowserWindow } from 'electron'

describe('WindowManager', () => {
  let wm: WindowManager

  beforeEach(() => {
    wm = new WindowManager()
  })

  it('creates main window', () => {
    const win = wm.createMainWindow()
    expect(win).toBeInstanceOf(BrowserWindow)
    expect(wm.getMainWindow()).toBe(win)
  })

  it('reuses main window if already created', () => {
    const first = wm.createMainWindow()
    const second = wm.createMainWindow()
    expect(first).toBe(second)
  })

  it('calls ready-to-show callback to show window', () => {
    const win = wm.createMainWindow()
    const onceMock = win.once as unknown as vi.Mock
    const callback = onceMock.mock.calls.find(c => c[0] === 'ready-to-show')?.[1]
    callback?.()
    expect(win.show).toHaveBeenCalled()
  })

  it('handles closed event', () => {
    const win = wm.createMainWindow()
    const onMock = win.on as unknown as vi.Mock
    const callback = onMock.mock.calls.find(c => c[0] === 'closed')?.[1]
    callback?.()
    expect(wm.getMainWindow()).toBeNull()
  })
})