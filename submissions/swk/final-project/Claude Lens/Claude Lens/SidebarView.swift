import SwiftData
import SwiftUI

struct SidebarView: View {
    @Environment(\.modelContext) private var modelContext
    @Query(sort: \Session.updatedAt, order: .reverse) private var sessions: [Session]
    @Bindable var sessionListVM: SessionListViewModel

    var body: some View {
        VStack(spacing: 0) {
            // Search bar
            HStack {
                Image(systemName: "magnifyingglass")
                    .foregroundStyle(.secondary)
                TextField("Search sessions...", text: $sessionListVM.searchText)
                    .textFieldStyle(.plain)
                if !sessionListVM.searchText.isEmpty {
                    Button {
                        sessionListVM.searchText = ""
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)
                }
            }
            .padding(8)
            .background(Color(.controlBackgroundColor))
            .clipShape(RoundedRectangle(cornerRadius: 8))
            .padding(8)

            Divider()

            // Session list
            List(selection: $sessionListVM.selectedSessionID) {
                ForEach(sessionListVM.filteredSessions(sessions)) { session in
                    SessionRowView(session: session)
                        .tag(session.persistentModelID)
                        .contextMenu {
                            Button("Delete", role: .destructive) {
                                sessionListVM.deleteSession(session, modelContext: modelContext)
                            }
                        }
                }
            }
            .listStyle(.sidebar)

            Divider()

            // Bottom bar
            HStack {
                Button {
                    _ = sessionListVM.createSession(modelContext: modelContext)
                } label: {
                    Label("New Chat", systemImage: "plus")
                }
                .buttonStyle(.plain)
                .keyboardShortcut("n", modifiers: .command)

                Spacer()

                let info = sessionListVM.storageInfo(sessions: sessions)
                Text("\(info.sessionCount) sessions")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
            .padding(8)
        }
    }
}

private struct SessionRowView: View {
    let session: Session

    var body: some View {
        VStack(alignment: .leading, spacing: 2) {
            Text(session.title)
                .font(.body)
                .lineLimit(1)
            HStack {
                Image(systemName: session.mode.icon)
                    .font(.caption2)
                Text(session.updatedAt, style: .relative)
                    .font(.caption2)
            }
            .foregroundStyle(.secondary)
        }
        .padding(.vertical, 2)
    }
}
