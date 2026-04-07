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

    // --- Throttle state for streaming UI updates ---
    private var lastFlushTime: ContinuousClock.Instant = .now
    private let flushInterval: Duration = .milliseconds(50)

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
        assistantMessage.isStreaming = true

        let model = selectedModel
            ?? UserDefaults.standard.string(forKey: "selectedModel")
            ?? "claude-sonnet-4-20250514"

        Task {
            do {
                try await streamAndHandleToolUse(
                    contents: contents,
                    conversationHistory: history,
                    systemPrompt: systemPrompt,
                    model: model,
                    apiKey: apiKey,
                    session: session,
                    userMessage: userMessage,
                    assistantMessage: assistantMessage
                )

                // Auto-title on first message
                if session.isAutoTitled && session.messages.count <= 2 {
                    generateAutoTitle(for: session, firstMessage: capturedText)
                }
                assistantMessage.isStreaming = false
                try? modelContext.save()
            } catch {
                errorMessage = error.localizedDescription
                assistantMessage.content = currentResponse.isEmpty
                    ? "Error: \(error.localizedDescription)"
                    : currentResponse
                assistantMessage.isStreaming = false
                try? modelContext.save()
            }

            isStreaming = false
        }
    }

    // MARK: - Tool Use Streaming

    private func streamAndHandleToolUse(
        contents: [MessageContent],
        conversationHistory: [[String: Any]],
        systemPrompt: String,
        model: String,
        apiKey: String,
        session: Session,
        userMessage: Message,
        assistantMessage: Message
    ) async throws {
        let stream = apiService.streamMessage(
            contents: contents,
            conversationHistory: conversationHistory,
            systemPrompt: systemPrompt,
            model: model,
            apiKey: apiKey
        )

        var pendingToolUse: (id: String, name: String, inputJSON: String)?

        lastFlushTime = .now
        for try await event in stream {
            switch event {
            case .textDelta(let token):
                currentResponse += token
                // Throttle SwiftData model updates to avoid CPU spike
                let now = ContinuousClock.Instant.now
                if now - lastFlushTime >= flushInterval {
                    assistantMessage.content = currentResponse
                    lastFlushTime = now
                }
            case .inputTokens(let count):
                session.tokenCountInput += count
                userMessage.tokenCount = count
            case .outputTokens(let count):
                session.tokenCountOutput += count
                assistantMessage.tokenCount = count
            case .toolUse(let id, let name, let inputJSON):
                pendingToolUse = (id: id, name: name, inputJSON: inputJSON)
            case .done:
                break
            }
        }
        // Final flush to ensure all content is displayed
        assistantMessage.content = currentResponse

        guard let toolUse = pendingToolUse,
              ["fetch_url", "web_search", "dictionary"].contains(toolUse.name)
        else { return }

        // Parse tool input JSON
        guard let inputData = toolUse.inputJSON.data(using: .utf8),
              let inputDict = try? JSONSerialization.jsonObject(with: inputData) as? [String: Any]
        else { return }

        let fetchedText: String

        if toolUse.name == "fetch_url" {
            guard let urlString = inputDict["url"] as? String,
                  let url = URL(string: urlString)
            else { return }
            assistantMessage.content = currentResponse.isEmpty
                ? "Fetching \(urlString)..."
                : currentResponse + "\n\n*Fetching \(urlString)...*"
            fetchedText = await fetchURLContent(url: url)
        } else if toolUse.name == "web_search" {
            guard let query = inputDict["query"] as? String else { return }
            assistantMessage.content = currentResponse.isEmpty
                ? "Searching: \(query)..."
                : currentResponse + "\n\n*Searching: \(query)...*"
            fetchedText = await webSearch(query: query)
        } else {
            guard let word = inputDict["word"] as? String else { return }
            assistantMessage.content = currentResponse.isEmpty
                ? "Looking up: \(word)..."
                : currentResponse + "\n\n*Looking up: \(word)...*"
            fetchedText = await dictionaryLookup(word: word)
        }

        // Build updated messages with tool_use block and tool_result
        var updatedHistory = conversationHistory

        // Add the user message
        var userContent: [[String: Any]] = []
        for content in contents {
            switch content {
            case .text(let text):
                userContent.append(["type": "text", "text": text])
            case .image(let data, let mediaType):
                userContent.append([
                    "type": "image",
                    "source": ["type": "base64", "media_type": mediaType, "data": data.base64EncodedString()]
                ])
            }
        }
        updatedHistory.append(["role": "user", "content": userContent])

        // Add assistant's tool_use message
        let assistantToolUseContent: [[String: Any]] = [
            [
                "type": "tool_use",
                "id": toolUse.id,
                "name": toolUse.name,
                "input": inputDict
            ]
        ]
        updatedHistory.append(["role": "assistant", "content": assistantToolUseContent])

        // Add tool_result message
        let toolResultContent: [[String: Any]] = [
            [
                "type": "tool_result",
                "tool_use_id": toolUse.id,
                "content": fetchedText
            ]
        ]
        updatedHistory.append(["role": "user", "content": toolResultContent])

        // Reset response and stream again with tool result
        currentResponse = ""
        assistantMessage.content = ""

        let followUpStream = apiService.streamMessage(
            contents: [],
            conversationHistory: updatedHistory,
            systemPrompt: systemPrompt,
            model: model,
            apiKey: apiKey
        )

        lastFlushTime = .now
        for try await event in followUpStream {
            switch event {
            case .textDelta(let token):
                currentResponse += token
                let now = ContinuousClock.Instant.now
                if now - lastFlushTime >= flushInterval {
                    assistantMessage.content = currentResponse
                    lastFlushTime = now
                }
            case .outputTokens(let count):
                session.tokenCountOutput += count
                assistantMessage.tokenCount = count
            case .inputTokens(let count):
                session.tokenCountInput += count
            case .toolUse, .done:
                break
            }
        }
        // Final flush
        assistantMessage.content = currentResponse
    }

    private func dictionaryLookup(word: String) async -> String {
        do {
            let encoded = word.addingPercentEncoding(withAllowedCharacters: .urlPathAllowed) ?? word
            guard let url = URL(string: "https://api.dictionaryapi.dev/api/v2/entries/en/\(encoded)") else {
                return "Failed to build dictionary URL."
            }
            var request = URLRequest(url: url)
            request.timeoutInterval = 10
            let (data, response) = try await URLSession.shared.data(for: request)
            let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 0
            if statusCode == 404 {
                return "Word '\(word)' not found in dictionary."
            }
            guard let entries = try? JSONSerialization.jsonObject(with: data) as? [[String: Any]],
                  let entry = entries.first
            else { return "Failed to parse dictionary response." }

            var result = "Word: \(word)\n"

            // Phonetics
            if let phonetics = entry["phonetics"] as? [[String: Any]] {
                let texts = phonetics.compactMap { $0["text"] as? String }.filter { !$0.isEmpty }
                if let phonetic = texts.first {
                    result += "Pronunciation: \(phonetic)\n"
                }
            }

            // Meanings
            if let meanings = entry["meanings"] as? [[String: Any]] {
                for meaning in meanings.prefix(3) {
                    let partOfSpeech = meaning["partOfSpeech"] as? String ?? ""
                    result += "\n[\(partOfSpeech)]\n"
                    if let definitions = meaning["definitions"] as? [[String: Any]] {
                        for (i, def) in definitions.prefix(3).enumerated() {
                            let definition = def["definition"] as? String ?? ""
                            result += "  \(i + 1). \(definition)\n"
                            if let example = def["example"] as? String {
                                result += "     Example: \"\(example)\"\n"
                            }
                        }
                    }
                    if let synonyms = meaning["synonyms"] as? [String], !synonyms.isEmpty {
                        result += "  Synonyms: \(synonyms.prefix(5).joined(separator: ", "))\n"
                    }
                }
            }

            return result
        } catch {
            return "Dictionary lookup failed: \(error.localizedDescription)"
        }
    }

    private func webSearch(query: String) async -> String {
        do {
            let encoded = query.addingPercentEncoding(withAllowedCharacters: .urlQueryAllowed) ?? query
            guard let url = URL(string: "https://html.duckduckgo.com/html/?q=\(encoded)") else {
                return "Failed to build search URL."
            }
            var request = URLRequest(url: url)
            request.setValue(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
                forHTTPHeaderField: "User-Agent"
            )
            request.timeoutInterval = 15
            let (data, _) = try await URLSession.shared.data(for: request)
            guard let html = String(data: data, encoding: .utf8) else {
                return "Failed to decode search results."
            }
            return parseSearchResults(html: html)
        } catch {
            return "Search failed: \(error.localizedDescription)"
        }
    }

    private func parseSearchResults(html: String) -> String {
        var results: [String] = []
        // Extract result blocks: <a class="result__a" href="...">title</a> and <a class="result__snippet">snippet</a>
        let titlePattern = "<a[^>]*class=\"result__a\"[^>]*href=\"([^\"]*)\"[^>]*>(.*?)</a>"
        let snippetPattern = "<a[^>]*class=\"result__snippet\"[^>]*>(.*?)</a>"

        let titleRegex = try? NSRegularExpression(pattern: titlePattern, options: [.caseInsensitive, .dotMatchesLineSeparators])
        let snippetRegex = try? NSRegularExpression(pattern: snippetPattern, options: [.caseInsensitive, .dotMatchesLineSeparators])

        let nsHTML = html as NSString
        let titleMatches = titleRegex?.matches(in: html, range: NSRange(location: 0, length: nsHTML.length)) ?? []
        let snippetMatches = snippetRegex?.matches(in: html, range: NSRange(location: 0, length: nsHTML.length)) ?? []

        for (i, titleMatch) in titleMatches.prefix(8).enumerated() {
            let url = nsHTML.substring(with: titleMatch.range(at: 1))
                .replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
            let title = nsHTML.substring(with: titleMatch.range(at: 2))
                .replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
            var snippet = ""
            if i < snippetMatches.count {
                snippet = nsHTML.substring(with: snippetMatches[i].range(at: 1))
                    .replacingOccurrences(of: "<[^>]+>", with: "", options: .regularExpression)
            }
            results.append("\(i + 1). \(title)\n   URL: \(url)\n   \(snippet)")
        }

        return results.isEmpty ? "No search results found." : results.joined(separator: "\n\n")
    }

    private func fetchURLContent(url: URL) async -> String {
        do {
            var request = URLRequest(url: url)
            request.setValue(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                forHTTPHeaderField: "User-Agent"
            )
            request.timeoutInterval = 15
            let (data, _) = try await URLSession.shared.data(for: request)
            guard let html = String(data: data, encoding: .utf8) ?? String(data: data, encoding: .isoLatin1) else {
                return "Failed to decode page content."
            }
            let text = stripHTML(html)
            let truncated = String(text.prefix(10000))
            return truncated.isEmpty ? "No readable text content found." : truncated
        } catch {
            return "Failed to fetch URL: \(error.localizedDescription)"
        }
    }

    private func stripHTML(_ html: String) -> String {
        // Remove script and style blocks entirely
        var result = html
        let blockPatterns = ["<script[^>]*>[\\s\\S]*?</script>", "<style[^>]*>[\\s\\S]*?</style>"]
        for pattern in blockPatterns {
            result = result.replacingOccurrences(of: pattern, with: "", options: [.regularExpression, .caseInsensitive])
        }
        // Strip remaining tags
        result = result.replacingOccurrences(of: "<[^>]+>", with: " ", options: .regularExpression)
        // Decode common HTML entities
        result = result
            .replacingOccurrences(of: "&amp;", with: "&")
            .replacingOccurrences(of: "&lt;", with: "<")
            .replacingOccurrences(of: "&gt;", with: ">")
            .replacingOccurrences(of: "&quot;", with: "\"")
            .replacingOccurrences(of: "&#39;", with: "'")
            .replacingOccurrences(of: "&nbsp;", with: " ")
        // Collapse whitespace
        let components = result.components(separatedBy: .whitespacesAndNewlines).filter { !$0.isEmpty }
        return components.joined(separator: " ")
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
