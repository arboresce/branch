package ai.arboresce.branch.catalog

import ai.arboresce.branch.shared.RuntimeSource

interface CatalogClock {
    fun nowMillis(): Long
}

class FixedCatalogClock(
    private val value: Long = CatalogFixtures.FIXED_NOW_MILLIS,
) : CatalogClock {
    override fun nowMillis(): Long = value
}

class ScriptedRuntimeSource(
    private val snapshots: List<String> = CatalogFixtures.runtimeSnapshots,
) : RuntimeSource {
    private var index = 0

    override fun snapshot(): String? {
        if (snapshots.isEmpty()) return null
        val value = snapshots[index.coerceAtMost(snapshots.size - 1)]
        index += 1
        return value
    }
}
