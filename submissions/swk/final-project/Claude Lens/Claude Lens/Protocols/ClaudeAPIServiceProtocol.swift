import Foundation

/// Events emitted during a streaming API response.
enum StreamEvent: Sendable {
    /// A text delta token from the assistant response.
    case textDelta(String)
    /// Token usage reported at message_start (input tokens).
    case inputTokens(Int)
    /// Token usage reported at message_delta (output tokens).
    case outputTokens(Int)
    /// The stream has completed successfully.
    case done
}

/// Content block sent in an API request message.
enum MessageContent: Sendable {
    case text(String)
    case image(data: Data, mediaType: String)
}

/// Abstracts all communication with the Anthropic Claude API.
/// Conforming types must be safe to call from @MainActor contexts via async.
protocol ClaudeAPIServiceProtocol: Sendable {

    /// Stream a message to the Claude API and receive events as they arrive.
    ///
    /// - Parameters:
    ///   - contents: The user's message content (text and/or images).
    ///   - conversationHistory: Previous messages in API-ready format.
    ///   - systemPrompt: The system prompt for this request.
    ///   - model: The Claude model identifier (e.g. "claude-sonnet-4-20250514").
    ///   - apiKey: The Anthropic API key.
    /// - Returns: An async throwing stream of `StreamEvent` values.
    /// - Throws: `ClaudeAPIError` on network or API-level failures.
    func streamMessage(
        contents: [MessageContent],
        conversationHistory: [[String: Any]],
        systemPrompt: String,
        model: String,
        apiKey: String
    ) -> AsyncThrowingStream<StreamEvent, Error>

    /// Validate that an API key is accepted by the Anthropic API.
    ///
    /// - Parameter apiKey: The key to validate.
    /// - Returns: `true` if the API returns a successful response.
    func validateAPIKey(_ apiKey: String) async -> Bool
}
