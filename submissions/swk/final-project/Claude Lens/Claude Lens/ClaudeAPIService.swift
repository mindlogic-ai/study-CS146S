import Foundation

struct ClaudeAPIError: Error, LocalizedError {
    let message: String
    var errorDescription: String? { message }
}

/// Concrete implementation of ClaudeAPIServiceProtocol.
/// Not @MainActor — network I/O runs on background threads.
/// The AsyncThrowingStream it returns is consumed on @MainActor by ViewModels.
final class ClaudeAPIService: ClaudeAPIServiceProtocol {

    private let baseURL = "https://api.anthropic.com/v1/messages"
    private let apiVersion = "2023-06-01"

    init() {}

    func streamMessage(
        contents: [MessageContent],
        conversationHistory: [[String: Any]],
        systemPrompt: String,
        model: String,
        apiKey: String
    ) -> AsyncThrowingStream<StreamEvent, Error> {
        AsyncThrowingStream { continuation in
            Task {
                do {
                    var userContent: [[String: Any]] = []
                    for content in contents {
                        switch content {
                        case .text(let text):
                            userContent.append(["type": "text", "text": text])
                        case .image(let data, let mediaType):
                            userContent.append([
                                "type": "image",
                                "source": [
                                    "type": "base64",
                                    "media_type": mediaType,
                                    "data": data.base64EncodedString()
                                ]
                            ])
                        }
                    }

                    var messages = conversationHistory
                    if !userContent.isEmpty {
                        messages.append(["role": "user", "content": userContent])
                    }

                    let tools: [[String: Any]] = [
                        [
                            "name": "fetch_url",
                            "description": "Fetch the content of a web page URL. Use this when the user provides a URL or asks about web content.",
                            "input_schema": [
                                "type": "object",
                                "properties": [
                                    "url": [
                                        "type": "string",
                                        "description": "The URL to fetch"
                                    ]
                                ],
                                "required": ["url"]
                            ]
                        ],
                        [
                            "name": "web_search",
                            "description": "Search the web for information. Use this when the user asks a question that requires up-to-date information, facts you're unsure about, or when they explicitly ask to search.",
                            "input_schema": [
                                "type": "object",
                                "properties": [
                                    "query": [
                                        "type": "string",
                                        "description": "The search query"
                                    ]
                                ],
                                "required": ["query"]
                            ]
                        ],
                        [
                            "name": "dictionary",
                            "description": "Look up a word definition, pronunciation, and usage examples. Use this when the user asks about the meaning of a word, how to use it, or wants a dictionary lookup.",
                            "input_schema": [
                                "type": "object",
                                "properties": [
                                    "word": [
                                        "type": "string",
                                        "description": "The word to look up"
                                    ],
                                    "language": [
                                        "type": "string",
                                        "description": "Language code: 'en' for English (default)",
                                        "enum": ["en"]
                                    ]
                                ],
                                "required": ["word"]
                            ]
                        ]
                    ]

                    let body: [String: Any] = [
                        "model": model,
                        "max_tokens": 4096,
                        "system": systemPrompt,
                        "stream": true,
                        "tools": tools,
                        "messages": messages
                    ]

                    guard let url = URL(string: baseURL),
                          let jsonData = try? JSONSerialization.data(withJSONObject: body)
                    else {
                        throw ClaudeAPIError(message: "Failed to create request")
                    }

                    var request = URLRequest(url: url)
                    request.httpMethod = "POST"
                    request.setValue("application/json", forHTTPHeaderField: "Content-Type")
                    request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
                    request.setValue(apiVersion, forHTTPHeaderField: "anthropic-version")
                    request.httpBody = jsonData

                    let (bytes, response) = try await URLSession.shared.bytes(for: request)
                    guard let httpResponse = response as? HTTPURLResponse else {
                        throw ClaudeAPIError(message: "Invalid response")
                    }

                    if httpResponse.statusCode != 200 {
                        var errorBody = ""
                        for try await line in bytes.lines {
                            errorBody += line
                        }
                        throw ClaudeAPIError(
                            message: "API error (\(httpResponse.statusCode)): \(errorBody)"
                        )
                    }

                    // Track tool_use block accumulation
                    var currentToolUseId: String?
                    var currentToolUseName: String?
                    var currentToolUseInputJSON = ""
                    var isAccumulatingToolInput = false

                    for try await line in bytes.lines {
                        guard line.hasPrefix("data: ") else { continue }
                        let jsonStr = String(line.dropFirst(6))
                        if jsonStr == "[DONE]" { break }

                        guard let data = jsonStr.data(using: .utf8),
                              let json = try? JSONSerialization.jsonObject(with: data) as? [String: Any]
                        else { continue }

                        let eventType = json["type"] as? String ?? ""

                        if eventType == "content_block_start",
                           let block = json["content_block"] as? [String: Any],
                           let blockType = block["type"] as? String
                        {
                            if blockType == "tool_use" {
                                currentToolUseId = block["id"] as? String
                                currentToolUseName = block["name"] as? String
                                currentToolUseInputJSON = ""
                                isAccumulatingToolInput = true
                            } else {
                                isAccumulatingToolInput = false
                            }
                        }

                        if eventType == "content_block_delta",
                           let delta = json["delta"] as? [String: Any]
                        {
                            let deltaType = delta["type"] as? String ?? ""
                            if deltaType == "text_delta", let text = delta["text"] as? String {
                                continuation.yield(.textDelta(text))
                            } else if deltaType == "input_json_delta",
                                      let partial = delta["partial_json"] as? String,
                                      isAccumulatingToolInput
                            {
                                currentToolUseInputJSON += partial
                            }
                        }

                        if eventType == "content_block_stop", isAccumulatingToolInput {
                            if let id = currentToolUseId, let name = currentToolUseName {
                                continuation.yield(.toolUse(id: id, name: name, inputJSON: currentToolUseInputJSON))
                            }
                            isAccumulatingToolInput = false
                            currentToolUseId = nil
                            currentToolUseName = nil
                            currentToolUseInputJSON = ""
                        }

                        if eventType == "message_start",
                           let message = json["message"] as? [String: Any],
                           let usageDict = message["usage"] as? [String: Any],
                           let inputTokens = usageDict["input_tokens"] as? Int
                        {
                            continuation.yield(.inputTokens(inputTokens))
                        }

                        if eventType == "message_delta",
                           let usageDict = json["usage"] as? [String: Any],
                           let outputTokens = usageDict["output_tokens"] as? Int
                        {
                            continuation.yield(.outputTokens(outputTokens))
                        }
                    }

                    continuation.yield(.done)
                    continuation.finish()
                } catch {
                    continuation.finish(throwing: error)
                }
            }
        }
    }

    func validateAPIKey(_ apiKey: String) async -> Bool {
        guard let url = URL(string: baseURL) else { return false }
        var request = URLRequest(url: url)
        request.httpMethod = "POST"
        request.setValue("application/json", forHTTPHeaderField: "Content-Type")
        request.setValue(apiKey, forHTTPHeaderField: "x-api-key")
        request.setValue(apiVersion, forHTTPHeaderField: "anthropic-version")

        let body: [String: Any] = [
            "model": "claude-haiku-4-5-20251001",
            "max_tokens": 1,
            "messages": [["role": "user", "content": "hi"]]
        ]
        request.httpBody = try? JSONSerialization.data(withJSONObject: body)

        do {
            let (_, response) = try await URLSession.shared.data(for: request)
            let statusCode = (response as? HTTPURLResponse)?.statusCode ?? 0
            // 200 = valid, 429 = rate limited but key is valid, 401 = invalid key
            return statusCode == 200 || statusCode == 429
        } catch {
            return false
        }
    }
}
