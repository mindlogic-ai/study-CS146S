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
