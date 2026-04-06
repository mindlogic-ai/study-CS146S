import Foundation
import SwiftData
import Testing
@testable import Claude_Lens

@Suite("SessionListViewModel")
@MainActor
struct SessionListViewModelTests {

    // MARK: - Helpers

    /// Creates an isolated in-memory ModelContainer for each test.
    private func makeContainer() throws -> ModelContainer {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        return try ModelContainer(for: Session.self, Message.self, configurations: config)
    }

    private func makeViewModel() -> SessionListViewModel {
        SessionListViewModel()
    }

    // MARK: - createSession

    @Test("createSession inserts a new session with default title")
    func createSessionInsertsDefault() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()

        // When
        let session = vm.createSession(modelContext: context)

        // Then
        #expect(session.title == "New Chat")
        #expect(session.messages.isEmpty)
        #expect(session.isAutoTitled == true)
    }

    @Test("createSession sets selectedSessionID to new session")
    func createSessionSetsSelectedID() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()

        // When
        let session = vm.createSession(modelContext: context)

        // Then
        #expect(vm.selectedSessionID == session.persistentModelID)
    }

    @Test("createSession returns unique sessions on multiple calls")
    func createSessionMultipleUnique() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()

        // When
        let s1 = vm.createSession(modelContext: context)
        let s2 = vm.createSession(modelContext: context)

        // Then
        #expect(s1.id != s2.id)
    }

    // MARK: - deleteSession

    @Test("deleteSession removes the session from context")
    func deleteSessionRemovesFromContext() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let session = vm.createSession(modelContext: context)

        // When
        vm.deleteSession(session, modelContext: context)

        // Then — fetch all sessions
        let remaining = try context.fetch(FetchDescriptor<Session>())
        #expect(remaining.isEmpty)
    }

    @Test("deleteSession clears selectedSessionID when deleting selected session")
    func deleteSessionClearsSelectedID() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let session = vm.createSession(modelContext: context)
        #expect(vm.selectedSessionID == session.persistentModelID)

        // When
        vm.deleteSession(session, modelContext: context)

        // Then
        #expect(vm.selectedSessionID == nil)
    }

    @Test("deleteSession does not clear selectedSessionID for a different session")
    func deleteSessionPreservesOtherSelectedID() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let s1 = vm.createSession(modelContext: context)
        let s2 = vm.createSession(modelContext: context)
        // Select s1
        vm.selectedSessionID = s1.persistentModelID

        // When — delete s2 (not selected)
        vm.deleteSession(s2, modelContext: context)

        // Then
        #expect(vm.selectedSessionID == s1.persistentModelID)
    }

    // MARK: - deleteAllSessions

    @Test("deleteAllSessions removes all sessions")
    func deleteAllSessionsRemovesAll() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        _ = vm.createSession(modelContext: context)
        _ = vm.createSession(modelContext: context)
        _ = vm.createSession(modelContext: context)

        // When
        vm.deleteAllSessions(modelContext: context)

        // Then
        let remaining = try context.fetch(FetchDescriptor<Session>())
        #expect(remaining.isEmpty)
    }

    @Test("deleteAllSessions clears selectedSessionID")
    func deleteAllSessionsClearsSelection() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        _ = vm.createSession(modelContext: context)

        // When
        vm.deleteAllSessions(modelContext: context)

        // Then
        #expect(vm.selectedSessionID == nil)
    }

    // MARK: - filteredSessions

    @Test("filteredSessions returns all sessions when searchText is empty")
    func filteredSessionsEmptySearch() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let s1 = vm.createSession(modelContext: context)
        s1.title = "Swift Tips"
        let s2 = vm.createSession(modelContext: context)
        s2.title = "Python Notes"
        vm.searchText = ""

        // When
        let results = vm.filteredSessions([s1, s2])

        // Then
        #expect(results.count == 2)
    }

    @Test("filteredSessions filters by matching title substring")
    func filteredSessionsByTitle() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let s1 = vm.createSession(modelContext: context)
        s1.title = "Swift Tips"
        let s2 = vm.createSession(modelContext: context)
        s2.title = "Python Notes"
        vm.searchText = "swift"

        // When
        let results = vm.filteredSessions([s1, s2])

        // Then
        #expect(results.count == 1)
        #expect(results.first?.title == "Swift Tips")
    }

    @Test("filteredSessions is case-insensitive")
    func filteredSessionsCaseInsensitive() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let session = vm.createSession(modelContext: context)
        session.title = "Swift Tips"
        vm.searchText = "SWIFT"

        // When
        let results = vm.filteredSessions([session])

        // Then
        #expect(results.count == 1)
    }

    @Test("filteredSessions returns empty array when no titles match")
    func filteredSessionsNoMatch() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let s1 = vm.createSession(modelContext: context)
        s1.title = "Swift Tips"
        vm.searchText = "Rust"

        // When
        let results = vm.filteredSessions([s1])

        // Then
        #expect(results.isEmpty)
    }

    @Test("filteredSessions sorts by updatedAt descending")
    func filteredSessionsSortedNewestFirst() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let s1 = vm.createSession(modelContext: context)
        s1.title = "Older"
        s1.updatedAt = Date(timeIntervalSinceNow: -3600) // 1 hour ago

        let s2 = vm.createSession(modelContext: context)
        s2.title = "Newer"
        s2.updatedAt = Date(timeIntervalSinceNow: -60)   // 1 minute ago
        vm.searchText = ""

        // When
        let results = vm.filteredSessions([s1, s2])

        // Then — newest first
        #expect(results.first?.title == "Newer")
        #expect(results.last?.title == "Older")
    }

    // MARK: - storageInfo

    @Test("storageInfo returns zero counts for empty sessions list")
    func storageInfoEmpty() throws {
        // Given
        let vm = makeViewModel()

        // When
        let info = vm.storageInfo(sessions: [])

        // Then
        #expect(info.sessionCount == 0)
        #expect(info.messageCount == 0)
        #expect(!info.estimatedSize.isEmpty)
    }

    @Test("storageInfo counts sessions and messages correctly")
    func storageInfoCountsMessages() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()

        let s1 = vm.createSession(modelContext: context)
        let msg1 = Message(role: .user, content: "Hello")
        let msg2 = Message(role: .assistant, content: "World")
        msg1.session = s1
        msg2.session = s1
        s1.messages.append(contentsOf: [msg1, msg2])

        let s2 = vm.createSession(modelContext: context)
        let msg3 = Message(role: .user, content: "Foo")
        msg3.session = s2
        s2.messages.append(msg3)

        // When
        let info = vm.storageInfo(sessions: [s1, s2])

        // Then
        #expect(info.sessionCount == 2)
        #expect(info.messageCount == 3)
    }

    @Test("storageInfo estimated size is non-empty string")
    func storageInfoSizeNonEmpty() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let vm = makeViewModel()
        let session = vm.createSession(modelContext: context)
        let msg = Message(role: .user, content: "A sample message with some content.")
        msg.session = session
        session.messages.append(msg)

        // When
        let info = vm.storageInfo(sessions: [session])

        // Then
        #expect(!info.estimatedSize.isEmpty)
    }
}
