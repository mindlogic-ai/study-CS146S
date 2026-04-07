import Foundation
import SwiftData

@Model
final class Session {
    var id: UUID
    var title: String
    var isAutoTitled: Bool
    var systemPrompt: String?
    var responseMode: String
    var tokenCountInput: Int
    var tokenCountOutput: Int
    var createdAt: Date
    var updatedAt: Date
    @Relationship(deleteRule: .cascade, inverse: \Message.session)
    var messages: [Message]

    init(
        title: String = "New Chat",
        responseMode: ResponseMode = .chat,
        systemPrompt: String? = nil
    ) {
        self.id = UUID()
        self.title = title
        self.isAutoTitled = true
        self.systemPrompt = systemPrompt
        self.responseMode = responseMode.rawValue
        self.tokenCountInput = 0
        self.tokenCountOutput = 0
        self.createdAt = Date()
        self.updatedAt = Date()
        self.messages = []
    }

    var mode: ResponseMode {
        get { ResponseMode(rawValue: responseMode) ?? .chat }
        set { responseMode = newValue.rawValue }
    }

    var totalTokens: Int {
        tokenCountInput + tokenCountOutput
    }

    var sortedMessages: [Message] {
        messages.sorted { $0.createdAt < $1.createdAt }
    }
}
