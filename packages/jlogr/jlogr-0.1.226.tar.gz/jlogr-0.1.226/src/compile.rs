// Set default macOS deployment target version
// Unsure if i need this honestly
 if target.is_macos() && env::var_os("MACOSX_DEPLOYMENT_TARGET").is_none() {
     use crate::target::rustc_macosx_target_version;

     let (major, minor) = rustc_macosx_target_version(target.target_triple());
     build_command.env("MACOSX_DEPLOYMENT_TARGET", format!("{}.{}", major, minor));
