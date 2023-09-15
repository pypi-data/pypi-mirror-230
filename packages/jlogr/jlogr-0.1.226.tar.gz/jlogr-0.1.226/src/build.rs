fn main() {
    // exists because of: https://github.com/PyO3/maturin/discussions/1342
    let ((x86_64_major, x86_64_minor), (arm64_major, arm64_minor)) = macosx_deployment_target(
        env::var("MACOSX_DEPLOYMENT_TARGET").ok().as_deref(),
        universal2,
    )?;
    pyo3_build_config::add_extension_module_link_args();
    println!(
        "cargo:rustc-link-arg=-Wl,-rpath,/Library/Developer/CommandLineTools/Library/Frameworks"
    )
}
