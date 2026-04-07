import Foundation

/// Abstracts macOS pasteboard (NSPasteboard) operations.
/// Must be called on @MainActor since NSPasteboard is main-thread bound.
@MainActor
protocol ClipboardServiceProtocol {

    /// Read the current text content from the system pasteboard.
    func readText() -> String?

    /// Read image data (PNG) from the system pasteboard.
    func readImage() -> Data?

    /// Whether the pasteboard currently contains image data.
    func hasImage() -> Bool

    /// Write text to the system pasteboard, replacing current contents.
    func writeText(_ text: String)

    /// Snapshot the current pasteboard contents for later restoration.
    /// Returns opaque data that can be passed to `restore(from:)`.
    func backup() -> Data?

    /// Restore pasteboard contents from a previous `backup()` snapshot.
    func restore(from backupData: Data?)
}
