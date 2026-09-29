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

    val probeImageBytes: ByteArray =
        byteArrayOf(
            0x89.toByte(),
            0x50.toByte(),
            0x4e.toByte(),
            0x47.toByte(),
            0x0d.toByte(),
            0x0a.toByte(),
            0x1a.toByte(),
            0x0a.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x0d.toByte(),
            0x49.toByte(),
            0x48.toByte(),
            0x44.toByte(),
            0x52.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x01.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x01.toByte(),
            0x08.toByte(),
            0x06.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x1f.toByte(),
            0x15.toByte(),
            0xc4.toByte(),
            0x89.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x0b.toByte(),
            0x49.toByte(),
            0x44.toByte(),
            0x41.toByte(),
            0x54.toByte(),
            0x78.toByte(),
            0x9c.toByte(),
            0x63.toByte(),
            0x60.toByte(),
            0x00.toByte(),
            0x02.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x05.toByte(),
            0x00.toByte(),
            0x01.toByte(),
            0x7a.toByte(),
            0x5e.toByte(),
            0xab.toByte(),
            0x3f.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x00.toByte(),
            0x49.toByte(),
            0x45.toByte(),
            0x4e.toByte(),
            0x44.toByte(),
            0xae.toByte(),
            0x42.toByte(),
            0x60.toByte(),
            0x82.toByte(),
        )
}
