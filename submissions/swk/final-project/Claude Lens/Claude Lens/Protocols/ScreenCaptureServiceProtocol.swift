import Foundation
import CoreGraphics

/// Abstracts screen region capture using ScreenCaptureKit.
/// Requires macOS Screen Recording permission.
@MainActor
protocol ScreenCaptureServiceProtocol {

    /// Capture a specific screen region as PNG image data.
    ///
    /// - Parameter rect: The screen rectangle to capture (in screen coordinates).
    /// - Returns: PNG-encoded image data, or `nil` on failure or permission denial.
    func captureScreenRegion(rect: CGRect) async -> Data?

    /// Whether the Screen Recording permission has been granted.
    var isScreenCaptureGranted: Bool { get }

    /// Request Screen Recording permission from the user.
    func requestScreenCaptureAccess()
}
