import Foundation
import SwiftData

@Model
final class Message {
    var id: UUID
    var role: String
    var content: String
    var imageData: Data?
    var tokenCount: Int
    var createdAt: Date
    var session: Session?

    init(
        role: MessageRole,
        content: String,
        imageData: Data? = nil,
        tokenCount: Int = 0
    ) {
        self.id = UUID()
        self.role = role.rawValue
        self.content = content
        self.imageData = imageData
        self.tokenCount = tokenCount
        self.createdAt = Date()
    }

    var messageRole: MessageRole {
        MessageRole(rawValue: role) ?? .user
    }

    var hasImage: Bool {
        imageData != nil
    }
}

enum MessageRole: String, Codable {
    case user = "user"
    case assistant = "assistant"
}
