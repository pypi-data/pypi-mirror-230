//! JIT-style runtime for WebAssembly using Cranelift.

#![deny(missing_docs, trivial_numeric_casts, unused_extern_crates)]
#![warn(unused_import_braces)]

mod code_memory;
mod debug;
mod demangling;
mod instantiate;
pub mod profiling;
mod unwind;

pub use crate::code_memory::CodeMemory;
pub use crate::instantiate::{
    subslice_range, CompiledFunctionInfo, CompiledModule, CompiledModuleInfo, ObjectBuilder,
    SymbolizeContext,
};
pub use demangling::*;

/// Version number of this crate.
pub const VERSION: &str = env!("CARGO_PKG_VERSION");
