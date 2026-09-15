use std::{env, process::Command};
fn main() {
    println!("cargo:rerun-if-changed=build.rs");
    println!("cargo:rerun-if-env-changed=BRANCH_BUILD_ID");
    let output = Command::new(env::var_os("RUSTC").expect("Cargo supplies RUSTC"))
        .arg("--version")
        .output()
        .expect("read compiler version");
    assert!(output.status.success());
    let compiler = String::from_utf8(output.stdout).expect("compiler version is UTF-8");
    println!("cargo:rustc-env=BRANCH_RUSTC={}", compiler.trim());
    for (source, destination) in [("TARGET", "BRANCH_TARGET"), ("PROFILE", "BRANCH_PROFILE")] {
        println!(
            "cargo:rustc-env={destination}={}",
            env::var(source).expect("Cargo build metadata")
        );
    }
}
