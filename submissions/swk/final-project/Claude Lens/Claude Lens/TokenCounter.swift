import Foundation

enum TokenCounter {
    static func estimateTokens(for text: String) -> Int {
        // Rough estimation: ~4 characters per token for English, ~2 for Korean
        let charCount = text.count
        let koreanCount = text.unicodeScalars.filter { $0.value >= 0xAC00 && $0.value <= 0xD7AF }.count
        let nonKoreanCount = charCount - koreanCount
        return (koreanCount / 2) + (nonKoreanCount / 4) + 1
    }
}
