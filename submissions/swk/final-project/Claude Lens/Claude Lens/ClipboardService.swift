import AppKit
import Foundation

/// Concrete implementation of ClipboardServiceProtocol.
/// @MainActor because NSPasteboard must be accessed on the main thread.
@MainActor
final class ClipboardService: ClipboardServiceProtocol {

    init() {}

    func readText() -> String? {
        NSPasteboard.general.string(forType: .string)
    }

    func readImage() -> Data? {
        let pasteboard = NSPasteboard.general
        if let tiffData = pasteboard.data(forType: .tiff) {
            guard let bitmapRep = NSBitmapImageRep(data: tiffData) else { return nil }
            return bitmapRep.representation(using: .png, properties: [:])
        }
        if let pngData = pasteboard.data(forType: .png) {
            return pngData
        }
        return nil
    }

    func hasImage() -> Bool {
        let pasteboard = NSPasteboard.general
        return pasteboard.canReadItem(withDataConformingToTypes: [
            NSPasteboard.PasteboardType.tiff.rawValue,
            NSPasteboard.PasteboardType.png.rawValue
        ])
    }

    func writeText(_ text: String) {
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        pasteboard.setString(text, forType: .string)
    }

    func backup() -> Data? {
        NSPasteboard.general.data(forType: .string)
            ?? NSPasteboard.general.data(forType: .tiff)
    }

    func restore(from backupData: Data?) {
        guard let data = backupData else { return }
        let pasteboard = NSPasteboard.general
        pasteboard.clearContents()
        if let str = String(data: data, encoding: .utf8) {
            pasteboard.setString(str, forType: .string)
        } else {
            pasteboard.setData(data, forType: .tiff)
        }
    }
}
