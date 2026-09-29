.DEFAULT_GOAL := help
ifneq ($(origin TARGET),undefined)
$(error Use an explicit target such as make dev-ios)
endif
.PHONY: help doctor setup check test verify setup-rust check-rust test-rust test-shared check-tools verify-rust test-shared-android test-shared-ios setup-ios dev-ios build-ios build-release-ios build-ios-device check-ios test-ios verify-ios setup-android dev-android build-android build-release-android check-android test-android verify-android build-catalog-android build-catalog-ios dev-catalog-android dev-catalog-ios test-catalog-android test-catalog-ios
help doctor setup check test verify setup-rust check-rust test-rust test-shared check-tools verify-rust test-shared-android test-shared-ios setup-ios dev-ios build-ios build-release-ios build-ios-device check-ios test-ios verify-ios setup-android dev-android build-android build-release-android check-android test-android verify-android build-catalog-android build-catalog-ios dev-catalog-android dev-catalog-ios test-catalog-android test-catalog-ios:
	@bash scripts/commands.sh "$@"
