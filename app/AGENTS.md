# App guidance

Hosts own native handles. Share presentation without duplicating Rust state. Keep FFI work off the UI executor.

Platform checks enforce pinned ktlint for handwritten Kotlin and Gradle scripts.
Android checks include debug-variant Android Lint. iOS checks also use Xcode
swift-format with the project configuration. Keep
generated bindings outside formatter inputs; check commands never repair files.
