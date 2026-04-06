import Foundation

enum ResponseMode: String, CaseIterable, Codable {
    case chat = "chat"
    case translate = "translate"
    case explain = "explain"
    case code = "code"

    var displayName: String {
        switch self {
        case .chat: return "자유 질문"
        case .translate: return "번역"
        case .explain: return "설명"
        case .code: return "코드 설명"
        }
    }

    var icon: String {
        switch self {
        case .chat: return "bubble.left.and.bubble.right"
        case .translate: return "character.book.closed"
        case .explain: return "lightbulb"
        case .code: return "chevron.left.forwardslash.chevron.right"
        }
    }

    var systemPrompt: String {
        switch self {
        case .translate:
            return """
            You are a translator. Detect the language of the input text. \
            If Korean, translate to English. If English, translate to Korean. \
            If other, translate to Korean. Output only the translation.
            """
        case .explain:
            return """
            You are an expert explainer. Analyze the given text or image \
            and provide a clear, concise explanation. Use bullet points for key \
            points. Respond in the same language as the input.
            """
        case .code:
            return """
            You are a senior software engineer. Analyze the given code and \
            explain: 1) What it does, 2) How it works, 3) Any potential issues. \
            Include code examples when helpful.
            """
        case .chat:
            return """
            You are a helpful assistant. Respond naturally to the user's \
            message. When an image is provided, describe and analyze its content.
            """
        }
    }

    var command: String {
        switch self {
        case .chat: return ""
        case .translate: return "/translate"
        case .explain: return "/explain"
        case .code: return "/code"
        }
    }

    static func fromCommand(_ text: String) -> ResponseMode? {
        switch text.lowercased().trimmingCharacters(in: .whitespaces) {
        case "/translate": return .translate
        case "/explain": return .explain
        case "/code": return .code
        default: return nil
        }
    }
}
