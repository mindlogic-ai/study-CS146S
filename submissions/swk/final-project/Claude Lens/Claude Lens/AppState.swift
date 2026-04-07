import Foundation

/// Global observable state for the overlay app.
/// Created as a @State in the App entry point and passed through the environment.
/// Not a singleton — no `.shared`.
@MainActor
@Observable
final class AppState {
    var isOverlayVisible = false
    var pendingCapturedText: String?
    var pendingCapturedImage: Data?
    var isCapturingScreenshot = false
    var showOnboarding: Bool

    var isOnboardingComplete: Bool {
        get { UserDefaults.standard.bool(forKey: "isOnboardingComplete") }
        set {
            UserDefaults.standard.set(newValue, forKey: "isOnboardingComplete")
            if newValue { showOnboarding = false }
        }
    }

    var selectedModel: String {
        get { UserDefaults.standard.string(forKey: "selectedModel") ?? "claude-sonnet-4-20250514" }
        set { UserDefaults.standard.set(newValue, forKey: "selectedModel") }
    }

    init() {
        let completed = UserDefaults.standard.bool(forKey: "isOnboardingComplete")
        self.showOnboarding = !completed
    }

    func toggleOverlay() {
        isOverlayVisible.toggle()
    }

    func showOverlay() {
        isOverlayVisible = true
    }

    func hideOverlay() {
        isOverlayVisible = false
    }

    static let availableModels: [(id: String, name: String)] = [
        ("claude-sonnet-4-20250514", "Claude Sonnet 4"),
        ("claude-haiku-4-5-20251001", "Claude Haiku 4.5"),
        ("claude-opus-4-6", "Claude Opus 4.6")
    ]
}
