import MarkdownUI
import SwiftUI

struct MessageBubbleView: View {
    let message: Message
    @Environment(\.services) private var services

    var body: some View {
        HStack(alignment: .top, spacing: 12) {
            if message.messageRole == .assistant {
                assistantBubble
                Spacer(minLength: 40)
            } else {
                Spacer(minLength: 40)
                userBubble
            }
        }
        .padding(.horizontal, 16)
        .padding(.vertical, 4)
    }

    private var userBubble: some View {
        VStack(alignment: .trailing, spacing: 6) {
            if let imageData = message.imageData, let nsImage = NSImage(data: imageData) {
                Image(nsImage: nsImage)
                    .resizable()
                    .aspectRatio(contentMode: .fit)
                    .frame(maxWidth: 300, maxHeight: 200)
                    .clipShape(RoundedRectangle(cornerRadius: 8))
            }
            if !message.content.isEmpty {
                Text(message.content)
                    .textSelection(.enabled)
                    .padding(12)
                    .background(Color.accentColor.opacity(0.15))
                    .clipShape(RoundedRectangle(cornerRadius: 12))
            }
        }
    }

    private var assistantBubble: some View {
        VStack(alignment: .leading, spacing: 6) {
            HStack(alignment: .top) {
                Image(systemName: "sparkles")
                    .foregroundStyle(.purple)
                    .font(.caption)
                    .padding(.top, 4)

                if message.content.isEmpty {
                    ProgressView()
                        .controlSize(.small)
                        .padding(12)
                } else if message.isStreaming {
                    // Plain text during streaming to avoid MarkdownUI re-parsing every token
                    Text(message.content)
                        .textSelection(.enabled)
                        .padding(12)
                        .background(Color(.controlBackgroundColor))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                } else {
                    Markdown(message.content)
                        .markdownTheme(.gitHub)
                        .textSelection(.enabled)
                        .padding(12)
                        .background(Color(.controlBackgroundColor))
                        .clipShape(RoundedRectangle(cornerRadius: 12))
                }
            }

            if !message.content.isEmpty {
                Button {
                    services.clipboardService.writeText(message.content)
                } label: {
                    Label("Copy", systemImage: "doc.on.doc")
                        .font(.caption2)
                }
                .buttonStyle(.plain)
                .foregroundStyle(.secondary)
            }
        }
    }
}
