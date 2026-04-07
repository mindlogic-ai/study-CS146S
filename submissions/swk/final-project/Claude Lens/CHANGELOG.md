# Changelog

## [Unreleased]

### Refactored
- ChatViewModel.sendMessage now accepts an optional `selectedModel` parameter instead of reading UserDefaults directly, improving testability and respecting DIP (ChatViewModel.swift)
- MessageBubbleView copy button now uses ClipboardServiceProtocol via environment instead of direct NSPasteboard access, maintaining DI consistency (MessageBubbleView.swift)
- SettingsView.dataTab reuses a single @State SessionListViewModel instead of creating throwaway instances on each render (SettingsView.swift)
- Removed force-unwrap on URL literal in OnboardingView, replaced with safe `if let` binding (OnboardingView.swift)
