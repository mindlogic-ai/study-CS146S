import Foundation
import SwiftData

@MainActor
@Observable
final class ChatViewModel {
    // --- Published State ---
    var currentResponse = ""
    var isStreaming = false
    var errorMessage: String?
    var inputText = ""
    var attachedImageData: Data?

    // --- Dependencies (injected via init) ---
    private let apiService: ClaudeAPIServiceProtocol
    private let keychainService: KeychainServiceProtocol

    init(
        apiService: ClaudeAPIServiceProtocol,
        keychainService: KeychainServiceProtocol
    ) {
        self.apiService = apiService
        self.keychainService = keychainService
    }

    // --- Methods ---

    func sendMessage(session: Session, modelContext: ModelContext, selectedModel: String? = nil) {
        let text = inputText.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !text.isEmpty || attachedImageData != nil else { return }

        // Check for mode command
        if let mode = ResponseMode.fromCommand(text) {
            session.mode = mode
            session.updatedAt = Date()
            inputText = ""
            return
        }

        guard let apiKey = keychainService.load() else {
            errorMessage = "API key not found. Please set your API key in Settings."
            return
        }

        // Create user message
        let userMessage = Message(
            role: .user,
            content: text,
            imageData: attachedImageData
        )
        userMessage.session = session
        session.messages.append(userMessage)
        session.updatedAt = Date()
        modelContext.insert(userMessage)

        // Create placeholder assistant message
        let assistantMessage = Message(role: .assistant, content: "")
        assistantMessage.session = session
        session.messages.append(assistantMessage)
        modelContext.insert(assistantMessage)

        // Build conversation history (excluding the empty assistant placeholder)
        let history = buildConversationHistory(session: session, excluding: assistantMessage)

        // Build content array
        var contents: [MessageContent] = []
        if let imageData = attachedImageData {
            contents.append(.image(data: imageData, mediaType: "image/png"))
        }
        if !text.isEmpty {
            contents.append(.text(text))
        } else if attachedImageData != nil {
            contents.append(.text("이 이미지를 설명해주세요."))
        }

        let systemPrompt = session.systemPrompt ?? session.mode.systemPrompt
        let capturedText = text
        inputText = ""
        attachedImageData = nil
        currentResponse = ""
        isStreaming = true
        errorMessage = nil

        let model = selectedModel
            ?? UserDefaults.standard.string(forKey: "selectedModel")
            ?? "claude-sonnet-4-20250514"

        Task {
            do {
                let stream = apiService.streamMessage(
                    contents: contents,
                    conversationHistory: history,
                    systemPrompt: systemPrompt,
                    model: model,
                    apiKey: apiKey
                )

                for try await event in stream {
                    switch event {
                    case .textDelta(let token):
                        currentResponse += token
                        assistantMessage.content = currentResponse
                    case .inputTokens(let count):
                        session.tokenCountInput += count
                        userMessage.tokenCount = count
                    case .outputTokens(let count):
                        session.tokenCountOutput += count
                        assistantMessage.tokenCount = count
                    case .done:
                        break
                    }
                }

                // Auto-title on first message
                if session.isAutoTitled && session.messages.count <= 2 {
                    generateAutoTitle(for: session, firstMessage: capturedText)
                }
                try? modelContext.save()
            } catch {
                errorMessage = error.localizedDescription
                assistantMessage.content = "Error: \(error.localizedDescription)"
                try? modelContext.save()
            }

            isStreaming = false
        }
    }

    func attachImage(_ data: Data) {
        attachedImageData = data
    }

    func removeAttachedImage() {
        attachedImageData = nil
    }

    // MARK: - Private helpers

    private func buildConversationHistory(
        session: Session,
        excluding: Message
    ) -> [[String: Any]] {
        session.sortedMessages
            .filter { $0.id != excluding.id }
            .compactMap { msg -> [String: Any]? in
                guard !msg.content.isEmpty else { return nil }
                var content: [[String: Any]] = []
                if let imageData = msg.imageData {
                    content.append([
                        "type": "image",
                        "source": [
                            "type": "base64",
                            "media_type": "image/png",
                            "data": imageData.base64EncodedString()
                        ]
                    ])
                }
                if !msg.content.isEmpty {
                    content.append(["type": "text", "text": msg.content])
                }
                return ["role": msg.role, "content": content]
            }
    }

    private func generateAutoTitle(for session: Session, firstMessage: String) {
        let truncated = String(firstMessage.prefix(100))
        if truncated.count > 30 {
            session.title = String(truncated.prefix(30)) + "..."
        } else if !truncated.isEmpty {
            session.title = truncated
        }
    }
}
