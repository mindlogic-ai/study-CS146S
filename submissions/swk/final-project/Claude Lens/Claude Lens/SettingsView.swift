import SwiftData
import SwiftUI

struct SettingsView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.services) private var services
    @Query private var sessions: [Session]
    @State private var settingsVM: SettingsViewModel?
    @State private var showDeleteConfirmation = false
    @State private var appState = AppState()
    @State private var sessionListVM = SessionListViewModel()

    var body: some View {
        Group {
            if let vm = settingsVM {
                TabView {
                    generalTab(vm: vm)
                        .tabItem { Label("General", systemImage: "gear") }
                    apiTab(vm: vm)
                        .tabItem { Label("API", systemImage: "key") }
                    dataTab
                        .tabItem { Label("Data", systemImage: "externaldrive") }
                }
                .frame(width: 480, height: 400)
            }
        }
        .onAppear {
            if settingsVM == nil {
                settingsVM = SettingsViewModel(
                    apiService: services.apiService,
                    keychainService: services.keychainService
                )
            }
        }
    }

    // MARK: - General Tab

    private func generalTab(vm: SettingsViewModel) -> some View {
        Form {
            Section("Model") {
                Picker("Claude Model", selection: Binding(
                    get: { appState.selectedModel },
                    set: { appState.selectedModel = $0 }
                )) {
                    ForEach(AppState.availableModels, id: \.id) { model in
                        Text(model.name).tag(model.id)
                    }
                }
            }

            Section("Permissions") {
                HStack {
                    Text("Accessibility")
                    Spacer()
                    if vm.isAccessibilityGranted {
                        Label("Granted", systemImage: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                    } else {
                        Button("Grant") {
                            services.textSelectionService.requestAccessibility()
                        }
                    }
                }
                HStack {
                    Text("Screen Recording")
                    Spacer()
                    if vm.isScreenCaptureGranted {
                        Label("Granted", systemImage: "checkmark.circle.fill")
                            .foregroundStyle(.green)
                    } else {
                        Button("Grant") {
                            services.screenCaptureService.requestScreenCaptureAccess()
                        }
                    }
                }
            }

            Section("Shortcuts") {
                HStack {
                    Text("Text Quick Capture")
                    Spacer()
                    Text("⌘+⇧+L")
                        .font(.system(.body, design: .monospaced))
                        .foregroundStyle(.secondary)
                }
                HStack {
                    Text("Screenshot Quick Capture")
                    Spacer()
                    Text("⌘+⇧+K")
                        .font(.system(.body, design: .monospaced))
                        .foregroundStyle(.secondary)
                }
            }
        }
        .formStyle(.grouped)
    }

    // MARK: - API Tab

    private func apiTab(vm: SettingsViewModel) -> some View {
        Form {
            Section("API Key") {
                HStack {
                    Text("Current key:")
                    Text(vm.maskedKey)
                        .font(.system(.body, design: .monospaced))
                        .foregroundStyle(.secondary)
                }

                HStack {
                    SecureField("New API key", text: Binding(
                        get: { vm.apiKeyInput },
                        set: { vm.apiKeyInput = $0 }
                    ))
                    .textFieldStyle(.roundedBorder)

                    Button("Save") {
                        Task { _ = await vm.saveAPIKey() }
                    }
                    .disabled(vm.apiKeyInput.isEmpty)
                }

                if vm.isValidating {
                    ProgressView("Validating...")
                        .controlSize(.small)
                }
                if let result = vm.validationResult {
                    Label(
                        result ? "Key saved!" : "Invalid key",
                        systemImage: result ? "checkmark.circle" : "xmark.circle"
                    )
                    .foregroundStyle(result ? .green : .red)
                }

                if vm.hasAPIKey {
                    Button("Delete API Key", role: .destructive) {
                        vm.deleteAPIKey()
                    }
                }
            }

            Section("System Prompt") {
                TextEditor(text: Binding(
                    get: { vm.customSystemPrompt },
                    set: { vm.customSystemPrompt = $0 }
                ))
                .frame(height: 100)
                .font(.system(.body, design: .monospaced))

                if !vm.customSystemPrompt.isEmpty {
                    Button("Reset to Default") {
                        vm.customSystemPrompt = ""
                    }
                }

                Text("Leave empty to use mode-specific default prompts.")
                    .font(.caption)
                    .foregroundStyle(.tertiary)
            }
        }
        .formStyle(.grouped)
    }

    // MARK: - Data Tab

    private var dataTab: some View {
        Form {
            Section("Storage") {
                let info = sessionListVM.storageInfo(sessions: sessions)
                LabeledContent("Sessions", value: "\(info.sessionCount)")
                LabeledContent("Messages", value: "\(info.messageCount)")
                LabeledContent("Size", value: info.estimatedSize)
            }

            Section("Danger Zone") {
                Button("Delete All Sessions", role: .destructive) {
                    showDeleteConfirmation = true
                }
                .confirmationDialog(
                    "Delete all sessions?",
                    isPresented: $showDeleteConfirmation,
                    titleVisibility: .visible
                ) {
                    Button("Delete All", role: .destructive) {
                        sessionListVM.deleteAllSessions(modelContext: modelContext)
                    }
                    Button("Cancel", role: .cancel) {}
                } message: {
                    Text("This will permanently delete all chat sessions and messages. This action cannot be undone.")
                }
            }
        }
        .formStyle(.grouped)
    }
}
