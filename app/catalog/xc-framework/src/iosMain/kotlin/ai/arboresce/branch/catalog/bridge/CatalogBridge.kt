package ai.arboresce.branch.catalog.bridge

import ai.arboresce.branch.catalog.CatalogFixtures
import ai.arboresce.branch.catalog.CatalogRoot
import androidx.compose.ui.window.ComposeUIViewController

fun makeCatalogViewController() = ComposeUIViewController { CatalogRoot() }

fun catalogItemTitles(): List<String> = CatalogFixtures.items.map { it.title }
