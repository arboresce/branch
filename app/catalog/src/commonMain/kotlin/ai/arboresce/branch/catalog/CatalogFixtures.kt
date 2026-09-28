package ai.arboresce.branch.catalog

data class CatalogItem(
    val id: String,
    val title: String,
    val subtitle: String,
)

data class CatalogMedia(
    val id: String,
    val label: String,
    val width: Int,
    val height: Int,
)

data class CatalogFormField(
    val id: String,
    val label: String,
    val required: Boolean,
)

object CatalogFixtures {
    const val FIXED_NOW_MILLIS: Long = 1_700_000_000_000

    val items: List<CatalogItem> =
        List(5) { index ->
            val position = index + 1
            CatalogItem(
                id = "catalog-item-$position",
                title = "Catalog Item $position",
                subtitle = "Deterministic row $position",
            )
        }

    val media: List<CatalogMedia> =
        listOf(
            CatalogMedia(id = "catalog-media-1", label = "Landscape", width = 16, height = 9),
            CatalogMedia(id = "catalog-media-2", label = "Portrait", width = 3, height = 4),
        )

    val form: List<CatalogFormField> =
        listOf(
            CatalogFormField(id = "catalog-field-1", label = "Name", required = true),
            CatalogFormField(id = "catalog-field-2", label = "Note", required = false),
        )

    val runtimeSnapshots: List<String> =
        listOf(
            "{\"source\":\"catalog\",\"schema_version\":1,\"revision\":0}",
            "{\"source\":\"catalog\",\"schema_version\":1,\"revision\":1}",
        )
}
