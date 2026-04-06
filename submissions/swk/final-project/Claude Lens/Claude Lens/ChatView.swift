import SwiftData
import SwiftUI

struct ChatView: View {
    let session: Session
    @Environment(\.modelContext) private var modelContext
    @Environment(\.services) private var services
    @Environment(AppState.self) private var appState
    @State private var chatVM: ChatViewModel?

    var body: some View {
        VStack(spacing: 0) {
            // Header
            HStack {
                VStack(alignment: .leading) {
                    Text(session.title)
                        .font(.headline)
                    Text("\(session.mode.displayName) mode")
                        .font(.caption)
                        .foregroundStyle(.secondary)
                }
                Spacer()
                Text("Tokens: \(session.tokenCountInput) in / \(session.tokenCountOutput) out")
                    .font(.caption2)
                    .foregroundStyle(.tertiary)
            }
            .padding(.horizontal, 16)
            .padding(.vertical, 8)

            Divider()

            if let vm = chatVM {
                // Messages
                ScrollViewReader { proxy in
                    ScrollView {
                        LazyVStack(spacing: 0) {
                            ForEach(session.sortedMessages) { message in
                                MessageBubbleView(message: message)
                                    .id(message.id)
                            }
                        }
                        .padding(.vertical, 12)
                    }
                    .onChange(of: session.messages.count) {
                        if let lastMessage = session.sortedMessages.last {
                            withAnimation(.easeOut(duration: 0.3)) {
                                proxy.scrollTo(lastMessage.id, anchor: .bottom)
                            }
                        }
                    }
                    .onChange(of: vm.currentResponse) {
                        if let lastMessage = session.sortedMessages.last {
                            proxy.scrollTo(lastMessage.id, anchor: .bottom)
                        }
                    }
                }

                // Error banner
                if let error = vm.errorMessage {
                    HStack {
                        Image(systemName: "exclamationmark.triangle")
                        Text(error)
                            .font(.caption)
                        Spacer()
                        Button("Dismiss") { vm.errorMessage = nil }
                            .font(.caption)
                    }
                    .padding(8)
                    .background(Color.red.opacity(0.1))
                    .clipShape(RoundedRectangle(cornerRadius: 8))
                    .padding(.horizontal, 16)
                }

                Divider()

                InputBarView(chatVM: vm, session: session, modelContext: modelContext)
            }
        }
        .onAppear {
            if chatVM == nil {
                chatVM = ChatViewModel(
                    apiService: services.apiService,
                    keychainService: services.keychainService
                )
            }
            consumePendingCapture()
        }
        .onChange(of: appState.pendingCapturedText) {
            consumePendingCapture()
        }
        .onChange(of: appState.pendingCapturedImage) {
            consumePendingCapture()
        }
    }

    private func consumePendingCapture() {
        guard let vm = chatVM else { return }
        if let text = appState.pendingCapturedText {
            vm.inputText = text
            appState.pendingCapturedText = nil
        }
        if let imageData = appState.pendingCapturedImage {
            vm.attachImage(imageData)
            appState.pendingCapturedImage = nil
        }
    }
}
