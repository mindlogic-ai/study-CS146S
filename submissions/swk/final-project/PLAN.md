# Claude Lens — macOS AI Overlay Assistant

## Concept

글로벌 단축키로 호출되는 macOS 오버레이 앱. 드래그한 텍스트나 스크린샷을 입력으로 받아 Claude API를 통해 번역, 설명, 요약 등을 제공한다.

### Core Value Proposition

> **"드래그 → 단축키 → 즉시 AI 응답"**
>
> 다른 AI 앱은 브라우저를 열고, 텍스트를 복사하고, 탭을 전환하고, 붙여넣고, 프롬프트를 작성해야 한다.
> Claude Lens는 **텍스트를 드래그한 뒤 단축키 하나**면 끝이다.
> 이 "제로 프릭션" 워크플로우가 앱의 핵심 경쟁력이다.

---

## Feature Specification

### F1. Quick Capture — 핵심 기능 (★)

앱의 가장 중요한 기능. 어떤 앱에서든 텍스트/이미지를 최소 동작으로 Claude에게 전달한다.

#### Quick Capture Flow (텍스트)

```
┌─────────────────────────────────────────────────────────────┐
│                    사용자 워크플로우                           │
│                                                             │
│  ① 크롬/사파리/노션 등에서 텍스트 드래그 (선택 상태)           │
│                    │                                        │
│                    ▼                                        │
│  ② ⌘+⇧+L 누름 (글로벌 핫키)                                │
│                    │                                        │
│     ┌──────────────▼──────────────┐                         │
│     │     백그라운드 처리 (~100ms)  │                         │
│     │                             │                         │
│     │  1. 현재 클립보드 백업       │                         │
│     │  2. ⌘+C 시뮬레이션 (CGEvent)│                         │
│     │  3. 50ms 대기               │                         │
│     │  4. 클립보드에서 텍스트 읽기  │                         │
│     │  5. 원래 클립보드 복원       │                         │
│     └──────────────┬──────────────┘                         │
│                    │                                        │
│                    ▼                                        │
│  ③ 오버레이 윈도우 등장                                      │
│     → 입력 바에 캡처된 텍스트가 자동으로 채워져 있음            │
│     → 현재 응답 모드(번역/설명/코드)에 따른 시스템 프롬프트 적용│
│                    │                                        │
│                    ▼                                        │
│  ④ 사용자 선택:                                              │
│     a) Enter → 바로 전송 (가장 빠른 경로, 2스텝 완료!)        │
│     b) 텍스트 수정/추가 질문 작성 후 Enter                    │
│     c) 모드 변경 후 Enter                                    │
│                    │                                        │
│                    ▼                                        │
│  ⑤ Claude 스트리밍 응답 렌더링                                │
│     → 응답 복사 버튼으로 바로 활용                             │
└─────────────────────────────────────────────────────────────┘
```

**최단 경로: 드래그 → ⌘+⇧+L → Enter = 2스텝으로 AI 응답 획득**

#### Quick Capture Flow (이미지/스크린샷) — 전용 캡처

```
┌─────────────────────────────────────────────────────────────┐
│                  스크린샷 Quick Capture                       │
│                                                             │
│  ① ⌘+⇧+K 누름 (스크린샷 전용 핫키)                          │
│                    │                                        │
│                    ▼                                        │
│  ② 화면에 영역 선택 UI 등장                                   │
│     → 반투명 오버레이 + 크로스헤어 커서                        │
│     → 드래그로 캡처 영역 선택                                 │
│     → Esc로 취소 가능                                        │
│                    │                                        │
│     ┌──────────────▼──────────────┐                         │
│     │     백그라운드 처리           │                         │
│     │                             │                         │
│     │  1. CGWindowListCreateImage │                         │
│     │     로 선택 영역 캡처        │                         │
│     │  2. NSImage → Data 변환     │                         │
│     └──────────────┬──────────────┘                         │
│                    │                                        │
│                    ▼                                        │
│  ③ 오버레이 윈도우 등장                                      │
│     → 입력 바에 캡처된 이미지 썸네일 표시                      │
│     → 입력 바에 자동 포커스 (추가 질문 입력 가능)              │
│                    │                                        │
│                    ▼                                        │
│  ④ 사용자 선택:                                              │
│     a) Enter → 바로 전송 ("이 이미지를 설명해줘")             │
│     b) "이 에러 메시지 해결법 알려줘" 등 추가 질문 후 Enter    │
│                    │                                        │
│                    ▼                                        │
│  ⑤ Claude Vision API로 이미지 분석 응답                      │
└─────────────────────────────────────────────────────────────┘
```

**최단 경로: ⌘+⇧+K → 영역 드래그 → Enter = 2스텝으로 스크린샷 AI 분석**

#### Quick Capture Flow (이미지/스크린샷) — 클립보드 폴백

기존 macOS 스크린샷 도구를 사용하는 경우도 지원:
```
  ① ⌘+⇧+⌃+4 로 스크린샷 (클립보드에 저장)
  ② ⌘+⇧+L 누름 (텍스트 핫키) → 클립보드에 이미지 감지 → 썸네일 표시
  ③ Enter → 응답
```

#### Quick Capture 핫키 요약

| Hotkey | 동작 | 최단 경로 |
|--------|------|----------|
| `⌘+⇧+L` | 선택 텍스트 캡처 → 오버레이 | 드래그 → ⌘+⇧+L → Enter (2스텝) |
| `⌘+⇧+K` | 스크린샷 영역 캡처 → 오버레이 | ⌘+⇧+K → 드래그 → Enter (2스텝) |

#### 기술 구현 상세

```swift
// TextSelectionService.swift — 텍스트 캡처
class TextSelectionService {
    /// 글로벌 핫키 트리거 시 호출
    /// 현재 활성 앱에서 선택된 텍스트를 가져온다
    func captureSelectedText() async -> String? {
        // 1. 현재 클립보드 백업
        let backup = NSPasteboard.general.save()
        
        // 2. ⌘+C 시뮬레이션 (Accessibility 권한 필요)
        let source = CGEventSource(stateID: .hidEventState)
        let cmdC_down = CGEvent(keyboardEventSource: source, 
                                virtualKey: 0x08, keyDown: true)
        cmdC_down?.flags = .maskCommand
        cmdC_down?.post(tap: .cghidEventTap)
        
        let cmdC_up = CGEvent(keyboardEventSource: source, 
                              virtualKey: 0x08, keyDown: false)
        cmdC_up?.flags = .maskCommand
        cmdC_up?.post(tap: .cghidEventTap)
        
        // 3. 클립보드 갱신 대기
        try? await Task.sleep(for: .milliseconds(50))
        
        // 4. 클립보드에서 텍스트 읽기
        let captured = NSPasteboard.general.string(forType: .string)
        
        // 5. 원래 클립보드 복원
        NSPasteboard.general.restore(from: backup)
        
        return captured
    }
}

// ScreenCaptureService.swift — 스크린샷 캡처
class ScreenCaptureService {
    /// 영역 선택 UI를 띄우고 선택된 영역을 캡처
    func captureScreenRegion() async -> NSImage? {
        // 1. 반투명 풀스크린 오버레이 윈도우 표시
        // 2. 크로스헤어 커서로 전환
        // 3. 사용자 드래그로 영역 선택 (CGRect)
        // 4. CGWindowListCreateImage(rect, ...) 로 해당 영역 캡처
        // 5. 오버레이 닫고 NSImage 반환
        // * Esc 시 nil 반환 (취소)
    }
}
```

#### 필수 권한
- **Accessibility 권한** — CGEvent를 통한 키 시뮬레이션에 필수 (텍스트 Quick Capture)
  - 첫 실행 시 `AXIsProcessTrusted()` 체크
  - 미허용 시 System Settings → Privacy → Accessibility 안내 다이얼로그
  - 권한 없으면 텍스트 Quick Capture 비활성화, 수동 `⌘+V`만 가능
- **Screen Recording 권한** — `CGWindowListCreateImage`에 필수 (스크린샷 Quick Capture)
  - 첫 스크린샷 캡처 시 macOS가 자동으로 권한 요청
  - 미허용 시 스크린샷 Quick Capture 비활성화, 기존 macOS 스크린샷(`⌘+⇧+⌃+4`) + `⌘+⇧+L` 폴백

### F2. Overlay Window
- 오버레이는 모든 앱 위에 떠있는 floating panel (`NSPanel`, `.floating` level)
- `Esc`로 오버레이 닫기
- 윈도우 위치/크기 변경 시 다음 호출에도 유지 (UserDefaults 저장)
- 오버레이 열릴 때 입력 바에 자동 포커스 (바로 타이핑 가능)
- Dock 대신 **메뉴바 아이콘**(Status Bar Item)으로 상주

### F3. Text Input
- 직접 텍스트 입력
- `⌘+V`로 클립보드 텍스트/이미지 수동 붙여넣기
- Quick Capture로 자동 채워진 텍스트 편집 가능

### F4. Screenshot / Image Input
- 스크린샷 또는 이미지 `⌘+V`로 붙여넣기
- Quick Capture 시 클립보드에 이미지가 있으면 자동으로 이미지 입력
- Claude Vision API를 통해 이미지 내용 인식 및 설명
- 이미지는 base64로 인코딩하여 multimodal 요청
- 채팅 영역에 이미지 썸네일 표시

### F4. Response Mode (응답 모드 선택)
입력 바 옆에 모드 드롭다운 또는 `/command` 방식:

| Mode | Command | System Prompt 동작 |
|------|---------|-------------------|
| 번역 (자동 감지) | `/translate` | 입력 텍스트의 언어를 감지하여 한↔영 번역 |
| 설명 / 요약 | `/explain` | 텍스트 또는 이미지의 내용을 쉽게 설명 |
| 코드 설명 | `/code` | 코드를 분석하고 동작 원리를 설명 |
| 자유 질문 | (기본) | 별도 모드 없이 일반 대화 |

- 각 모드별로 최적화된 시스템 프롬프트가 자동 적용
- 모드는 세션 단위로 유지되거나, 메시지 단위로 전환 가능

### F5. AI Response & Streaming
- Claude API SSE(Server-Sent Events) 스트리밍으로 실시간 응답 렌더링
- **스트리밍 인디케이터** — 응답 생성 중 타이핑 애니메이션 또는 깜빡이는 커서
- **Markdown 렌더링** — 코드블록(syntax highlighting), 볼드, 이탤릭, 리스트, 링크 등
- **응답 복사 버튼** — 각 응답 버블에 복사 버튼, 클릭 시 클립보드에 복사
- **컨텍스트 유지** — 같은 세션 내 이전 대화를 Claude에 함께 전송하여 맥락 유지

### F6. Chat UI
- **좌측 사이드바**: 세션 히스토리 리스트
  - 새 세션 생성 (`⌘+N`)
  - 세션 삭제 (스와이프 또는 우클릭)
  - 세션 검색 (제목 기반 필터)
  - **세션 자동 제목** — 첫 메시지 기반으로 Claude가 세션 제목을 자동 생성
- **우측 메인 영역**: 채팅 메시지 렌더링
  - 유저 메시지 (우측 정렬, 텍스트 + 이미지)
  - 어시스턴트 메시지 (좌측 정렬, 마크다운 렌더링)
  - 자동 스크롤 (새 메시지 시 하단으로)

### F7. Keyboard-First UX
오버레이 앱 특성상 키보드 중심 조작:

| Shortcut | Action |
|----------|--------|
| `⌘ + ⇧ + L` | 텍스트 Quick Capture → 오버레이 |
| `⌘ + ⇧ + K` | 스크린샷 Quick Capture → 영역 선택 → 오버레이 |
| `Esc` | 오버레이 닫기 / 스크린샷 영역 선택 취소 |
| `⌘ + N` | 새 세션 |
| `⌘ + V` | 클립보드 붙여넣기 (텍스트/이미지) |
| `Enter` | 메시지 전송 |
| `Shift + Enter` | 줄바꿈 |
| `⌘ + C` | 선택된 응답 텍스트 복사 |
| `⌘ + ,` | 설정 열기 |

### F8. Session Persistence & Storage Management (SwiftData)
- 모든 세션과 메시지를 SwiftData(SQLite)로 로컬 저장
- 앱 재시작 시 이전 세션 복원
- 세션별 메시지 히스토리 무제한 보관
- 세션 삭제 시 관련 메시지(텍스트+이미지)도 cascade 삭제
- **저장 용량 표시:**
  - 설정 화면에 전체 저장 용량 표시 (e.g. "대화 기록: 42.3 MB")
  - SwiftData DB 파일 크기 + 이미지 데이터 합산
  - 세션 수, 총 메시지 수도 함께 표시 (e.g. "23개 세션 · 156개 메시지 · 42.3 MB")
- **데이터 정리 (Clear):**
  - **전체 삭제** — 모든 세션/메시지 일괄 삭제 + 확인 다이얼로그 ("정말 모든 대화 기록을 삭제하시겠습니까?")
  - **기간별 삭제** — 오래된 대화 정리 (e.g. "30일 이전 대화 삭제", "90일 이전")
  - **개별 세션 삭제** — 사이드바에서 스와이프 또는 우클릭 → 삭제
  - 삭제 후 용량 즉시 재계산 및 UI 반영

### F9. Onboarding & Permissions
- **첫 실행 온보딩 플로우 (스텝 바이 스텝 위저드):**

  ```
  ┌─────────────────────────────────────────────┐
  │            Onboarding Wizard                │
  │                                             │
  │  Step 1: Welcome                            │
  │  ● ○ ○ ○                                    │
  │  "Claude Lens에 오신 것을 환영합니다"         │
  │  앱 소개 + 핵심 기능 미리보기                  │
  │  [다음 →]                                    │
  ├─────────────────────────────────────────────┤
  │  Step 2: API Key                            │
  │  ○ ● ○ ○                                    │
  │  Anthropic API key 입력                      │
  │  [Console에서 발급받기 ↗] 링크               │
  │  [sk-ant-...        ] [검증]                 │
  │  ✅ "API key가 확인되었습니다"                 │
  │  [다음 →]                                    │
  ├─────────────────────────────────────────────┤
  │  Step 3: Permissions                        │
  │  ○ ○ ● ○                                    │
  │  앱이 필요한 권한을 요청합니다                  │
  │                                             │
  │  ☐ Accessibility 권한 (필수)                 │
  │    → 텍스트 Quick Capture에 필요              │
  │    [권한 허용하기]                             │
  │                                             │
  │  ☐ Screen Recording 권한 (선택)              │
  │    → 스크린샷 Quick Capture에 필요            │
  │    [권한 허용하기]                             │
  │                                             │
  │  * 권한은 나중에 설정에서 변경 가능             │
  │  [다음 →]                                    │
  ├─────────────────────────────────────────────┤
  │  Step 4: Ready!                             │
  │  ○ ○ ○ ●                                    │
  │  "모든 설정이 완료되었습니다!"                  │
  │  Quick Capture: ⌘+⇧+L (텍스트)              │
  │  Screenshot:    ⌘+⇧+K (스크린샷)            │
  │  [시작하기 🚀]                                │
  └─────────────────────────────────────────────┘
  ```

  - **Step 1: Welcome** — 앱 소개, 핵심 가치("드래그 → 단축키 → AI 응답") 안내
  - **Step 2: API Key** — 키 입력 + 유효성 검증 + Keychain 저장
  - **Step 3: Permissions** — 필요 권한 일괄 요청
    - **Accessibility** (필수) — 텍스트 Quick Capture용. `AXIsProcessTrusted()` 체크 후 System Settings로 안내
    - **Screen Recording** (선택) — 스크린샷 Quick Capture용. `CGPreflightScreenCaptureAccess()` / `CGRequestScreenCaptureAccess()` 호출
    - 각 권한별 상태 표시: ✅ 허용됨 / ⚠️ 미허용 (기능 제한 안내)
    - 권한 미허용 시에도 다음 단계 진행 가능 (나중에 설정에서 변경 안내)
  - **Step 4: Ready** — 설정 완료 확인 + 핵심 단축키 안내 + 시작
- **키 미설정 상태:**
  - 채팅 입력 비활성화
  - 메인 영역에 "API key를 설정해주세요" 안내 + 설정 바로가기 버튼
- **키 관리 (설정 화면):**
  - API key 변경 (현재 키는 마스킹 표시: `sk-ant-...xxxx`)
  - 키 삭제
  - 키 재검증 버튼
- **보안:**
  - API key는 Keychain에만 저장 (UserDefaults, 파일 등에 저장 금지)
  - 메모리에서도 사용 후 즉시 해제
  - 로그/콘솔에 키 노출 금지

### F10. Settings (설정)
- **모델 선택** — Claude Sonnet / Haiku / Opus 전환
- **System Prompt 커스터마이징** — 기본 시스템 프롬프트를 사용자가 직접 수정
- **토큰 사용량 표시** — 세션별 및 누적 토큰 카운트 (input/output tokens)
- **단축키 커스터마이징:**
  - 설정 화면에 Hotkeys 섹션
  - 변경 가능한 단축키 목록:
    | Action | 기본값 | 설명 |
    |--------|--------|------|
    | Text Quick Capture | `⌘+⇧+L` | 선택 텍스트 캡처 → 오버레이 |
    | Screenshot Quick Capture | `⌘+⇧+K` | 영역 선택 스크린샷 → 오버레이 |
    | 새 세션 | `⌘+N` | 새 대화 세션 생성 |
    | 설정 열기 | `⌘+,` | 설정 화면 열기 |
  - **키 레코딩 방식:** 입력 필드 클릭 → "Press shortcut..." 표시 → 사용자가 원하는 키 조합 입력 → 자동 등록
  - **충돌 감지:** 다른 앱/시스템 단축키와 겹칠 경우 경고 표시
  - **기본값 복원:** "Reset to Defaults" 버튼
  - 변경된 단축키는 UserDefaults에 저장, 앱 재시작 시 자동 적용
  - 글로벌 핫키(Text/Screenshot Quick Capture)는 즉시 재등록

### F11. Menu Bar Icon
- Dock 아이콘 대신 메뉴바에 상주하는 Status Bar Item
- 메뉴바 아이콘 클릭 시:
  - 오버레이 열기/닫기
  - 최근 세션 바로가기
  - 설정 열기
  - 앱 종료

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Swift 6 |
| **UI Framework** | SwiftUI (macOS 15+) |
| **AI API** | Anthropic Claude API (claude-sonnet-4-20250514) |
| **Networking** | URLSession (streaming SSE) |
| **Persistence** | SwiftData (SQLite backed) |
| **Hotkey** | Carbon HotKey API / HotKey package |
| **Image** | Claude Vision API (base64) |
| **Secure Storage** | Keychain (API key) |
| **Package Manager** | Swift Package Manager |

---

## Architecture

```
┌──────────────────────────────────────────────────────┐
│              macOS Menu Bar App                       │
│  ┌─────┐                                             │
│  │ ☰  │ ← Status Bar Item                           │
│  └──┬──┘                                             │
│     │ toggle                                         │
│  ┌──▼───────────────────────────────────────────┐    │
│  │           Overlay Window (Panel)              │    │
│  ├──────────┬───────────────────────────────────┤    │
│  │ Sidebar  │         Main Chat Area            │    │
│  │          │                                   │    │
│  │ [Search] │  ┌─────────────────────────────┐  │    │
│  │          │  │   Message Bubbles           │  │    │
│  │ [New ⌘N] │  │   (Markdown + Images)       │  │    │
│  │ [Sess 1] │  │   + Copy buttons            │  │    │
│  │ [Sess 2] │  │   + Streaming indicator     │  │    │
│  │ [Sess 3] │  └─────────────────────────────┘  │    │
│  │          │  ┌─────────────────────────────┐  │    │
│  │          │  │ [Mode ▼] [Input...] [Send]  │  │    │
│  │          │  │  /translate /explain /code   │  │    │
│  ├──────────┴──┴─────────────────────────────┘  │    │
│  │  Token count: 1,234 in / 2,567 out           │    │
│  └──────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────┘

App Architecture (MVVM):

├── App/
│   ├── ClaudeLensApp.swift          # Entry point, menu bar, hotkey
│   └── AppState.swift               # Global state (@Observable)
├── Models/
│   ├── Session.swift                # SwiftData - 세션 (auto-title)
│   ├── Message.swift                # SwiftData - 메시지 (text/image)
│   └── ResponseMode.swift           # 응답 모드 enum
├── ViewModels/
│   ├── ChatViewModel.swift          # 채팅 로직, streaming, 컨텍스트 관리
│   ├── SessionListViewModel.swift   # 세션 CRUD, 검색, 자동 제목
│   └── SettingsViewModel.swift      # 설정 관리
├── Views/
│   ├── OverlayWindow.swift          # Floating panel 설정
│   ├── ContentView.swift            # NavigationSplitView (sidebar + detail)
│   ├── SidebarView.swift            # 세션 히스토리 + 검색
│   ├── ChatView.swift               # 채팅 메시지 영역
│   ├── MessageBubbleView.swift      # 메시지 버블 (마크다운 + 복사)
│   ├── InputBarView.swift           # 입력 바 (모드 선택 + 텍스트/이미지)
│   ├── OnboardingView.swift         # 첫 실행 API key 온보딩 플로우
│   ├── SettingsView.swift           # 설정 화면
│   └── MenuBarView.swift            # 메뉴바 드롭다운
├── Services/
│   ├── ClaudeAPIService.swift       # Anthropic API (streaming SSE)
│   ├── HotkeyService.swift          # 글로벌 단축키 등록/해제
│   ├── ClipboardService.swift       # NSPasteboard 읽기 (텍스트/이미지)
│   ├── TextSelectionService.swift   # 활성 앱 선택 텍스트 자동 감지
│   └── ScreenCaptureService.swift   # 영역 선택 스크린샷 캡처
└── Utilities/
    ├── KeychainHelper.swift         # API key 보안 저장
    ├── MarkdownRenderer.swift       # 마크다운 → AttributedString
    └── TokenCounter.swift           # 토큰 사용량 추적
```

---

## Data Models

### Session
```swift
@Model
final class Session {
    var id: UUID
    var title: String               // 자동 생성 또는 수동 편집
    var isAutoTitled: Bool           // 자동 제목 생성 여부
    var systemPrompt: String?       // 세션별 커스텀 시스템 프롬프트
    var responseMode: String        // "chat" | "translate" | "explain" | "code"
    var tokenCountInput: Int        // 누적 입력 토큰
    var tokenCountOutput: Int       // 누적 출력 토큰
    var createdAt: Date
    var updatedAt: Date
    @Relationship(deleteRule: .cascade) var messages: [Message]
}
```

### Message
```swift
@Model
final class Message {
    var id: UUID
    var role: String                // "user" | "assistant"
    var content: String
    var imageData: Data?            // optional screenshot/image
    var tokenCount: Int             // 이 메시지의 토큰 수
    var createdAt: Date
    var session: Session?
}
```

### ResponseMode
```swift
enum ResponseMode: String, CaseIterable, Codable {
    case chat = "chat"
    case translate = "translate"
    case explain = "explain"
    case code = "code"
    
    var displayName: String { ... }
    var systemPrompt: String { ... }
    var icon: String { ... }        // SF Symbol name
}
```

---

## Claude API Integration

- **Endpoint:** `https://api.anthropic.com/v1/messages`
- **Models:**
  - `claude-sonnet-4-20250514` (기본 — 비용 효율 + 성능 균형)
  - `claude-haiku-4-5-20251001` (빠른 응답, 낮은 비용)
  - `claude-opus-4-6` (최고 품질)
- **Streaming:** SSE를 통한 실시간 응답 렌더링
- **Vision:** 이미지를 base64로 인코딩하여 multimodal 입력
- **Context:** 세션 내 이전 대화를 messages 배열로 함께 전송
- **Token Tracking:** 응답의 `usage` 필드에서 토큰 수 추출 및 저장

### System Prompts (모드별)

```
[translate] You are a translator. Detect the language of the input text.
If Korean, translate to English. If English, translate to Korean.
If other, translate to Korean. Output only the translation.

[explain] You are an expert explainer. Analyze the given text or image
and provide a clear, concise explanation. Use bullet points for key
points. Respond in the same language as the input.

[code] You are a senior software engineer. Analyze the given code and
explain: 1) What it does, 2) How it works, 3) Any potential issues.
Include code examples when helpful.

[chat] You are a helpful assistant. Respond naturally to the user's
message. When an image is provided, describe and analyze its content.
```

---

## Implementation Plan

### Phase 1: Project Setup & Basic UI
- [ ] Xcode 프로젝트 생성 (macOS App, SwiftUI)
- [ ] SwiftData 모델 정의 (Session, Message, ResponseMode)
- [ ] 기본 레이아웃: NavigationSplitView (Sidebar + Chat)
- [ ] 세션 목록 CRUD (생성, 선택, 삭제)
- [ ] 세션 검색 필터
- [ ] 메시지 입력 바 (텍스트 입력 + 전송)
- [ ] 키보드 단축키 기본 설정 (Enter 전송, Shift+Enter 줄바꿈)

### Phase 2: Claude API Integration
- [ ] ClaudeAPIService 구현 (streaming SSE)
- [ ] 텍스트 메시지 전송 및 스트리밍 응답 렌더링
- [ ] 이미지(base64) 멀티모달 요청
- [ ] 컨텍스트 유지 (세션 내 이전 대화 전송)
- [ ] 에러 핸들링 (rate limit, network error, invalid key)
- [ ] 토큰 사용량 추적 (usage 필드 파싱)
- [ ] 스트리밍 인디케이터 (타이핑 애니메이션)

### Phase 3: Response Mode & Markdown
- [ ] ResponseMode enum 및 모드별 시스템 프롬프트
- [ ] 입력 바에 모드 드롭다운 UI
- [ ] `/translate`, `/explain`, `/code` 커맨드 파싱
- [ ] Markdown 렌더링 (AttributedString or 커스텀)
- [ ] 코드블록 syntax highlighting
- [ ] 응답 복사 버튼

### Phase 4: Overlay & Hotkey
- [ ] 글로벌 단축키 등록 (Accessibility 권한 요청)
- [ ] 오버레이 윈도우 (NSPanel, floating, above all)
- [ ] 윈도우 위치/크기 저장 및 복원 (UserDefaults)
- [ ] 메뉴바 아이콘 (MenuBarExtra)
- [ ] 메뉴바 드롭다운 (열기, 최근 세션, 설정, 종료)
- [ ] Dock 아이콘 숨기기 (LSUIElement)

### Phase 5: Quick Capture (Text + Screenshot)
- [ ] 클립보드 텍스트 읽기 (NSPasteboard)
- [ ] 클립보드 이미지 읽기 및 붙여넣기
- [ ] TextSelectionService — ⌘+C 시뮬레이션으로 선택 텍스트 캡처
- [ ] 클립보드 백업/복원 (사용자 클립보드 보존)
- [ ] ⌘+⇧+L 핫키 → 텍스트 Quick Capture → 입력 바 자동 채움
- [ ] ScreenCaptureService — 영역 선택 UI (반투명 오버레이 + 크로스헤어)
- [ ] CGWindowListCreateImage로 선택 영역 캡처
- [ ] ⌘+⇧+K 핫키 → 스크린샷 Quick Capture → 입력 바에 썸네일
- [ ] Screen Recording 권한 요청 처리
- [ ] 클립보드 이미지 폴백 (기존 macOS 스크린샷 → ⌘+⇧+L)

### Phase 6: Onboarding Wizard & Settings
- [ ] KeychainHelper 구현 (API key CRUD)
- [ ] 온보딩 위저드 (OnboardingView) — 4단계 스텝 바이 스텝
  - [ ] Step 1: Welcome — 앱 소개 + 핵심 기능 안내
  - [ ] Step 2: API Key — 입력 + 유효성 검증 + Keychain 저장
  - [ ] Step 3: Permissions — Accessibility + Screen Recording 권한 일괄 요청
  - [ ] Step 4: Ready — 설정 완료 + 단축키 안내
- [ ] 권한 상태 체크 (AXIsProcessTrusted, CGPreflightScreenCaptureAccess)
- [ ] 권한 미허용 시 기능별 폴백 처리
- [ ] 키 미설정 시 채팅 비활성화 + 안내 화면
- [ ] 설정 화면 (SettingsView)
- [ ] API key 마스킹 표시 및 변경/삭제
- [ ] 모델 선택 (Sonnet / Haiku / Opus)
- [ ] System Prompt 커스터마이징
- [ ] 단축키 커스터마이징 UI (키 레코딩 방식)
- [ ] 단축키 충돌 감지 및 경고
- [ ] 단축키 변경 시 글로벌 핫키 즉시 재등록
- [ ] 기본값 복원 ("Reset to Defaults")
- [ ] 세션 자동 제목 생성 (첫 메시지 기반 Claude 호출)
- [ ] 토큰 사용량 표시 (세션별 + 누적)
- [ ] 다크/라이트 모드 대응

### Phase 7: Testing & Submission
- [ ] ViewModel 단위 테스트 (ChatViewModel, SessionListViewModel)
- [ ] Service mock 테스트 (ClaudeAPIService, ClipboardService)
- [ ] Edge case 테스트 (빈 입력, 네트워크 에러, 큰 이미지)
- [ ] README.md 작성 (설치, 아키텍처, 설계 결정)
- [ ] .env.example 준비
- [ ] 데모 시나리오 준비 및 리허설

---

## Environment Variables

```bash
ANTHROPIC_API_KEY=sk-ant-...   # Claude API key
```

---

## Scoring Target

| Category | Target | Strategy |
|----------|--------|----------|
| Technical Depth (30) | 25+ | Multi-modal (text+vision), streaming SSE, 모드별 시스템 프롬프트, 컨텍스트 관리, 토큰 추적 |
| Product Quality (25) | 22+ | Native macOS UX, 오버레이, 클립보드/선택텍스트, 키보드 중심 UX, 마크다운, 메뉴바 |
| Code Quality (20) | 17+ | MVVM, SwiftData, Protocol 기반 DI, 멀티에이전트 개발, 테스트, .claude/ setup |
| Demo (15) | 13+ | 실사용 시나리오: 웹 텍스트 드래그→번역, 스크린샷→설명, 코드→분석 |
| Ambition (10) | 9+ | Native macOS overlay + 메뉴바 + 자동 텍스트 감지는 웹앱 대비 큰 차별화 |
