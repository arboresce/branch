.DEFAULT_GOAL := help
ifneq ($(origin TARGET),undefined)
$(error Use an explicit target such as make dev-ios)
endif
.PHONY: help doctor setup check test verify setup-rust check-rust test-rust verify-rust setup-ios dev-ios build-ios check-ios test-ios verify-ios setup-android dev-android build-android check-android test-android verify-android
help doctor setup check test verify setup-rust check-rust test-rust verify-rust setup-ios dev-ios build-ios check-ios test-ios verify-ios setup-android dev-android build-android check-android test-android verify-android:
	@bash scripts/commands.sh "$@"
