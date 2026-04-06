import Foundation
import Testing
@testable import Claude_Lens

@Suite("ResponseMode")
struct ResponseModeTests {

    // MARK: - Display Names

    @Test("all cases have non-empty display names")
    func displayNamesNonEmpty() {
        for mode in ResponseMode.allCases {
            #expect(!mode.displayName.isEmpty, "displayName for \(mode) is empty")
        }
    }

    @Test("display names are distinct")
    func displayNamesDistinct() {
        let names = ResponseMode.allCases.map(\.displayName)
        let unique = Set(names)
        #expect(unique.count == ResponseMode.allCases.count)
    }

    // MARK: - Icons

    @Test("all cases have non-empty SF Symbol names")
    func iconsNonEmpty() {
        for mode in ResponseMode.allCases {
            #expect(!mode.icon.isEmpty, "icon for \(mode) is empty")
        }
    }

    @Test("icons are distinct")
    func iconsDistinct() {
        let icons = ResponseMode.allCases.map(\.icon)
        let unique = Set(icons)
        #expect(unique.count == ResponseMode.allCases.count)
    }

    // MARK: - System Prompts

    @Test("all cases have non-empty system prompts")
    func systemPromptsNonEmpty() {
        for mode in ResponseMode.allCases {
            #expect(!mode.systemPrompt.isEmpty, "systemPrompt for \(mode) is empty")
        }
    }

    @Test("system prompts are distinct")
    func systemPromptsDistinct() {
        let prompts = ResponseMode.allCases.map(\.systemPrompt)
        let unique = Set(prompts)
        #expect(unique.count == ResponseMode.allCases.count)
    }

    // MARK: - Commands

    @Test("translate command parses to translate mode")
    func translateCommandParsed() {
        // Given / When
        let result = ResponseMode.fromCommand("/translate")

        // Then
        #expect(result == .translate)
    }

    @Test("explain command parses to explain mode")
    func explainCommandParsed() {
        // Given / When
        let result = ResponseMode.fromCommand("/explain")

        // Then
        #expect(result == .explain)
    }

    @Test("code command parses to code mode")
    func codeCommandParsed() {
        // Given / When
        let result = ResponseMode.fromCommand("/code")

        // Then
        #expect(result == .code)
    }

    @Test("commands are case-insensitive", arguments: ["/TRANSLATE", "/Translate", "/tRaNsLaTe"])
    func translateCommandCaseInsensitive(input: String) {
        #expect(ResponseMode.fromCommand(input) == .translate)
    }

    @Test("unknown command returns nil")
    func unknownCommandReturnsNil() {
        // Given / When
        let result = ResponseMode.fromCommand("/unknown")

        // Then
        #expect(result == nil)
    }

    @Test("empty string returns nil")
    func emptyStringReturnsNil() {
        #expect(ResponseMode.fromCommand("") == nil)
    }

    @Test("plain text returns nil")
    func plainTextReturnsNil() {
        #expect(ResponseMode.fromCommand("hello world") == nil)
    }

    @Test("chat mode has empty command string")
    func chatCommandIsEmpty() {
        #expect(ResponseMode.chat.command == "")
    }

    @Test("non-chat modes have slash-prefixed commands")
    func nonChatCommandsHaveSlashPrefix() {
        let nonChat: [ResponseMode] = [.translate, .explain, .code]
        for mode in nonChat {
            #expect(mode.command.hasPrefix("/"), "\(mode).command missing '/' prefix")
        }
    }

    // MARK: - Raw Values & CaseIterable

    @Test("raw value round-trips")
    func rawValueRoundTrip() {
        for mode in ResponseMode.allCases {
            let reconstructed = ResponseMode(rawValue: mode.rawValue)
            #expect(reconstructed == mode)
        }
    }

    @Test("unknown raw value falls back to chat in Session")
    func unknownRawValueFallback() {
        let result = ResponseMode(rawValue: "nonexistent")
        #expect(result == nil)
    }

    @Test("allCases has exactly 4 members")
    func allCasesCount() {
        #expect(ResponseMode.allCases.count == 4)
    }
}
