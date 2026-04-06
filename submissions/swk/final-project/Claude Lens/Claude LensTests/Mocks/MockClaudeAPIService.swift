import Foundation
@testable import Claude_Lens

/// In-memory mock for ClaudeAPIServiceProtocol.
/// Configure `streamMessageResult` and `validateKeyResult` before each test.
final class MockClaudeAPIService: ClaudeAPIServiceProtocol, @unchecked Sendable {

    // --- Configuration ---
    var streamMessageResult: [StreamEvent] = []
    var validateKeyResult: Bool = true
    var shouldThrowOnStream: Error? = nil

    // --- Call Tracking ---
    var streamMessageCallCount = 0
    var validateAPIKeyCallCount = 0
    var lastStreamContents: [MessageContent]?
    var lastStreamSystemPrompt: String?
    var lastStreamModel: String?
    var lastValidatedKey: String?

    func streamMessage(
        contents: [MessageContent],
        conversationHistory: [[String: Any]],
        systemPrompt: String,
        model: String,
        apiKey: String
    ) -> AsyncThrowingStream<StreamEvent, Error> {
        streamMessageCallCount += 1
        lastStreamContents = contents
        lastStreamSystemPrompt = systemPrompt
        lastStreamModel = model

        let events = streamMessageResult
        let error = shouldThrowOnStream

        return AsyncThrowingStream { continuation in
            if let error {
                continuation.finish(throwing: error)
                return
            }
            for event in events {
                continuation.yield(event)
            }
            continuation.finish()
        }
    }

    func validateAPIKey(_ apiKey: String) async -> Bool {
        validateAPIKeyCallCount += 1
        lastValidatedKey = apiKey
        return validateKeyResult
    }
}
