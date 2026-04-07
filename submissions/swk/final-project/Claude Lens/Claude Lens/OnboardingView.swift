import SwiftUI

struct OnboardingView: View {
    @State private var currentStep = 0
    @State private var settingsVM: SettingsViewModel?
    @State private var isKeyValid: Bool?
    @Environment(\.services) private var services
    @Environment(AppState.self) private var appState

    var body: some View {
        VStack(spacing: 0) {
            // Progress indicator
            HStack(spacing: 8) {
                ForEach(0..<4, id: \.self) { step in
                    Circle()
                        .fill(step == currentStep ? Color.accentColor : Color.secondary.opacity(0.3))
                        .frame(width: 8, height: 8)
                }
            }
            .padding(.top, 24)

            Spacer()

            // Step content
            if let vm = settingsVM {
                Group {
                    switch currentStep {
                    case 0: welcomeStep
                    case 1: permissionsStep(vm: vm)
                    case 2: apiKeyStep(vm: vm)
                    case 3: readyStep
                    default: EmptyView()
                    }
                }
                .frame(maxWidth: 450)

                Spacer()

                // Navigation
                HStack {
                    if currentStep > 0 {
                        Button("Back") {
                            withAnimation { currentStep -= 1 }
                        }
                    }
                    Spacer()
                    if currentStep < 3 {
                        Button("Next") {
                            withAnimation { currentStep += 1 }
                        }
                        .buttonStyle(.borderedProminent)
                        .disabled(currentStep == 2 && !vm.hasAPIKey)
                    }
                }
                .padding(24)
            }
        }
        .frame(width: 520, height: 440)
        .onAppear {
            if settingsVM == nil {
                settingsVM = SettingsViewModel(
                    apiService: services.apiService,
                    keychainService: services.keychainService
                )
            }
        }
    }

    // MARK: - Steps

    private var welcomeStep: some View {
        VStack(spacing: 16) {
            Image(systemName: "sparkle.magnifyingglass")
                .font(.system(size: 56))
                .foregroundStyle(.purple)
            Text("Welcome to Claude Lens")
                .font(.title)
                .fontWeight(.bold)
            Text("Drag text or capture a screenshot, press a hotkey, and get instant AI responses.")
                .multilineTextAlignment(.center)
                .foregroundStyle(.secondary)
            HStack(spacing: 24) {
                featureCard(icon: "text.cursor", title: "Text Capture", desc: "⌘+⇧+L")
                featureCard(icon: "camera.viewfinder", title: "Screenshot", desc: "⌘+⌃+⇧+4")
                featureCard(icon: "bubble.left.and.bubble.right", title: "AI Chat", desc: "Streaming")
            }
            .padding(.top, 8)
        }
        .padding(24)
    }

    private func apiKeyStep(vm: SettingsViewModel) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "key")
                .font(.system(size: 40))
                .foregroundStyle(.orange)
            Text("API Key Setup")
                .font(.title2)
                .fontWeight(.bold)
            Text("Enter your Anthropic API key to enable Claude AI.")
                .font(.body)
                .foregroundStyle(.secondary)
                .multilineTextAlignment(.center)

            HStack {
                SecureField("sk-ant-...", text: Binding(
                    get: { vm.apiKeyInput },
                    set: { vm.apiKeyInput = $0 }
                ))
                .textFieldStyle(.roundedBorder)

                Button("Validate") {
                    Task {
                        isKeyValid = await vm.saveAPIKey()
                    }
                }
                .disabled(vm.apiKeyInput.isEmpty || vm.isValidating)
            }

            if vm.isValidating {
                ProgressView("Validating...")
                    .controlSize(.small)
            }
            if let valid = isKeyValid {
                Label(
                    valid ? "API key verified!" : "Invalid API key",
                    systemImage: valid ? "checkmark.circle.fill" : "xmark.circle.fill"
                )
                .foregroundStyle(valid ? .green : .red)
            }

            if let consoleURL = URL(string: "https://console.anthropic.com/settings/keys") {
                Link("Get an API key from Anthropic Console",
                     destination: consoleURL)
                    .font(.caption)
            }
        }
        .padding(24)
    }

    private func permissionsStep(vm: SettingsViewModel) -> some View {
        VStack(spacing: 16) {
            Image(systemName: "lock.shield")
                .font(.system(size: 40))
                .foregroundStyle(.blue)
            Text("Permissions")
                .font(.title2)
                .fontWeight(.bold)

            VStack(alignment: .leading, spacing: 12) {
                permissionRow(
                    icon: "hand.raised",
                    title: "Accessibility (Required)",
                    desc: "For text Quick Capture",
                    granted: vm.isAccessibilityGranted,
                    action: { services.textSelectionService.requestAccessibility() }
                )
                permissionRow(
                    icon: "camera",
                    title: "Screen Recording (Optional)",
                    desc: "For screenshot Quick Capture",
                    granted: vm.isScreenCaptureGranted,
                    action: { services.screenCaptureService.requestScreenCaptureAccess() }
                )
            }

            Text("Permissions can be changed later in System Settings.")
                .font(.caption)
                .foregroundStyle(.tertiary)
        }
        .padding(24)
    }

    private var readyStep: some View {
        VStack(spacing: 16) {
            Image(systemName: "checkmark.seal.fill")
                .font(.system(size: 56))
                .foregroundStyle(.green)
            Text("You're all set!")
                .font(.title)
                .fontWeight(.bold)

            VStack(alignment: .leading, spacing: 8) {
                shortcutRow("⌘+⇧+L", "Text Quick Capture")
                shortcutRow("⌘+⌃+⇧+4", "Screenshot Quick Capture")
                shortcutRow("Esc", "Hide overlay")
                shortcutRow("⌘+N", "New session")
            }

            Button("Start Using Claude Lens") {
                appState.isOnboardingComplete = true
            }
            .buttonStyle(.borderedProminent)
            .controlSize(.large)
        }
        .padding(24)
    }

    // MARK: - Helpers

    private func featureCard(icon: String, title: String, desc: String) -> some View {
        VStack(spacing: 6) {
            Image(systemName: icon)
                .font(.title2)
                .foregroundStyle(.purple)
            Text(title)
                .font(.caption)
                .fontWeight(.medium)
            Text(desc)
                .font(.caption2)
                .foregroundStyle(.secondary)
        }
        .frame(width: 100)
    }

    private func permissionRow(
        icon: String, title: String, desc: String,
        granted: Bool, action: @escaping () -> Void
    ) -> some View {
        HStack {
            Image(systemName: icon)
                .frame(width: 24)
            VStack(alignment: .leading) {
                Text(title).font(.body)
                Text(desc).font(.caption).foregroundStyle(.secondary)
            }
            Spacer()
            if granted {
                Image(systemName: "checkmark.circle.fill")
                    .foregroundStyle(.green)
            } else {
                Button("Grant") { action() }
                    .controlSize(.small)
            }
        }
        .padding(8)
        .background(Color(.controlBackgroundColor))
        .clipShape(RoundedRectangle(cornerRadius: 8))
    }

    private func shortcutRow(_ key: String, _ desc: String) -> some View {
        HStack {
            Text(key)
                .font(.system(.body, design: .monospaced))
                .fontWeight(.medium)
                .frame(width: 100, alignment: .trailing)
            Text(desc)
                .foregroundStyle(.secondary)
        }
    }
}
