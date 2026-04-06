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

## Available Tools — MCP Servers & Plugins

에이전트와 메인 세션에서 적극 활용해야 하는 도구들:

### MCP: XcodeBuildMCP (`xcodebuild`)
Xcode 프로젝트 빌드, 테스트, 실행을 자동화하는 MCP 서버.

**사용 시점:**
- 코드 작성/수정 후 빌드 검증 → `xcodebuild` MCP로 빌드
- 테스트 실행 → `xcodebuild` MCP로 테스트 러닝
- UI 확인 → 앱 실행 후 스크린샷 캡처
- 빌드 에러 발생 시 → 에러 로그 확인 및 수정

**에이전트별 활용:**
| Agent | XcodeBuildMCP 활용 |
|-------|-------------------|
| `feature-implementer` | 구현 완료 후 빌드 검증, 앱 실행하여 기본 동작 확인 |
| `test-writer` | 테스트 작성 후 테스트 실행 및 결과 확인 |
| `code-refactor` | 리팩토링 후 빌드 + 테스트 통과 검증 |

### Plugin: SwiftUI Expert (`swiftui-expert`)
SwiftUI 코드 작성, 리뷰, 개선을 위한 전문 스킬.

**사용 시점:**
- SwiftUI 뷰 작성 시 best practice 확인
- `@Observable`, `NavigationSplitView`, state management 패턴 결정
- macOS 14+ / iOS 17+ API 활용 가이드
- Liquid Glass 등 최신 디자인 트렌드 적용

### Plugin: Swift Concurrency (`swift-concurrency`)
async/await, actor isolation, Sendable 관련 전문 스킬.

**사용 시점:**
- `@MainActor` isolation 패턴 설계
- URLSession SSE 스트리밍 구현 시 concurrency 패턴
- Swift 6 strict concurrency 대응
- data race 진단 및 해결

### Plugin: Swift Testing Expert (`swift-testing-expert`)
Swift Testing 프레임워크 전문 스킬.

**사용 시점:**
- `#expect` / `#require` 매크로 사용법
- parameterized test, trait, tag 설계
- XCTest → Swift Testing 마이그레이션
- async 테스트 패턴

### Plugin: Swift LSP (`swift-lsp`)
Swift 코드 분석을 위한 LSP 통합.

**사용 시점:**
- 심볼 정의 찾기 (`goto definition`)
- 참조 검색 (`find references`)
- 코드 진단 (`diagnostics`) — 컴파일 에러/경고 실시간 확인
- 리네이밍 (`rename`) — 안전한 심볼 이름 변경

### Plugin: Oh My Claude Code (`oh-my-claudecode`)
고급 워크플로우 오케스트레이션.

**사용 시점:**
- `/ultrawork` — 여러 파일을 병렬로 구현할 때
- `/verify` — 변경사항이 실제로 동작하는지 검증
- `/trace` — 버그 원인 추적
- `/autopilot` — 자율 구현 모드

### Tool Usage Rules

1. **코드 작성 후 반드시 빌드 검증** — XcodeBuildMCP로 빌드하여 컴파일 에러 즉시 확인
2. **SwiftUI 뷰 작성 시** — `swiftui-expert` 스킬로 best practice 확인
3. **async/await 코드 작성 시** — `swift-concurrency` 스킬로 actor isolation 확인
4. **테스트 작성 시** — `swift-testing-expert` 스킬로 최신 매크로/패턴 활용
5. **리팩토링 시** — Swift LSP로 참조 검색 후 안전하게 변경
6. **빌드 실패 시** — Swift LSP diagnostics + XcodeBuildMCP 에러 로그 병행 확인

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
