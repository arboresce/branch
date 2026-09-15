package ai.arboresce.branch
import ai.arboresce.branch.bindings.BranchRuntime
import android.app.Application

class BranchApplication : Application() {
    val runtime: BranchRuntime by lazy { BranchRuntime() }
}
