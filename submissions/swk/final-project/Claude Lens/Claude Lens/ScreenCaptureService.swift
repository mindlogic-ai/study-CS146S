import AppKit
import Foundation
import ScreenCaptureKit

/// Concrete implementation of ScreenCaptureServiceProtocol.
/// @MainActor because ScreenCaptureKit callbacks dispatch on the main thread.
@MainActor
final class ScreenCaptureService: ScreenCaptureServiceProtocol {

    init() {}

    var isScreenCaptureGranted: Bool {
        CGPreflightScreenCaptureAccess()
    }

    func requestScreenCaptureAccess() {
        // Register the app in the Screen Recording list
        CGRequestScreenCaptureAccess()
        // Then open System Settings to let the user toggle it on
        if let url = URL(string: "x-apple.systempreferences:com.apple.preference.security?Privacy_ScreenCapture") {
            NSWorkspace.shared.open(url)
        }
    }

    func captureScreenRegion(rect: CGRect) async -> Data? {
        do {
            let availableContent = try await SCShareableContent.excludingDesktopWindows(
                false, onScreenWindowsOnly: true
            )
            guard let display = availableContent.displays.first else { return nil }

            let filter = SCContentFilter(display: display, excludingWindows: [])
            let config = SCStreamConfiguration()
            config.sourceRect = rect
            config.width = Int(rect.width) * 2
            config.height = Int(rect.height) * 2
            config.showsCursor = false

            let image = try await SCScreenshotManager.captureImage(
                contentFilter: filter,
                configuration: config
            )
            let bitmapRep = NSBitmapImageRep(cgImage: image)
            return bitmapRep.representation(using: .png, properties: [:])
        } catch {
            return nil
        }
    }
}
