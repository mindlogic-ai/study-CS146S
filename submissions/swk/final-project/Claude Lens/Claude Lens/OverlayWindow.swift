import AppKit
import SwiftUI

final class OverlayPanel: NSPanel {
    override var canBecomeKey: Bool { true }
    override var canBecomeMain: Bool { true }

    init(contentRect: NSRect) {
        super.init(
            contentRect: contentRect,
            styleMask: [.titled, .closable, .resizable, .nonactivatingPanel, .fullSizeContentView],
            backing: .buffered,
            defer: false
        )

        level = .floating
        isFloatingPanel = true
        hidesOnDeactivate = false
        titlebarAppearsTransparent = true
        titleVisibility = .hidden
        isMovableByWindowBackground = true
        isOpaque = false
        backgroundColor = NSColor.windowBackgroundColor
        collectionBehavior = [.canJoinAllSpaces, .fullScreenAuxiliary]

        // Restore saved position
        if let frameString = UserDefaults.standard.string(forKey: "overlayWindowFrame") {
            let frame = NSRectFromString(frameString)
            if frame.width > 0 && frame.height > 0 {
                setFrame(frame, display: false)
            }
        }
    }

    override func close() {
        // Save position before closing
        UserDefaults.standard.set(
            NSStringFromRect(frame),
            forKey: "overlayWindowFrame"
        )
        orderOut(nil)
    }
}

@MainActor
final class OverlayWindowController {
    static let shared = OverlayWindowController()
    private var panel: OverlayPanel?

    private init() {}

    func show(with content: some View) {
        if panel == nil {
            let defaultFrame = NSRect(x: 0, y: 0, width: 750, height: 550)
            panel = OverlayPanel(contentRect: defaultFrame)
            let hostingView = NSHostingView(rootView: content)
            panel?.contentView = hostingView
            panel?.center()
        }
        panel?.makeKeyAndOrderFront(nil)
        NSApp.activate(ignoringOtherApps: true)
    }

    func hide() {
        panel?.close()
    }

    func toggle(with content: some View) {
        if panel?.isVisible == true {
            hide()
        } else {
            show(with: content)
        }
    }

    var isVisible: Bool {
        panel?.isVisible ?? false
    }
}
