import SwiftData
import SwiftUI

struct ContentView: View {
    @Environment(\.modelContext) private var modelContext
    @Environment(\.services) private var services
    @State private var sessionListVM = SessionListViewModel()

    var body: some View {
        NavigationSplitView {
            SidebarView(sessionListVM: sessionListVM)
                .navigationSplitViewColumnWidth(min: 200, ideal: 250)
        } detail: {
            if let selectedID = sessionListVM.selectedSessionID,
               let session = fetchSession(id: selectedID)
            {
                ChatView(session: session)
            } else {
                emptyState
            }
        }
        .frame(minWidth: 700, minHeight: 500)
        .onAppear {
            ensureSessionSelected()
        }
    }

    private var emptyState: some View {
        VStack(spacing: 16) {
            Image(systemName: "bubble.left.and.text.bubble.right")
                .font(.system(size: 48))
                .foregroundStyle(.tertiary)
            Text("Select a session or create a new one")
                .font(.title3)
                .foregroundStyle(.secondary)

            if !services.keychainService.hasKey {
                VStack(spacing: 8) {
                    Text("API key not configured")
                        .font(.headline)
                        .foregroundStyle(.orange)
                    Text("Go to Settings (⌘,) to set your Anthropic API key")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                .padding(.top, 12)
            }

            Button("New Chat") {
                _ = sessionListVM.createSession(modelContext: modelContext)
            }
            .keyboardShortcut("n", modifiers: .command)
        }
        .frame(maxWidth: .infinity, maxHeight: .infinity)
    }

    private func ensureSessionSelected() {
        guard sessionListVM.selectedSessionID == nil else { return }
        let descriptor = FetchDescriptor<Session>(
            sortBy: [SortDescriptor(\.updatedAt, order: .reverse)]
        )
        let sessions = (try? modelContext.fetch(descriptor)) ?? []
        if let latest = sessions.first {
            sessionListVM.selectedSessionID = latest.persistentModelID
        } else {
            _ = sessionListVM.createSession(modelContext: modelContext)
        }
    }

    private func fetchSession(id: PersistentIdentifier) -> Session? {
        let descriptor = FetchDescriptor<Session>()
        let sessions = (try? modelContext.fetch(descriptor)) ?? []
        return sessions.first { $0.persistentModelID == id }
    }
}
