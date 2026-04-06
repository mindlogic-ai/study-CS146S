import Foundation
import SwiftData

/// ViewModel for the session list sidebar.
/// No service dependencies — pure SwiftData CRUD.
@MainActor
@Observable
final class SessionListViewModel {
    var searchText = ""
    var selectedSessionID: PersistentIdentifier?

    init() {}

    func createSession(modelContext: ModelContext) -> Session {
        let session = Session()
        modelContext.insert(session)
        try? modelContext.save()
        selectedSessionID = session.persistentModelID
        return session
    }

    func deleteSession(_ session: Session, modelContext: ModelContext) {
        if selectedSessionID == session.persistentModelID {
            selectedSessionID = nil
        }
        modelContext.delete(session)
        try? modelContext.save()
    }

    func deleteAllSessions(modelContext: ModelContext) {
        try? modelContext.delete(model: Session.self)
        selectedSessionID = nil
        try? modelContext.save()
    }

    func filteredSessions(_ sessions: [Session]) -> [Session] {
        let sorted = sessions.sorted { $0.updatedAt > $1.updatedAt }
        if searchText.isEmpty {
            return sorted
        }
        return sorted.filter {
            $0.title.localizedCaseInsensitiveContains(searchText)
        }
    }

    func storageInfo(
        sessions: [Session]
    ) -> (sessionCount: Int, messageCount: Int, estimatedSize: String) {
        let sessionCount = sessions.count
        let messageCount = sessions.reduce(0) { $0 + $1.messages.count }
        var totalBytes: Int64 = 0
        for session in sessions {
            for message in session.messages {
                totalBytes += Int64(message.content.utf8.count)
                totalBytes += Int64(message.imageData?.count ?? 0)
            }
        }
        let formatter = ByteCountFormatter()
        formatter.countStyle = .file
        let sizeString = formatter.string(fromByteCount: totalBytes)
        return (sessionCount, messageCount, sizeString)
    }
}
