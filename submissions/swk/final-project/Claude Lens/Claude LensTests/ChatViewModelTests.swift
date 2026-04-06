import Foundation
import SwiftData
import Testing
@testable import Claude_Lens

@Suite("ChatViewModel", .serialized)
@MainActor
struct ChatViewModelTests {

    // MARK: - Helpers

    private func makeContainer() throws -> ModelContainer {
        let config = ModelConfiguration(isStoredInMemoryOnly: true)
        return try ModelContainer(for: Session.self, Message.self, configurations: config)
    }

    private func makeViewModel(
        apiKey: String? = "sk-ant-test-key",
        streamEvents: [StreamEvent] = [],
        streamError: Error? = nil,
        validateResult: Bool = true
    ) -> (ChatViewModel, MockClaudeAPIService, MockKeychainService) {
        let api = MockClaudeAPIService()
        api.streamMessageResult = streamEvents
        api.shouldThrowOnStream = streamError
        api.validateKeyResult = validateResult
        let keychain = MockKeychainService(preloadedKey: apiKey)
        let vm = ChatViewModel(apiService: api, keychainService: keychain)
        return (vm, api, keychain)
    }

    private func makeSession(in context: ModelContext) -> Session {
        let session = Session()
        context.insert(session)
        return session
    }

    // MARK: - Guard: missing API key

    @Test("sendMessage sets errorMessage when API key is absent")
    func sendMessageNoAPIKey() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, api, _) = makeViewModel(apiKey: nil)
        let session = makeSession(in: context)
        vm.inputText = "Hello"

        // When
        vm.sendMessage(session: session, modelContext: context)

        // Then
        #expect(vm.errorMessage != nil)
        #expect(vm.errorMessage?.contains("API key") == true)
        #expect(api.streamMessageCallCount == 0)
    }

    @Test("sendMessage does nothing when inputText is empty and no image attached")
    func sendMessageEmptyInput() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, api, _) = makeViewModel()
        let session = makeSession(in: context)
        vm.inputText = "   "

        // When
        vm.sendMessage(session: session, modelContext: context)

        // Then
        #expect(api.streamMessageCallCount == 0)
        #expect(session.messages.isEmpty)
    }

    // MARK: - Mode command parsing

    @Test("sendMessage with /translate command switches mode and does not call API")
    func sendMessageTranslateCommand() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, api, _) = makeViewModel()
        let session = makeSession(in: context)
        vm.inputText = "/translate"

        // When
        vm.sendMessage(session: session, modelContext: context)

        // Then
        #expect(session.mode == .translate)
        #expect(api.streamMessageCallCount == 0)
        #expect(vm.inputText == "")
        #expect(session.messages.isEmpty)
    }

    @Test("sendMessage with /explain command switches mode")
    func sendMessageExplainCommand() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, api, _) = makeViewModel()
        let session = makeSession(in: context)
        vm.inputText = "/explain"

        // When
        vm.sendMessage(session: session, modelContext: context)

        // Then
        #expect(session.mode == .explain)
        #expect(api.streamMessageCallCount == 0)
    }

    @Test("sendMessage with /code command switches mode")
    func sendMessageCodeCommand() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, api, _) = makeViewModel()
        let session = makeSession(in: context)
        vm.inputText = "/code"

        // When
        vm.sendMessage(session: session, modelContext: context)

        // Then
        #expect(session.mode == .code)
        #expect(api.streamMessageCallCount == 0)
    }

    // MARK: - Happy path: text message

    @Test("sendMessage creates user and assistant messages in session")
    func sendMessageCreatesMessages() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.textDelta("Hi"), .done]
        let (vm, _, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        vm.inputText = "Hello"

        // When
        vm.sendMessage(session: session, modelContext: context)
        // Allow the Task to complete
        try await Task.sleep(nanoseconds: 200_000_000) // 0.1s

        // Then
        #expect(session.messages.count == 2)
        let user = session.sortedMessages.first
        let assistant = session.sortedMessages.last
        #expect(user?.role == MessageRole.user.rawValue)
        #expect(user?.content == "Hello")
        #expect(assistant?.role == MessageRole.assistant.rawValue)
    }

    @Test("sendMessage streams text tokens into assistant message content")
    func sendMessageStreamsTokens() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [
            .textDelta("Hello"),
            .textDelta(", "),
            .textDelta("world!"),
            .done
        ]
        let (vm, _, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        vm.inputText = "Greet me"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        let assistant = session.sortedMessages.last
        #expect(assistant?.content == "Hello, world!")
        #expect(vm.currentResponse == "Hello, world!")
    }

    @Test("sendMessage updates token counts from stream events")
    func sendMessageUpdatesTokenCounts() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [
            .inputTokens(42),
            .textDelta("Response"),
            .outputTokens(7),
            .done
        ]
        let (vm, _, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        vm.inputText = "Count tokens"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(session.tokenCountInput == 42)
        #expect(session.tokenCountOutput == 7)
        #expect(session.totalTokens == 49)

        let userMsg = session.sortedMessages.first
        let assistantMsg = session.sortedMessages.last
        #expect(userMsg?.tokenCount == 42)
        #expect(assistantMsg?.tokenCount == 7)
    }

    @Test("sendMessage clears inputText after initiating send")
    func sendMessageClearsInputText() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, _, _) = makeViewModel(streamEvents: [.done])
        let session = makeSession(in: context)
        vm.inputText = "Clear me"

        // When
        vm.sendMessage(session: session, modelContext: context)

        // Then — inputText is cleared synchronously before the Task fires
        #expect(vm.inputText == "")
    }

    @Test("sendMessage sets isStreaming false after stream completes")
    func sendMessageIsStreamingLifecycle() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.textDelta("ok"), .done]
        let (vm, _, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        vm.inputText = "Test"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then — streaming should be done
        #expect(vm.isStreaming == false)
    }

    // MARK: - Image attachment

    @Test("attachImage sets attachedImageData")
    func attachImageSetsData() throws {
        // Given
        let (vm, _, _) = makeViewModel()
        let data = Data([0x89, 0x50, 0x4E, 0x47]) // PNG header bytes

        // When
        vm.attachImage(data)

        // Then
        #expect(vm.attachedImageData == data)
    }

    @Test("removeAttachedImage clears attachedImageData")
    func removeAttachedImageClearsData() throws {
        // Given
        let (vm, _, _) = makeViewModel()
        vm.attachImage(Data([0x00, 0x01]))

        // When
        vm.removeAttachedImage()

        // Then
        #expect(vm.attachedImageData == nil)
    }

    @Test("sendMessage with only image attached (no text) calls API")
    func sendMessageWithImageOnly() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.textDelta("Image description"), .done]
        let (vm, api, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        let imageData = Data(repeating: 0xFF, count: 16)
        vm.attachImage(imageData)
        vm.inputText = "" // no text

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(api.streamMessageCallCount == 1)
        // Content should include the image
        let contents = try #require(api.lastStreamContents)
        let hasImage = contents.contains { content in
            if case .image = content { return true }
            return false
        }
        #expect(hasImage == true)
    }

    @Test("sendMessage clears attachedImageData after send")
    func sendMessageClearsImage() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, _, _) = makeViewModel(streamEvents: [.done])
        let session = makeSession(in: context)
        vm.inputText = "Check image"
        vm.attachImage(Data(repeating: 0xAB, count: 8))

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(vm.attachedImageData == nil)
    }

    // MARK: - Error handling

    @Test("sendMessage sets errorMessage when API stream throws")
    func sendMessageHandlesStreamError() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        struct FakeError: Error, LocalizedError {
            var errorDescription: String? { "Network failure" }
        }
        let (vm, _, _) = makeViewModel(streamError: FakeError())
        let session = makeSession(in: context)
        vm.inputText = "Will fail"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(vm.errorMessage != nil)
        #expect(vm.isStreaming == false)
    }

    @Test("sendMessage clears prior errorMessage on new send attempt")
    func sendMessageClearsPriorError() throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let (vm, _, _) = makeViewModel(streamEvents: [.done])
        let session = makeSession(in: context)
        vm.inputText = "Retry"
        // Simulate a prior error
        vm.errorMessage = "Previous error"

        // When
        vm.sendMessage(session: session, modelContext: context)

        // Then — errorMessage cleared synchronously when the new send starts
        #expect(vm.errorMessage == nil)
    }

    // MARK: - Auto-title generation

    @Test("auto-title is set after first message when isAutoTitled is true")
    func autoTitleGeneratedOnFirstMessage() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.textDelta("Sure!"), .done]
        let (vm, _, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        #expect(session.isAutoTitled == true)
        #expect(session.title == "New Chat")
        vm.inputText = "Tell me something interesting about Swift"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(session.title != "New Chat")
        #expect(!session.title.isEmpty)
    }

    @Test("auto-title truncates long messages to 30 chars with ellipsis")
    func autoTitleTruncatesLongMessage() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.textDelta("Response"), .done]
        let (vm, _, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        // Message longer than 30 chars
        vm.inputText = "This is a very long message that exceeds thirty characters"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(session.title.hasSuffix("..."))
        // Base is 30 chars + "..." = 33
        #expect(session.title.count <= 33)
    }

    @Test("auto-title uses short message verbatim without ellipsis")
    func autoTitleShortMessageVerbatim() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.textDelta("Yes"), .done]
        let (vm, _, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        vm.inputText = "Hi"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(session.title == "Hi")
        #expect(!session.title.hasSuffix("..."))
    }

    // MARK: - System prompt selection

    @Test("sendMessage uses session systemPrompt when set")
    func sendMessageUsesCustomSystemPrompt() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.done]
        let (vm, api, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        session.systemPrompt = "Custom system prompt"
        vm.inputText = "Test"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(api.lastStreamSystemPrompt == "Custom system prompt")
    }

    @Test("sendMessage falls back to mode systemPrompt when session has no custom prompt")
    func sendMessageFallsBackToModeSystemPrompt() async throws {
        // Given
        let container = try makeContainer()
        let context = container.mainContext
        let events: [StreamEvent] = [.done]
        let (vm, api, _) = makeViewModel(streamEvents: events)
        let session = makeSession(in: context)
        session.systemPrompt = nil
        session.mode = .translate
        vm.inputText = "Translate this"

        // When
        vm.sendMessage(session: session, modelContext: context)
        try await Task.sleep(nanoseconds: 200_000_000)

        // Then
        #expect(api.lastStreamSystemPrompt == ResponseMode.translate.systemPrompt)
    }
}
