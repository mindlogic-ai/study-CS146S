# Claude Lens

macOS 네이티브 오버레이 AI 어시스턴트. 글로벌 단축키로 텍스트나 스크린샷을 캡처하고, Claude API를 통해 번역/설명/코드 분석/자유 질문을 즉시 수행합니다.

## Screenshots

> 앱 실행 시 오버레이 윈도우가 자동으로 열리며, 메뉴 바에서 접근할 수 있습니다.

## Features

- **Text Quick Capture** — 텍스트를 드래그한 상태에서 `Cmd+Shift+L`로 즉시 캡처 & 분석
- **Screenshot Capture** — `Cmd+Ctrl+Shift+4`로 화면 영역을 캡처하여 이미지 분석
- **Streaming Responses** — Claude API SSE 스트리밍으로 실시간 응답 표시
- **Markdown Rendering** — MarkdownUI를 활용한 리치 마크다운 렌더링 (헤더, 코드블록, 리스트 등)
- **Multi-Session** — 여러 대화 세션을 사이드바에서 관리
- **4가지 응답 모드:**

| 모드 | 명령어 | 설명 |
|------|--------|------|
| 자유 질문 | (기본) | 일반 AI 대화 |
| 번역 | `/translate` | 한↔영 자동 감지 번역 |
| 설명 | `/explain` | 텍스트/이미지 분석 설명 |
| 코드 설명 | `/code` | 코드 분석 및 설명 |

- **이미지 첨부** — 클립보드 이미지 붙여넣기 지원
- **Floating Overlay** — 다른 앱 위에 항상 표시되는 플로팅 패널
- **Menu Bar App** — Dock에 표시되지 않는 메뉴 바 전용 앱
- **Onboarding** — 초기 설정 가이드 (API 키, 권한 설정)
- **Token Tracking** — 입력/출력 토큰 사용량 추적

## Tech Stack

| 구분 | 기술 |
|------|------|
| Language | Swift 6 |
| UI | SwiftUI (macOS 15+) |
| Persistence | SwiftData |
| AI | Anthropic Claude API (REST + SSE Streaming) |
| Markdown | [MarkdownUI](https://github.com/gonzalezreal/swift-markdown-ui) |
| Hotkeys | Carbon Event API |
| Security | macOS Keychain (API 키 저장) |
| Architecture | MVVM + Protocol-based DI |

## Requirements

- macOS 15.0+
- Xcode 16.0+
- Anthropic API Key ([발급받기](https://console.anthropic.com/settings/keys))

## Setup

### Option A: DMG로 설치 (권장)

1. **DMG 파일 열기**
   - `Claude Lens.dmg` 파일을 더블클릭
   - "개발자를 확인할 수 없음" 경고가 나타나면:
     - **System Settings → Privacy & Security** 하단으로 스크롤
     - `"Claude Lens" was blocked` 메시지 옆 **Open Anyway** 클릭
     - 또는 터미널에서 실행:
       ```bash
       xattr -cr "/Applications/Claude Lens.app"
       ```

2. **앱 설치**
   - DMG가 마운트되면 `Claude Lens.app`을 `/Applications` 폴더로 드래그
   - 또는 더블클릭하여 바로 실행

3. **첫 실행 시 권한 허용**
   - macOS가 "인터넷에서 다운로드한 앱" 확인 → **Open** 클릭
   - 메뉴 바에 Claude Lens 아이콘이 나타남

### Option B: 소스에서 빌드

1. **프로젝트 열기**
   ```bash
   open "Claude Lens.xcodeproj"
   ```

2. **빌드 & 실행**
   - Xcode에서 `Cmd+R`로 빌드 및 실행
   - 또는 커맨드라인:
     ```bash
     xcodebuild -scheme "Claude Lens" -configuration Debug build
     ```

### 초기 설정 (Onboarding)

앱 첫 실행 시 온보딩 화면이 표시됩니다:

1. **Welcome** — 앱 소개
2. **Permissions** — 권한 설정
   - Accessibility 권한 허용 (텍스트 캡처용, 필수)
   - Screen Recording 권한 허용 (스크린샷 캡처용, 선택)
3. **API Key** — Anthropic API 키 입력 및 검증
4. **Ready** — 설정 완료, 시작

## Keyboard Shortcuts

| 단축키 | 동작 |
|--------|------|
| `Cmd+Shift+L` | 텍스트 Quick Capture (글로벌) |
| `Cmd+Ctrl+Shift+4` | 스크린샷 캡처 (글로벌) |
| `Cmd+Shift+L` | 오버레이 Show/Hide (메뉴 바) |
| `Cmd+N` | 새 세션 |
| `Enter` | 메시지 전송 |
| `Shift+Enter` | 줄바꿈 |

## Architecture

```
Claude Lens/
├── Claude_LensApp.swift          # Entry point, MenuBarExtra, hotkey wiring
├── AppState.swift                # Global observable state
├── Models/
│   ├── Session.swift             # SwiftData 대화 세션
│   ├── Message.swift             # SwiftData 메시지 (text/image)
│   └── ResponseMode.swift        # 응답 모드 enum
├── ViewModels/
│   ├── ChatViewModel.swift       # 채팅 로직, API 호출
│   ├── SessionListViewModel.swift # 세션 CRUD
│   └── SettingsViewModel.swift   # 설정 관리
├── Views/
│   ├── ContentView.swift         # NavigationSplitView (sidebar + detail)
│   ├── SidebarView.swift         # 세션 히스토리 리스트
│   ├── ChatView.swift            # 메시지 리스트 + 스크롤
│   ├── MessageBubbleView.swift   # 메시지 버블 (Markdown 렌더링)
│   ├── InputBarView.swift        # 텍스트 + 이미지 입력 바
│   ├── OnboardingView.swift      # 초기 설정 가이드
│   └── SettingsView.swift        # 설정 화면
├── Services/
│   ├── ClaudeAPIService.swift    # Anthropic REST API (SSE streaming)
│   ├── HotkeyService.swift       # Carbon API 글로벌 단축키
│   ├── ClipboardService.swift    # NSPasteboard 텍스트/이미지 읽기
│   ├── KeychainService.swift     # Keychain API 키 저장
│   ├── TextSelectionService.swift # Accessibility 텍스트 선택 캡처
│   └── ScreenCaptureService.swift # 화면 캡처 권한 관리
├── Protocols/                    # 모든 서비스의 Protocol 인터페이스
├── Overlay/
│   └── OverlayWindow.swift       # NSPanel 기반 플로팅 윈도우
└── DI/
    ├── ServiceContainer.swift    # 의존성 주입 컨테이너
    └── ServiceContainerKey.swift # SwiftUI EnvironmentKey
```

## Testing

```bash
xcodebuild -scheme "Claude Lens" test -parallel-testing-enabled NO
```

52개의 유닛 테스트가 포함되어 있습니다:
- `ChatViewModelTests` — 메시지 전송, 스트리밍, 에러 처리, 자동 제목 생성
- `SessionListViewModelTests` — 세션 CRUD
- `SettingsViewModelTests` — API 키 저장/검증
- `ResponseModeTests` — 응답 모드 전환, 시스템 프롬프트

모든 서비스는 Protocol 기반으로 설계되어 Mock 객체를 통한 테스트가 가능합니다.

## Development

이 프로젝트는 **Multi-Agent Pipeline**으로 개발되었습니다:

1. **Architecture Reviewer** (Opus) — MVVM 설계, Protocol 정의, ARCHITECTURE.md 작성
2. **Feature Implementer** (Sonnet) — Models → Services → ViewModels → Views 순서 구현
3. **Test Writer** (Sonnet) — Swift Testing 프레임워크 기반 테스트 작성
4. **Code Refactor** (Opus) — SOLID 원칙 검증, 코드 품질 개선

## License

This project is part of Stanford CS146S coursework.
