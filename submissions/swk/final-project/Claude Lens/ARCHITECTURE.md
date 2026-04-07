# ARCHITECTURE.md — Claude Lens

## 1. Architecture Overview

Claude Lens follows **MVVM** (Model-View-ViewModel) with **Protocol-based Dependency Injection**. Every service dependency flows through a protocol interface so that ViewModels can be tested with mocks and concrete implementations can be swapped without changing business logic.

```
┌─────────────────────────────────────────────────────────────────┐
│                        SwiftUI Views                            │
│  ContentView, ChatView, SidebarView, InputBarView,              │
│  MessageBubbleView, OnboardingView, SettingsView                │
│                                                                 │
│  Rules:                                                         │
│  - Thin, declarative, no business logic                         │
│  - Depend ONLY on ViewModels (via @State / @Bindable)           │
│  - Access SwiftData via @Environment(\.modelContext) and @Query  │
│  - All run on @MainActor (implicit for SwiftUI views)           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ observes
┌──────────────────────────▼──────────────────────────────────────┐
│                        ViewModels                               │
│  ChatViewModel, SessionListViewModel, SettingsViewModel         │
│                                                                 │
│  Rules:                                                         │
│  - @MainActor @Observable classes                               │
│  - Own all business logic, state mutations, API orchestration   │
│  - Depend on Services ONLY through Protocol interfaces          │
│  - Receive ModelContext as method parameter (not stored)         │
│  - NEVER import SwiftUI (import Foundation + SwiftData only)    │
└───────────┬─────────────────────────────────┬───────────────────┘
            │ calls via protocol              │ reads/writes
┌───────────▼───────────────┐   ┌─────────────▼───────────────────┐
│        Services            │   │          Models (SwiftData)     │
│                            │   │                                 │
│  ClaudeAPIService          │   │  Session                        │
│  KeychainService           │   │  Message                        │
│  ClipboardService          │   │  ResponseMode (enum)            │
│  HotkeyService             │   │                                 │
│  TextSelectionService      │   │  Rules:                         │
│  ScreenCaptureService      │   │  - Pure data, @Model classes    │
│                            │   │  - No service/VM imports        │
│  Rules:                    │   │  - Relationships, computed props │
│  - Each has a Protocol     │   │  - No UI dependencies           │
│  - Concrete is final class │   └─────────────────────────────────┘
│  - Injected, not .shared   │
└────────────────────────────┘
```

### Data Flow — Quick Capture (Text)

```
User drags text → ⌘+⇧+L
        │
        ▼
  HotkeyService (Carbon API)
  fires onTextCapture callback
        │
        ▼
  AppCoordinator (App entry point)
    ├── TextSelectionService.captureSelectedText()
    │     ├── ClipboardService.backup()
    │     ├── CGEvent ⌘+C simulation
    │     ├── ClipboardService.readText()
    │     └── ClipboardService.restore()
    │
    ├── Sets AppState.pendingCapturedText
    └── Shows overlay window
              │
              ▼
        ChatView.onAppear
          └── ChatViewModel consumes pending text
                └── inputText = capturedText
                      │
                      ▼ (user presses Enter)
                ChatViewModel.sendMessage()
                  ├── Creates Message models (SwiftData)
                  ├── ClaudeAPIService.streamMessage()
                  │     └── AsyncThrowingStream<StreamEvent>
                  └── Updates assistant Message.content on each token
```

---

## 2. Protocol Definitions

All protocols live in `Claude Lens/Protocols/`. Each file contains one protocol.

### 2.1 ClaudeAPIServiceProtocol

```swift
// Protocols/ClaudeAPIServiceProtocol.swift

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
```

### 2.2 KeychainServiceProtocol

```swift
// Protocols/KeychainServiceProtocol.swift

import Foundation

/// Abstracts secure credential storage (Keychain on macOS).
protocol KeychainServiceProtocol: Sendable {

    /// Save an API key to secure storage, replacing any existing value.
    /// - Returns: `true` if the key was saved successfully.
    @discardableResult
    func save(apiKey: String) -> Bool

    /// Load the stored API key.
    /// - Returns: The API key string, or `nil` if none is stored.
    func load() -> String?

    /// Delete the stored API key.
    /// - Returns: `true` if deletion succeeded or key did not exist.
    @discardableResult
    func delete() -> Bool

    /// Whether an API key currently exists in storage.
    var hasKey: Bool { get }

    /// A masked representation of the stored key for UI display.
    /// - Returns: e.g. "sk-ant-...xxxx", or `nil` if no key is stored.
    func maskedKey() -> String?
}
```

### 2.3 ClipboardServiceProtocol

```swift
// Protocols/ClipboardServiceProtocol.swift

import Foundation

/// Abstracts macOS pasteboard (NSPasteboard) operations.
/// Must be called on @MainActor since NSPasteboard is main-thread bound.
@MainActor
protocol ClipboardServiceProtocol {

    /// Read the current text content from the system pasteboard.
    func readText() -> String?

    /// Read image data (PNG) from the system pasteboard.
    func readImage() -> Data?

    /// Whether the pasteboard currently contains image data.
    func hasImage() -> Bool

    /// Write text to the system pasteboard, replacing current contents.
    func writeText(_ text: String)

    /// Snapshot the current pasteboard contents for later restoration.
    /// Returns opaque data that can be passed to `restore(from:)`.
    func backup() -> Data?

    /// Restore pasteboard contents from a previous `backup()` snapshot.
    func restore(from backupData: Data?)
}
```

### 2.4 HotkeyServiceProtocol

```swift
// Protocols/HotkeyServiceProtocol.swift

import Foundation

/// Identifies a registered hotkey for unregistration.
struct HotkeyRegistration: Sendable {
    let id: UInt32
}

/// Abstracts global hotkey registration using the Carbon Event API.
/// Must be called on @MainActor (Carbon events dispatch on the main thread).
@MainActor
protocol HotkeyServiceProtocol {

    /// Register all configured global hotkeys.
    /// Sets up the Carbon event handler and registers individual key combos.
    func register()

    /// Unregister all global hotkeys and tear down the event handler.
    func unregister()

    /// Callback invoked when the text capture hotkey (default: ⌘+⇧+L) is pressed.
    var onTextCapture: (() -> Void)? { get set }

    /// Callback invoked when the screenshot capture hotkey (default: ⌘+⇧+K) is pressed.
    var onScreenshotCapture: (() -> Void)? { get set }
}
```

### 2.5 TextSelectionServiceProtocol

```swift
// Protocols/TextSelectionServiceProtocol.swift

import Foundation

/// Abstracts the capture of currently-selected text from the active application.
/// Requires macOS Accessibility permission.
@MainActor
protocol TextSelectionServiceProtocol {

    /// Capture the currently selected text in the frontmost application.
    ///
    /// Implementation:
    /// 1. Backup clipboard
    /// 2. Simulate ⌘+C via CGEvent
    /// 3. Wait for clipboard update (~80ms)
    /// 4. Read text from clipboard
    /// 5. Restore original clipboard
    ///
    /// - Returns: The selected text, or `nil` if nothing was selected
    ///   or accessibility permission is not granted.
    func captureSelectedText() async -> String?

    /// Whether the Accessibility permission has been granted by the user.
    var isAccessibilityGranted: Bool { get }

    /// Prompt the user to grant Accessibility permission via System Settings.
    func requestAccessibility()
}
```

### 2.6 ScreenCaptureServiceProtocol

```swift
// Protocols/ScreenCaptureServiceProtocol.swift

import Foundation
import CoreGraphics

/// Abstracts screen region capture using ScreenCaptureKit.
/// Requires macOS Screen Recording permission.
@MainActor
protocol ScreenCaptureServiceProtocol {

    /// Capture a specific screen region as PNG image data.
    ///
    /// - Parameter rect: The screen rectangle to capture (in screen coordinates).
    /// - Returns: PNG-encoded image data, or `nil` on failure or permission denial.
    func captureScreenRegion(rect: CGRect) async -> Data?

    /// Whether the Screen Recording permission has been granted.
    var isScreenCaptureGranted: Bool { get }

    /// Request Screen Recording permission from the user.
    func requestScreenCaptureAccess()
}
```

---

## 3. Data Models

All models live in `Claude Lens/Models/`. They are pure SwiftData entities with zero service or ViewModel imports.

### 3.1 Session

```swift
// Models/Session.swift

import Foundation
import SwiftData

@Model
final class Session {
    var id: UUID
    var title: String
    var isAutoTitled: Bool
    var systemPrompt: String?
    var responseMode: String          // Stored as raw value of ResponseMode
    var tokenCountInput: Int
    var tokenCountOutput: Int
    var createdAt: Date
    var updatedAt: Date

    @Relationship(deleteRule: .cascade, inverse: \Message.session)
    var messages: [Message]

    // --- Computed ---

    var mode: ResponseMode {
        get { ResponseMode(rawValue: responseMode) ?? .chat }
        set { responseMode = newValue.rawValue }
    }

    var totalTokens: Int { tokenCountInput + tokenCountOutput }

    var sortedMessages: [Message] {
        messages.sorted { $0.createdAt < $1.createdAt }
    }
}
```

### 3.2 Message

```swift
// Models/Message.swift

import Foundation
import SwiftData

@Model
final class Message {
    var id: UUID
    var role: String                  // "user" or "assistant"
    var content: String
    var imageData: Data?
    var tokenCount: Int
    var createdAt: Date
    var session: Session?

    // --- Computed ---

    var messageRole: MessageRole {
        MessageRole(rawValue: role) ?? .user
    }

    var hasImage: Bool { imageData != nil }
}

enum MessageRole: String, Codable, Sendable {
    case user = "user"
    case assistant = "assistant"
}
```

### 3.3 ResponseMode

```swift
// Models/ResponseMode.swift

import Foundation

enum ResponseMode: String, CaseIterable, Codable, Sendable {
    case chat = "chat"
    case translate = "translate"
    case explain = "explain"
    case code = "code"

    var displayName: String { ... }
    var icon: String { ... }            // SF Symbol name
    var systemPrompt: String { ... }
    var command: String { ... }

    static func fromCommand(_ text: String) -> ResponseMode? { ... }
}
```

---

## 4. ViewModel Designs

### 4.1 ChatViewModel

```swift
// ViewModels/ChatViewModel.swift

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

    /// Send the current input (text + optional image) to Claude API.
    /// Creates user and assistant Message models in the given context.
    func sendMessage(session: Session, modelContext: ModelContext) { ... }

    /// Attach image data for the next message.
    func attachImage(_ data: Data) { ... }

    /// Remove the currently attached image.
    func removeAttachedImage() { ... }
}
```

**Key change from current code:** `ClaudeAPIService.shared` and `KeychainHelper` are replaced with protocol-injected dependencies. The `sendMessage` method uses `apiService.streamMessage(...)` returning `AsyncThrowingStream<StreamEvent>` instead of callback closures, enabling structured concurrency with a `for try await` loop.

### 4.2 SessionListViewModel

```swift
// ViewModels/SessionListViewModel.swift

import Foundation
import SwiftData

@MainActor
@Observable
final class SessionListViewModel {
    var searchText = ""
    var selectedSessionID: PersistentIdentifier?

    // No service dependencies needed — pure SwiftData CRUD.

    func createSession(modelContext: ModelContext) -> Session { ... }
    func deleteSession(_ session: Session, modelContext: ModelContext) { ... }
    func deleteAllSessions(modelContext: ModelContext) { ... }
    func filteredSessions(_ sessions: [Session]) -> [Session] { ... }
    func storageInfo(sessions: [Session]) -> (sessionCount: Int, messageCount: Int, estimatedSize: String) { ... }
}
```

### 4.3 SettingsViewModel

```swift
// ViewModels/SettingsViewModel.swift

import Foundation

@MainActor
@Observable
final class SettingsViewModel {
    var apiKeyInput = ""
    var isValidating = false
    var validationResult: Bool?
    var customSystemPrompt: String { ... }  // UserDefaults-backed

    // --- Dependencies ---
    private let apiService: ClaudeAPIServiceProtocol
    private let keychainService: KeychainServiceProtocol

    init(
        apiService: ClaudeAPIServiceProtocol,
        keychainService: KeychainServiceProtocol
    ) {
        self.apiService = apiService
        self.keychainService = keychainService
    }

    var maskedKey: String { keychainService.maskedKey() ?? "Not set" }
    var hasAPIKey: Bool { keychainService.hasKey }

    func saveAPIKey() async -> Bool { ... }
    func deleteAPIKey() { ... }

    // Permission checks remain direct OS calls (not worth abstracting)
    var isAccessibilityGranted: Bool { AXIsProcessTrusted() }
    var isScreenCaptureGranted: Bool { CGPreflightScreenCaptureAccess() }
}
```

---

## 5. AppState and Coordination

### 5.1 AppState

```swift
// App/AppState.swift

import Foundation

@MainActor
@Observable
final class AppState {
    var isOverlayVisible = false
    var pendingCapturedText: String?
    var pendingCapturedImage: Data?

    // UserDefaults-backed preferences
    var isOnboardingComplete: Bool { get set }
    var selectedModel: String { get set }

    func toggleOverlay() { ... }
    func showOverlay() { ... }
    func hideOverlay() { ... }

    static let availableModels: [(id: String, name: String)] = [...]
}
```

**Key change:** `AppState` is no longer a singleton. It is created in `Claude_LensApp` and passed through the SwiftUI environment or as a parameter.

### 5.2 App Entry Point

```swift
// App/Claude_LensApp.swift

@main
struct Claude_LensApp: App {
    // Create service instances (concrete types)
    private let apiService: ClaudeAPIServiceProtocol = ClaudeAPIService()
    private let keychainService: KeychainServiceProtocol = KeychainService()
    private let clipboardService: ClipboardServiceProtocol = ClipboardService()
    private let hotkeyService: HotkeyServiceProtocol = HotkeyService()
    private let textSelectionService: TextSelectionServiceProtocol = TextSelectionService(clipboard: ...)
    private let screenCaptureService: ScreenCaptureServiceProtocol = ScreenCaptureService()

    @State private var appState = AppState()

    // Wire hotkey callbacks, pass services to ViewModels via environment or init
}
```

---

## 6. Dependency Injection Strategy

### 6.1 Service Container

A lightweight struct groups all service instances for convenient passing:

```swift
// App/ServiceContainer.swift

import Foundation

/// Groups all service protocol references for dependency injection.
@MainActor
struct ServiceContainer {
    let apiService: ClaudeAPIServiceProtocol
    let keychainService: KeychainServiceProtocol
    let clipboardService: ClipboardServiceProtocol
    let hotkeyService: HotkeyServiceProtocol
    let textSelectionService: TextSelectionServiceProtocol
    let screenCaptureService: ScreenCaptureServiceProtocol

    /// Production configuration with real service implementations.
    static func production() -> ServiceContainer {
        let clipboard = ClipboardService()
        return ServiceContainer(
            apiService: ClaudeAPIService(),
            keychainService: KeychainService(),
            clipboardService: clipboard,
            hotkeyService: HotkeyService(),
            textSelectionService: TextSelectionService(clipboard: clipboard),
            screenCaptureService: ScreenCaptureService()
        )
    }
}
```

### 6.2 SwiftUI Environment Key

```swift
// App/ServiceContainerKey.swift

import SwiftUI

private struct ServiceContainerKey: EnvironmentKey {
    @MainActor static let defaultValue: ServiceContainer = .production()
}

extension EnvironmentValues {
    var services: ServiceContainer {
        get { self[ServiceContainerKey.self] }
        set { self[ServiceContainerKey.self] = newValue }
    }
}
```

### 6.3 Usage in Views

```swift
struct ChatView: View {
    let session: Session
    @Environment(\.services) private var services
    @Environment(\.modelContext) private var modelContext
    @State private var chatVM: ChatViewModel?

    var body: some View {
        content
            .onAppear {
                if chatVM == nil {
                    chatVM = ChatViewModel(
                        apiService: services.apiService,
                        keychainService: services.keychainService
                    )
                }
            }
    }
}
```

### 6.4 Testing with Mocks

```swift
// Tests/Mocks/MockClaudeAPIService.swift

final class MockClaudeAPIService: ClaudeAPIServiceProtocol, @unchecked Sendable {
    var streamMessageResult: [StreamEvent] = []
    var validateKeyResult = true
    var streamMessageCallCount = 0

    func streamMessage(
        contents: [MessageContent],
        conversationHistory: [[String: Any]],
        systemPrompt: String,
        model: String,
        apiKey: String
    ) -> AsyncThrowingStream<StreamEvent, Error> {
        streamMessageCallCount += 1
        let events = streamMessageResult
        return AsyncThrowingStream { continuation in
            for event in events {
                continuation.yield(event)
            }
            continuation.finish()
        }
    }

    func validateAPIKey(_ apiKey: String) async -> Bool {
        validateKeyResult
    }
}
```

---

## 7. Layer Separation Rules

| Rule | Description |
|------|-------------|
| **Models import nothing** | `Session`, `Message`, `ResponseMode` import only `Foundation` and `SwiftData`. No services, no ViewModels, no SwiftUI. |
| **Services own their protocol** | Each service file implements its protocol. Services may depend on other service protocols (e.g., `TextSelectionService` depends on `ClipboardServiceProtocol`). Services never import SwiftUI or SwiftData. |
| **ViewModels depend on protocols** | ViewModels receive service dependencies through `init` parameters typed as protocols, never concrete classes. ViewModels import `Foundation` and `SwiftData` (for `ModelContext`), never `SwiftUI`. |
| **Views depend on ViewModels** | Views create or receive ViewModels. Views access services only indirectly through ViewModels, except `@Environment(\.services)` for ViewModel initialization. |
| **No singletons** | Replace all `.shared` patterns with injected instances. The `ServiceContainer` is the single composition root, created in the App entry point. |
| **ModelContext is a parameter** | ViewModels receive `ModelContext` as method parameters, not stored properties. This keeps them testable (pass a test container's context). |

### Import Rules by Layer

| Layer | Allowed Imports |
|-------|----------------|
| Models | `Foundation`, `SwiftData` |
| Protocols | `Foundation`, `CoreGraphics` (for `CGRect`) |
| Services | `Foundation`, `AppKit`, `Carbon`, `ScreenCaptureKit`, protocol files |
| ViewModels | `Foundation`, `SwiftData`, protocol files |
| Views | `SwiftUI`, `SwiftData`, ViewModel files, Model files |
| App | `SwiftUI`, `SwiftData`, everything (composition root) |

---

## 8. View Hierarchy

```
Claude_LensApp (Scene)
├── MenuBarExtra
│   ├── Show/Hide Overlay button
│   ├── New Session button
│   ├── Settings button
│   └── Quit button
│
├── Window("Claude Lens")
│   ├── OnboardingView (shown if !isOnboardingComplete)
│   │   ├── Step 0: welcomeStep
│   │   ├── Step 1: apiKeyStep
│   │   ├── Step 2: permissionsStep
│   │   └── Step 3: readyStep
│   │
│   └── ContentView
│       └── NavigationSplitView
│           ├── sidebar: SidebarView
│           │   ├── Search TextField
│           │   ├── List of SessionRowView
│           │   └── Bottom bar (New Chat + session count)
│           │
│           └── detail: ChatView (or emptyState)
│               ├── Header (title, mode, token counts)
│               ├── ScrollView > LazyVStack
│               │   └── ForEach: MessageBubbleView
│               │       ├── userBubble (right-aligned, image + text)
│               │       └── assistantBubble (left-aligned, markdown + copy)
│               ├── Error banner (conditional)
│               └── InputBarView
│                   ├── Attached image preview
│                   ├── Mode picker (Menu)
│                   ├── Paste image button
│                   ├── TextField (multi-line)
│                   └── Send button
│
└── Settings (window)
    └── SettingsView
        └── TabView
            ├── General tab (model, permissions, shortcuts)
            ├── API tab (key management, system prompt)
            └── Data tab (storage info, delete all)
```

---

## 9. Concurrency Strategy

### 9.1 @MainActor Isolation

| Component | @MainActor | Reason |
|-----------|-----------|--------|
| All Views | Yes (implicit) | SwiftUI requirement |
| All ViewModels | Yes (explicit) | UI state mutations must happen on main thread |
| AppState | Yes (explicit) | Observed by Views |
| ClipboardService | Yes (explicit) | NSPasteboard is main-thread only |
| HotkeyService | Yes (explicit) | Carbon event handler dispatches on main thread |
| TextSelectionService | Yes (explicit) | CGEvent + clipboard access |
| ScreenCaptureService | Yes (explicit) | ScreenCaptureKit callbacks |
| ClaudeAPIService | No | Network-bound; returns AsyncThrowingStream consumed on @MainActor |
| KeychainService | No | Thread-safe Security framework calls |

### 9.2 Streaming Pattern

The current code uses callback closures (`onToken`, `onComplete`, `onError`). The redesigned architecture uses structured concurrency:

```swift
// In ChatViewModel.sendMessage():
func sendMessage(session: Session, modelContext: ModelContext) {
    guard let apiKey = keychainService.load() else {
        errorMessage = "API key not found."
        return
    }

    // ... create messages, build history ...

    isStreaming = true
    currentResponse = ""
    errorMessage = nil

    Task {
        do {
            let stream = apiService.streamMessage(
                contents: contents,
                conversationHistory: history,
                systemPrompt: systemPrompt,
                model: selectedModel,
                apiKey: apiKey
            )

            for try await event in stream {
                switch event {
                case .textDelta(let text):
                    currentResponse += text
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

            // Stream finished — auto-title, save
            if session.isAutoTitled && session.messages.count <= 2 {
                generateAutoTitle(for: session, firstMessage: text)
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
```

### 9.3 Sendable Boundaries

- `StreamEvent` is `Sendable` (enum of value types).
- `MessageContent` is `Sendable` (enum with `String` and `Data`).
- `ClaudeAPIServiceProtocol` is `Sendable` so the service can be captured in `Task` closures from `@MainActor` contexts.
- `KeychainServiceProtocol` is `Sendable` for the same reason.
- `@MainActor`-isolated protocols (`ClipboardServiceProtocol`, etc.) do not need `Sendable` since they are only called from the main actor.

---

## 10. File Organization (Target State)

```
Claude Lens/
├── App/
│   ├── Claude_LensApp.swift              # @main, scene, hotkey wiring
│   ├── AppState.swift                    # Global observable state
│   ├── ServiceContainer.swift            # DI container struct
│   └── ServiceContainerKey.swift         # SwiftUI EnvironmentKey
│
├── Models/
│   ├── Session.swift                     # @Model — conversation session
│   ├── Message.swift                     # @Model — individual message
│   └── ResponseMode.swift               # Response mode enum
│
├── Protocols/
│   ├── ClaudeAPIServiceProtocol.swift    # + StreamEvent, MessageContent
│   ├── KeychainServiceProtocol.swift
│   ├── ClipboardServiceProtocol.swift
│   ├── HotkeyServiceProtocol.swift
│   ├── TextSelectionServiceProtocol.swift
│   └── ScreenCaptureServiceProtocol.swift
│
├── Services/
│   ├── ClaudeAPIService.swift            # URLSession SSE streaming
│   ├── KeychainService.swift             # Security framework (renamed from Helper)
│   ├── ClipboardService.swift            # NSPasteboard operations
│   ├── HotkeyService.swift              # Carbon HotKey API
│   ├── TextSelectionService.swift        # ⌘+C simulation + clipboard
│   └── ScreenCaptureService.swift        # ScreenCaptureKit
│
├── ViewModels/
│   ├── ChatViewModel.swift               # Chat logic + streaming
│   ├── SessionListViewModel.swift        # Session CRUD + search
│   └── SettingsViewModel.swift           # Settings + key management
│
├── Views/
│   ├── ContentView.swift                 # NavigationSplitView
│   ├── SidebarView.swift                 # Session list sidebar
│   ├── ChatView.swift                    # Message area + input
│   ├── MessageBubbleView.swift           # Individual message bubble
│   ├── InputBarView.swift                # Text/image input bar
│   ├── OnboardingView.swift              # First-run wizard
│   ├── SettingsView.swift                # Settings tabs
│   └── OverlayWindow.swift              # NSPanel subclass + controller
│
└── Utilities/
    └── TokenCounter.swift                # Token estimation helper
```

---

## 11. Migration Checklist (Current State to Target)

The current codebase has these architectural issues that the feature-implementer must fix:

| Issue | Current | Target |
|-------|---------|--------|
| Singleton services | `ClaudeAPIService.shared`, `HotkeyService.shared`, etc. | Injected via `ServiceContainer` |
| No protocols | Services are concrete classes without interfaces | Every service has a protocol in `Protocols/` |
| Direct Keychain access | `KeychainHelper` enum with static methods | `KeychainService` class conforming to `KeychainServiceProtocol` |
| Callback-based streaming | `onToken` / `onComplete` / `onError` closures | `AsyncThrowingStream<StreamEvent>` |
| AppState singleton | `AppState.shared` referenced everywhere | `AppState()` instance via `@State` in App, environment for children |
| ViewModels create singletons | `ChatViewModel` accesses `ClaudeAPIService.shared` directly | Receives `ClaudeAPIServiceProtocol` via init |
| Views access services directly | `InputBarView` calls `ClipboardService.shared.readImage()` | Goes through ViewModel method |
| `KeychainHelper` naming | Named "Helper" (enum with static methods) | Renamed to `KeychainService` (class, instance methods) |
| Missing Protocols/ directory | Does not exist | New directory with 6 protocol files |
| Missing ServiceContainer | Does not exist | New file in App/ |

---

## 12. Handoff Notes for Feature-Implementer

### Implementation Order

Follow this sequence to avoid forward-reference compile errors:

1. **Models** (no changes needed beyond adding `Sendable` where needed)
2. **Protocols/** (create all 6 protocol files -- these have zero dependencies)
3. **Services** (refactor each to conform to its protocol, remove `static let shared`, accept dependencies via init)
4. **ServiceContainer** + **ServiceContainerKey** (composition root)
5. **ViewModels** (refactor to accept protocol dependencies via init)
6. **Views** (refactor to use `@Environment(\.services)` for ViewModel creation, remove all `.shared` references)
7. **App entry point** (create `ServiceContainer.production()`, wire hotkeys, pass through environment)

### Critical Details

- **TextSelectionService depends on ClipboardServiceProtocol** -- pass it via init, do not access `.shared`.
- **ClaudeAPIService should NOT be @MainActor** -- it does network I/O. The `AsyncThrowingStream` it returns will be consumed on @MainActor by the ViewModel.
- **HotkeyService must remain @MainActor** -- Carbon event handlers run on the main thread.
- **KeychainHelper becomes KeychainService** -- convert from `enum` with `static` methods to `final class` with instance methods conforming to `KeychainServiceProtocol`.
- **OverlayPanel / OverlayWindowController** -- these are AppKit classes managing the floating panel. They remain in Views/ and are not abstracted behind a protocol (they are UI, not business logic).
- **Streaming refactor** -- the single biggest change. Replace the 3-callback pattern in `ClaudeAPIService.sendMessage()` with `AsyncThrowingStream<StreamEvent>`. The ViewModel then uses `for try await event in stream { ... }` inside a `Task`.
- **conversationHistory type** -- the current `[[String: Any]]` type works but is not type-safe. This is acceptable for MVP; a future refactor can introduce `Codable` request/response models.

### Testing Strategy

With protocols in place, every ViewModel can be tested by injecting mocks:

| Test Target | Mock Dependencies | Key Assertions |
|-------------|-------------------|----------------|
| `ChatViewModel` | `MockClaudeAPIService`, `MockKeychainService` | Message creation, streaming token accumulation, error handling, auto-title |
| `SettingsViewModel` | `MockClaudeAPIService`, `MockKeychainService` | API key save/validate/delete, masked key display |
| `SessionListViewModel` | (none -- pure SwiftData) | Create/delete sessions, search filtering, storage calculation |
