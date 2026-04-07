import Carbon
import Cocoa
import Foundation

/// Concrete implementation of HotkeyServiceProtocol using the Carbon Event API.
/// @MainActor because Carbon event handlers dispatch on the main thread.
@MainActor
@Observable
final class HotkeyService: HotkeyServiceProtocol {

    private var textCaptureHotkeyRef: EventHotKeyRef?
    private var screenshotHotkeyRef: EventHotKeyRef?

    var onTextCapture: (() -> Void)?
    var onScreenshotCapture: (() -> Void)?

    // Shared instance used only by the Carbon C callback — not a public singleton.
    // The app wires callbacks before calling register().
    nonisolated(unsafe) static weak var _callbackInstance: HotkeyService?

    init() {}

    func register() {
        HotkeyService._callbackInstance = self
        registerGlobalHandler()
        // ⌘+⇧+L for text capture
        registerHotkey(
            keyCode: UInt32(kVK_ANSI_L),
            modifiers: UInt32(cmdKey | shiftKey),
            id: 1,
            ref: &textCaptureHotkeyRef
        )
        // ⌘+⌃+⇧+4 for screenshot capture
        registerHotkey(
            keyCode: UInt32(kVK_ANSI_4),
            modifiers: UInt32(cmdKey | shiftKey | controlKey),
            id: 2,
            ref: &screenshotHotkeyRef
        )
    }

    func unregister() {
        if let ref = textCaptureHotkeyRef {
            UnregisterEventHotKey(ref)
            textCaptureHotkeyRef = nil
        }
        if let ref = screenshotHotkeyRef {
            UnregisterEventHotKey(ref)
            screenshotHotkeyRef = nil
        }
        HotkeyService._callbackInstance = nil
    }

    private func registerHotkey(
        keyCode: UInt32,
        modifiers: UInt32,
        id: UInt32,
        ref: inout EventHotKeyRef?
    ) {
        let hotkeyID = EventHotKeyID(signature: OSType(0x434C_4E53), id: id)  // "CLNS"
        var hotKeyRef: EventHotKeyRef?
        let status = RegisterEventHotKey(
            keyCode,
            modifiers,
            hotkeyID,
            GetApplicationEventTarget(),
            0,
            &hotKeyRef
        )
        if status == noErr {
            ref = hotKeyRef
        }
    }

    private func registerGlobalHandler() {
        var eventType = EventTypeSpec(
            eventClass: OSType(kEventClassKeyboard),
            eventKind: UInt32(kEventHotKeyPressed)
        )
        InstallEventHandler(
            GetApplicationEventTarget(),
            { _, event, _ -> OSStatus in
                var hotkeyID = EventHotKeyID()
                GetEventParameter(
                    event,
                    EventParamName(kEventParamDirectObject),
                    EventParamType(typeEventHotKeyID),
                    nil,
                    MemoryLayout<EventHotKeyID>.size,
                    nil,
                    &hotkeyID
                )
                Task { @MainActor in
                    switch hotkeyID.id {
                    case 1:
                        HotkeyService._callbackInstance?.onTextCapture?()
                    case 2:
                        HotkeyService._callbackInstance?.onScreenshotCapture?()
                    default:
                        break
                    }
                }
                return noErr
            },
            1,
            &eventType,
            nil,
            nil
        )
    }
}
