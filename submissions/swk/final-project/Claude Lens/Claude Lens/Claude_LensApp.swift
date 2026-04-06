import SwiftData
import SwiftUI

@main
struct Claude_LensApp: App {
    // Composition root — create the service container once
    @State private var services = ServiceContainer.production()
    @State private var appState = AppState()
    // showOnboarding is now on appState for NSHostingView observability

    var sharedModelContainer: ModelContainer = {
        let schema = Schema([Session.self, Message.self])
        let config = ModelConfiguration(schema: schema, isStoredInMemoryOnly: false)
        do {
            return try ModelContainer(for: schema, configurations: [config])
        } catch {
            fatalError("Could not create ModelContainer: \(error)")
        }
    }()

    init() {
        // Defer hotkey registration until after the app is fully initialized
        DispatchQueue.main.async { [self] in
            wireHotkeys()
        }
    }

    private var overlayContent: some View {
        Group {
            if appState.showOnboarding {
                OnboardingView {
                    appState.isOnboardingComplete = true
                }
            } else {
                ContentView()
                    .environment(appState)
            }
        }
        .modelContainer(sharedModelContainer)
        .environment(\.services, services)
    }

    var body: some Scene {
        // Menu Bar
        MenuBarExtra("Claude Lens", systemImage: "sparkle.magnifyingglass") {
            Button("Show/Hide Overlay") {
                OverlayWindowController.shared.toggle(with: overlayContent)
            }
            .keyboardShortcut("l", modifiers: [.command, .shift])

            Divider()

            Button("New Session") {
                OverlayWindowController.shared.show(with: overlayContent)
            }
            .keyboardShortcut("n", modifiers: .command)

            SettingsLink {
                Text("Settings...")
            }
            .keyboardShortcut(",", modifiers: .command)

            Divider()

            Button("Quit Claude Lens") {
                services.hotkeyService.unregister()
                NSApplication.shared.terminate(nil)
            }
            .keyboardShortcut("q", modifiers: .command)
        }

        // Settings window
        Settings {
            SettingsView()
                .modelContainer(sharedModelContainer)
                .environment(\.services, services)
        }
    }

    // MARK: - Hotkey wiring

    @MainActor
    private func wireHotkeys() {
        services.hotkeyService.onTextCapture = { [self] in
            Task { @MainActor in
                if services.textSelectionService.isAccessibilityGranted {
                    let text = await services.textSelectionService.captureSelectedText()
                    appState.pendingCapturedText = text
                } else if let text = services.clipboardService.readText() {
                    appState.pendingCapturedText = text
                }
                if appState.pendingCapturedText == nil,
                   let imageData = services.clipboardService.readImage()
                {
                    appState.pendingCapturedImage = imageData
                }
                OverlayWindowController.shared.show(with: overlayContent)
            }
        }
        services.hotkeyService.onScreenshotCapture = { [self] in
            Task { @MainActor in
                // Launch macOS interactive screen capture to clipboard
                let process = Process()
                process.executableURL = URL(fileURLWithPath: "/usr/sbin/screencapture")
                process.arguments = ["-ic"] // interactive, clipboard
                try? process.run()
                process.waitUntilExit()

                // Read captured image from clipboard
                if let imageData = services.clipboardService.readImage() {
                    appState.pendingCapturedImage = imageData
                    OverlayWindowController.shared.show(with: overlayContent)
                }
            }
        }
        services.hotkeyService.register()
    }
}
