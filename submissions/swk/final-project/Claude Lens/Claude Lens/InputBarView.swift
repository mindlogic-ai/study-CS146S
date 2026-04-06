import SwiftData
import SwiftUI

struct InputBarView: View {
    @Bindable var chatVM: ChatViewModel
    let session: Session
    let modelContext: ModelContext
    @Environment(\.services) private var services
    @FocusState private var isInputFocused: Bool

    init(chatVM: ChatViewModel, session: Session, modelContext: ModelContext) {
        self.chatVM = chatVM
        self.session = session
        self.modelContext = modelContext
    }

    var body: some View {
        VStack(spacing: 8) {
            // Attached image preview
            if let imageData = chatVM.attachedImageData,
               let nsImage = NSImage(data: imageData)
            {
                HStack {
                    Image(nsImage: nsImage)
                        .resizable()
                        .aspectRatio(contentMode: .fit)
                        .frame(height: 60)
                        .clipShape(RoundedRectangle(cornerRadius: 6))

                    Button {
                        chatVM.removeAttachedImage()
                    } label: {
                        Image(systemName: "xmark.circle.fill")
                            .foregroundStyle(.secondary)
                    }
                    .buttonStyle(.plain)

                    Spacer()
                }
                .padding(.horizontal, 12)
            }

            HStack(spacing: 8) {
                // Mode picker
                Menu {
                    ForEach(ResponseMode.allCases, id: \.self) { mode in
                        Button {
                            session.mode = mode
                        } label: {
                            Label(mode.displayName, systemImage: mode.icon)
                        }
                    }
                } label: {
                    Image(systemName: session.mode.icon)
                        .frame(width: 28, height: 28)
                        .contentShape(Rectangle())
                }
                .menuStyle(.borderlessButton)
                .frame(width: 36)

                // Paste image button — only visible when clipboard has an image
                if services.clipboardService.hasImage() {
                    Button {
                        if let imageData = services.clipboardService.readImage() {
                            chatVM.attachImage(imageData)
                        }
                    } label: {
                        Image(systemName: "photo.on.rectangle")
                            .frame(width: 28, height: 28)
                    }
                    .buttonStyle(.plain)
                    .help("Paste image from clipboard")
                }

                // Text input
                TextEditor(text: $chatVM.inputText)
                    .font(.body)
                    .scrollContentBackground(.hidden)
                    .frame(minHeight: 20, maxHeight: 120)
                    .fixedSize(horizontal: false, vertical: true)
                    .focused($isInputFocused)
                    .overlay(alignment: .leading) {
                        if chatVM.inputText.isEmpty {
                            Text("Type a message... (/translate, /explain, /code)")
                                .foregroundStyle(.tertiary)
                                .allowsHitTesting(false)
                        }
                    }
                    .onKeyPress(.return, phases: .down) { keyPress in
                        if keyPress.modifiers.contains(.shift) {
                            return .ignored // allow newline
                        }
                        chatVM.sendMessage(session: session, modelContext: modelContext)
                        return .handled
                    }

                // Send button
                Button {
                    chatVM.sendMessage(session: session, modelContext: modelContext)
                } label: {
                    Image(systemName: "arrow.up.circle.fill")
                        .font(.title2)
                        .foregroundStyle(
                            chatVM.inputText.isEmpty && chatVM.attachedImageData == nil
                                ? Color.secondary : Color.accentColor
                        )
                }
                .buttonStyle(.plain)
                .disabled(chatVM.inputText.isEmpty && chatVM.attachedImageData == nil)
                .keyboardShortcut(.return, modifiers: [])
            }
            .padding(10)
            .background(Color(.controlBackgroundColor))
            .clipShape(RoundedRectangle(cornerRadius: 12))
        }
        .padding(.horizontal, 16)
        .padding(.bottom, 12)
        .onAppear { isInputFocused = true }
        .onChange(of: chatVM.inputText) {
            isInputFocused = true
        }
    }
}
