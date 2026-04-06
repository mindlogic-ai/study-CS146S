# CLAUDE.md — Claude Lens (macOS AI Overlay App)

## Project Overview

**Claude Lens** — macOS 네이티브 오버레이 앱. 글로벌 단축키로 호출하여 드래그한 텍스트나 스크린샷을 Claude API로 번역/설명하는 AI 어시스턴트.

## Tech Stack

- **Language:** Swift 6
- **UI:** SwiftUI (macOS 15+)
- **Persistence:** SwiftData
- **AI:** Anthropic Claude API (direct REST, streaming SSE)
- **Package Manager:** Swift Package Manager

## Architecture (MVVM)

```
ClaudeLens/
├── App/
│   ├── ClaudeLensApp.swift          # Entry point, hotkey, menu bar
│   └── AppState.swift               # Global state (Observable)
├── Models/
│   ├── Session.swift                # SwiftData - 대화 세션
│   └── Message.swift                # SwiftData - 메시지 (text/image)
├── ViewModels/
│   ├── ChatViewModel.swift          # Chat logic, Claude API calls
│   └── SessionListViewModel.swift   # Session CRUD
├── Views/
│   ├── ContentView.swift            # NavigationSplitView (sidebar + detail)
│   ├── SidebarView.swift            # Session history list
│   ├── ChatView.swift               # Message list + scroll
│   ├── MessageBubbleView.swift      # Individual message bubble
│   └── InputBarView.swift           # Text + image input bar
├── Services/
│   ├── ClaudeAPIService.swift       # Anthropic REST API (streaming)
│   ├── HotkeyService.swift          # Global hotkey (Carbon API)
│   └── ClipboardService.swift       # NSPasteboard read (text/image)
└── Utilities/
    └── KeychainHelper.swift         # API key secure storage
```

## Build & Run

```bash
# Xcode에서 열기
open ClaudeLens.xcodeproj

# 또는 커맨드라인 빌드
xcodebuild -scheme ClaudeLens -configuration Debug build

# 테스트
xcodebuild -scheme ClaudeLens test
```

## Multi-Agent Workflow

이 프로젝트는 4개의 전문 에이전트를 활용한 멀티에이전트 개발 워크플로우를 사용합니다.

### Agent Pipeline

```
[새 기능 요청]
     │
     ▼
┌─────────────────────┐
│ architecture-reviewer│  ← Phase 1: 설계 (opus)
│ ARCHITECTURE.md 작성 │
│ Protocol 정의        │
└────────┬────────────┘
         │ handoff
         ▼
┌─────────────────────┐
│ feature-implementer  │  ← Phase 2: 구현 (sonnet)
│ Domain → Service →   │
│ View 순서 구현       │
└────────┬────────────┘
         │ handoff
         ▼
┌─────────────────────┐
│ test-writer          │  ← Phase 3: 테스트 (sonnet)
│ Swift Testing 작성   │
│ Given/When/Then      │
└────────┬────────────┘
         │ handoff
         ▼
┌─────────────────────┐
│ code-refactor        │  ← Phase 4: 리팩토링 (opus)
│ SOLID 검증           │
│ 네이밍/성능 개선      │
└─────────────────────┘
```

### When to Use Each Agent

| Agent | Trigger | Model |
|-------|---------|-------|
| `architecture-reviewer` | 새 기능 설계, Protocol 정의, 아키텍처 결정 | opus |
| `feature-implementer` | 설계 완료 후 구현, SwiftUI 뷰 작성, API 연동 | sonnet |
| `test-writer` | 코드 구현 완료 후 테스트 작성 | sonnet |
| `code-refactor` | 기능 완성 후 코드 품질 개선 | opus |

### Parallel Agent Usage

독립적인 작업은 에이전트를 병렬로 실행:
- UI 구현 + API 서비스 구현 → 별도 에이전트 동시 실행
- 테스트 작성 + 문서 업데이트 → 병렬 실행 가능

## Code Conventions

### Swift Style
- **Indentation:** 4 spaces
- **Line length:** 120 characters
- **Naming:** camelCase (properties/methods), PascalCase (types/protocols)
- **Access control:** 최소 권한 원칙 (private first, widen as needed)
- **Concurrency:** async/await + @MainActor for UI updates

### SwiftUI Patterns
- `@Observable` macro (iOS 17+ / macOS 14+)
- `NavigationSplitView` for sidebar layout
- `@Environment(\.modelContext)` for SwiftData access
- Small, composable views (max ~50 lines per View body)

### Error Handling
- `Result` type or throwing functions
- Never force-unwrap in production code
- User-facing errors → localized alert messages

## Claude API Integration

- **Endpoint:** `POST https://api.anthropic.com/v1/messages`
- **Auth:** `x-api-key` header (stored in Keychain)
- **Streaming:** SSE (`stream: true`) for real-time response rendering
- **Vision:** Base64-encoded images in `content` array
- **Model:** `claude-sonnet-4-20250514` (default)

### System Prompt Strategy
```
You are a helpful assistant. When the user provides text, translate it 
or explain it based on context. When the user provides an image/screenshot, 
describe and explain the content. Respond in the same language as the user's 
message unless asked to translate.
```

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...   # Required: Claude API key
```

API key는 `.env` 파일 또는 macOS Keychain에 저장.

## Key Dependencies (SPM)

- No external dependencies for MVP (URLSession for networking, SwiftData for persistence)
- Optional: `HotKey` package for simplified global hotkey registration

## File Naming Convention

- Views: `*View.swift`
- ViewModels: `*ViewModel.swift`
- Models: singular noun (e.g., `Session.swift`, `Message.swift`)
- Services: `*Service.swift`
- Protocols: `*Protocol.swift` or descriptive name
