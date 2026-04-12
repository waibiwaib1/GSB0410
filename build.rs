use std::env;
use std::fs::{self, File};
use std::io::{self, Read, Write};
use std::path::Path;
use std::process;

use app::{RGArg, RGArgKind};

#[allow(dead_code)]
#[path = "crates/core/app.rs"]
mod app;

fn main() {
    // OUT_DIR is set by Cargo and it's where any additional build artifacts
    // are written.
    let outdir = match env::var_os("OUT_DIR") {
        Some(outdir) => outdir,
        None => {
            eprintln!(
                "OUT_DIR environment variable not defined. \
                 Please file a bug: \
                 https://github.com/BurntSushi/ripgrep/issues/new"
            );
            process::exit(1);
        }
    };
    fs::create_dir_all(&outdir).unwrap();

    let stamp_path = Path::new(&outdir).join("ripgrep-stamp");
    if let Err(err) = File::create(&stamp_path) {
        panic!("failed to write {}: {}", stamp_path.display(), err);
    }
    if let Err(err) = generate_man_page(&outdir) {
        eprintln!("failed to generate man page: {}", err);
    }

    if let Err(err) = generate_shell_completions(&outdir) {
        eprintln!("failed to generate shell completions: {}", err);
    }

    // Make the current git hash available to the build.
    if let Some(rev) = git_revision_hash() {
        println!("cargo:rustc-env=RIPGREP_BUILD_GIT_HASH={}", rev);
    }
    // Embed a Windows manifest and set some linker options. The main reason
    // for this is to enable long path support on Windows. This still, I
    // believe, requires enabling long path support in the registry. But if
    // that's enabled, then this will let ripgrep use C:\... style paths that
    // are longer than 260 characters.
    set_windows_exe_options();
}

fn set_windows_exe_options() {
    static MANIFEST: &str = "pkg/windows/Manifest.xml";

    let Ok(target_os) = env::var("CARGO_CFG_TARGET_OS") else { return };
    let Ok(target_env) = env::var("CARGO_CFG_TARGET_ENV") else { return };
    if !(target_os == "windows" && target_env == "msvc") {
        return;
    }

    let Ok(mut manifest) = env::current_dir() else { return };
    manifest.push(MANIFEST);
    let Some(manifest) = manifest.to_str() else { return };

    println!("cargo:rerun-if-changed={}", MANIFEST);
    // Embed the Windows application manifest file.
    println!("cargo:rustc-link-arg-bin=rg=/MANIFEST:EMBED");
    println!("cargo:rustc-link-arg-bin=rg=/MANIFESTINPUT:{manifest}");
    // Turn linker warnings into errors. Helps debugging, otherwise the
    // warnings get squashed (I believe).
    println!("cargo:rustc-link-arg-bin=rg=/WX");
}

fn git_revision_hash() -> Option<String> {
    let result = process::Command::new("git")
        .args(&["rev-parse", "--short=10", "HEAD"])
        .output();
    result.ok().and_then(|output| {
        let v = String::from_utf8_lossy(&output.stdout).trim().to_string();
        if v.is_empty() {
            None
        } else {
            Some(v)
        }
    })
}

fn generate_man_page<P: AsRef<Path>>(outdir: P) -> io::Result<()> {
    // If asciidoctor isn't installed, fallback to asciidoc.
    if let Err(err) = process::Command::new("asciidoctor").output() {
        eprintln!(
            "Could not run 'asciidoctor' binary, falling back to 'a2x'."
        );
        eprintln!("Error from running 'asciidoctor': {}", err);
        return legacy_generate_man_page::<P>(outdir);
    }
    // 1. Read asciidoctor template.
    // 2. Interpolate template with auto-generated docs.
    // 3. Save interpolation to disk.
    // 4. Use asciidoctor to convert to man page.
    let outdir = outdir.as_ref();
    let cwd = env::current_dir()?;
    let tpl_path = cwd.join("doc").join("rg.1.txt.tpl");
    let txt_path = outdir.join("rg.1.txt");

    let mut tpl = String::new();
    File::open(&tpl_path)?.read_to_string(&mut tpl)?;
    let options =
        formatted_options()?.replace("&#123;", "{").replace("&#125;", "}");
    tpl = tpl.replace("{OPTIONS}", &options);

    let githash = git_revision_hash();
    let githash = githash.as_ref().map(|x| &**x);
    tpl = tpl.replace("{VERSION}", &app::long_version(githash, false));

    File::create(&txt_path)?.write_all(tpl.as_bytes())?;
    let result = process::Command::new("asciidoctor")
        .arg("--doctype")
        .arg("manpage")
        .arg("--backend")
        .arg("manpage")
        .arg(&txt_path)
        .spawn()?
        .wait()?;
    if !result.success() {
        let msg =
            format!("'asciidoctor' failed with exit code {:?}", result.code());
        return Err(ioerr(msg));
    }
    Ok(())
}

fn legacy_generate_man_page<P: AsRef<Path>>(outdir: P) -> io::Result<()> {
    // If asciidoc isn't installed, then don't do anything.
    if let Err(err) = process::Command::new("a2x").output() {
        eprintln!("Could not run 'a2x' binary, skipping man page generation.");
        eprintln!("Error from running 'a2x': {}", err);
        return Ok(());
    }
    // 1. Read asciidoc template.
    // 2. Interpolate template with auto-generated docs.
    // 3. Save interpolation to disk.
    // 4. Use a2x (part of asciidoc) to convert to man page.
    let outdir = outdir.as_ref();
    let cwd = env::current_dir()?;
    let tpl_path = cwd.join("doc").join("rg.1.txt.tpl");
    let txt_path = outdir.join("rg.1.txt");

    let mut tpl = String::new();
    File::open(&tpl_path)?.read_to_string(&mut tpl)?;
    tpl = tpl.replace("{OPTIONS}", &formatted_options()?);

    let githash = git_revision_hash();
    let githash = githash.as_ref().map(|x| &**x);
    tpl = tpl.replace("{VERSION}", &app::long_version(githash, false));

    File::create(&txt_path)?.write_all(tpl.as_bytes())?;
    let result = process::Command::new("a2x")
        .arg("--no-xmllint")
        .arg("--doctype")
        .arg("manpage")
        .arg("--format")
        .arg("manpage")
        .arg(&txt_path)
        .spawn()?
        .wait()?;
    if !result.success() {
        let msg = format!("'a2x' failed with exit code {:?}", result.code());
        return Err(ioerr(msg));
    }
    Ok(())
}

fn formatted_options() -> io::Result<String> {
    let mut args = app::all_args_and_flags();
    args.sort_by(|x1, x2| x1.name.cmp(&x2.name));

    let mut formatted = vec![];
    for arg in args {
        if arg.hidden {
            continue;
        }
        // ripgrep only has two positional arguments, and probably will only
        // ever have two positional arguments, so we just hardcode them into
        // the template.
        if let app::RGArgKind::Positional { .. } = arg.kind {
            continue;
        }
        formatted.push(formatted_arg(&arg)?);
    }
    Ok(formatted.join("\n\n"))
}

fn formatted_arg(arg: &RGArg) -> io::Result<String> {
    match arg.kind {
        RGArgKind::Positional { .. } => {
            panic!("unexpected positional argument")
        }
        RGArgKind::Switch { long, short, multiple } => {
            let mut out = vec![];

            let mut header = format!("--{}", long);
            if let Some(short) = short {
                header = format!("-{}, {}", short, header);
            }
            if multiple {
                header = format!("*{}* ...::", header);
            } else {
                header = format!("*{}*::", header);
            }
            writeln!(out, "{}", header)?;
            writeln!(out, "{}", formatted_doc_txt(arg)?)?;

            Ok(String::from_utf8(out).unwrap())
        }
        RGArgKind::Flag { long, short, value_name, multiple, .. } => {
            let mut out = vec![];

            let mut header = format!("--{}", long);
            if let Some(short) = short {
                header = format!("-{}, {}", short, header);
            }
            if multiple {
                header = format!("*{}* _{}_ ...::", header, value_name);
            } else {
                header = format!("*{}* _{}_::", header, value_name);
            }
            writeln!(out, "{}", header)?;
            writeln!(out, "{}", formatted_doc_txt(arg)?)?;

            Ok(String::from_utf8(out).unwrap())
        }
    }
}

fn formatted_doc_txt(arg: &RGArg) -> io::Result<String> {
    let paragraphs: Vec<String> = arg
        .doc_long
        .replace("{", "&#123;")
        .replace("}", r"&#125;")
        // Hack to render ** literally in man page correctly. We can't put
        // these crazy +++ in the help text directly, since that shows
        // literally in --help output.
        .replace("*-g 'foo/**'*", "*-g +++'foo/**'+++*")
        .split("\n\n")
        .map(|s| s.to_string())
        .collect();
    if paragraphs.is_empty() {
        return Err(ioerr(format!("missing docs for --{}", arg.name)));
    }
    let first = format!("  {}", paragraphs[0].replace("\n", "\n  "));
    if paragraphs.len() == 1 {
        return Ok(first);
    }
    Ok(format!("{}\n+\n{}", first, paragraphs[1..].join("\n+\n")))
}

fn generate_shell_completions<P: AsRef<Path>>(outdir: P) -> io::Result<()> {
    let outdir = outdir.as_ref();
    let args = app::all_args_and_flags();

    let mut switches = vec![];
    let mut flags = vec![];
    for arg in &args {
        if arg.hidden {
            continue;
        }
        match &arg.kind {
            RGArgKind::Switch { long, short, .. } => {
                switches.push((*long, *short));
            }
            RGArgKind::Flag { long, short, .. } => {
                flags.push((*long, *short));
            }
            RGArgKind::Positional { .. } => {}
        }
    }

    generate_bash_completion(outdir, &switches, &flags)?;
    generate_fish_completion(outdir, &switches, &flags)?;
    generate_powershell_completion(outdir, &switches, &flags)?;

    Ok(())
}

fn generate_bash_completion(
    outdir: &Path,
    switches: &[(&str, Option<char>)],
    flags: &[(&str, Option<char>)],
) -> io::Result<()> {
    let mut out = String::new();
    out.push_str("_rg() {\n");
    out.push_str("  local cur prev opts\n");
    out.push_str("  COMPREPLY=()\n");
    out.push_str("  cur=\"${COMP_WORDS[COMP_CWORD]}\"\n");
    out.push_str("  prev=\"${COMP_WORDS[COMP_CWORD-1]}\"\n");
    out.push_str("\n");
    out.push_str("  local switches=\"");
    for (long, short) in switches {
        out.push_str("--");
        out.push_str(long);
        out.push_str(" ");
        if let Some(s) = short {
            out.push_str("-");
            out.push(*s);
            out.push_str(" ");
        }
    }
    out.push_str("\"\n");
    out.push_str("\n");
    out.push_str("  local flag_opts=\"");
    for (long, short) in flags {
        out.push_str("--");
        out.push_str(long);
        out.push_str(" ");
        if let Some(s) = short {
            out.push_str("-");
            out.push(*s);
            out.push_str(" ");
        }
    }
    out.push_str("\"\n");
    out.push_str("\n");
    out.push_str("  if [[ ${cur} == -* ]] ; then\n");
    out.push_str("    COMPREPLY=( $(compgen -W \"${switches} ${flag_opts}\" -- ${cur}) )\n");
    out.push_str("    return 0\n");
    out.push_str("  fi\n");
    out.push_str("\n");
    out.push_str("  case ${prev} in\n");
    for (long, short) in flags {
        out.push_str("    --");
        out.push_str(long);
        out.push_str("|");
        if let Some(s) = short {
            out.push_str("-");
            out.push(*s);
        } else {
            out.push_str("--");
            out.push_str(long);
        }
        out.push_str(")\n");
        out.push_str("      return 0\n");
        out.push_str("      ;;\n");
    }
    out.push_str("    *)\n");
    out.push_str("      ;;\n");
    out.push_str("  esac\n");
    out.push_str("\n");
    out.push_str("  COMPREPLY=( $(compgen -f -- ${cur}) )\n");
    out.push_str("  return 0\n");
    out.push_str("}\n");
    out.push_str("complete -F _rg rg\n");

    let path = outdir.join("rg.bash");
    File::create(&path)?.write_all(out.as_bytes())?;
    Ok(())
}

fn generate_fish_completion(
    outdir: &Path,
    switches: &[(&str, Option<char>)],
    flags: &[(&str, Option<char>)],
) -> io::Result<()> {
    let mut out = String::new();
    out.push_str("complete -c rg -f\n");
    for (long, short) in switches {
        out.push_str("complete -c rg -n '__fish_use_subcommand' -l ");
        out.push_str(long);
        if let Some(s) = short {
            out.push_str(" -s ");
            out.push(*s);
        }
        out.push_str("\n");
    }
    for (long, short) in flags {
        out.push_str("complete -c rg -n '__fish_use_subcommand' -l ");
        out.push_str(long);
        if let Some(s) = short {
            out.push_str(" -s ");
            out.push(*s);
        }
        out.push_str(" -r\n");
    }

    let path = outdir.join("rg.fish");
    File::create(&path)?.write_all(out.as_bytes())?;
    Ok(())
}

fn generate_powershell_completion(
    outdir: &Path,
    switches: &[(&str, Option<char>)],
    flags: &[(&str, Option<char>)],
) -> io::Result<()> {
    let mut out = String::new();
    out.push_str("using namespace System.Management.Automation\n");
    out.push_str("using namespace System.Management.Automation.Language\n");
    out.push_str("\n");
    out.push_str("Register-ArgumentCompleter -CommandName rg -ScriptBlock {\n");
    out.push_str("    param($wordToComplete, $commandAst, $cursorPosition)\n");
    out.push_str("\n");
    out.push_str("    $commandElements = $commandAst.CommandElements\n");
    out.push_str("    $command = @(\n");
    out.push_str("        'rg'\n");
    out.push_str("        for ($i = 1; $i -lt $commandElements.Count; $i++) {\n");
    out.push_str("            $element = $commandElements[$i]\n");
    out.push_str("            if ($element -isnot [StringConstantExpressionAst]) {\n");
    out.push_str("                break\n");
    out.push_str("            }\n");
    out.push_str("            if ($element.Value.StartsWith('-') -and $element.Value -notmatch '^--?$') {\n");
    out.push_str("                break\n");
    out.push_str("            }\n");
    out.push_str("        }\n");
    out.push_str("    ) -join ' '\n");
    out.push_str("\n");
    out.push_str("    $completions = @(\n");
    for (long, short) in switches {
        if let Some(s) = short {
            out.push_str("        [CompletionResult]::new('-");
            out.push(*s);
            out.push_str("', '-");
            out.push(*s);
            out.push_str("', [CompletionResultType]::ParameterName, '--");
            out.push_str(long);
            out.push_str("')\n");
        }
        out.push_str("        [CompletionResult]::new('--");
        out.push_str(long);
        out.push_str("', '--");
        out.push_str(long);
        out.push_str("', [CompletionResultType]::ParameterName, '--");
        out.push_str(long);
        out.push_str("')\n");
    }
    for (long, short) in flags {
        if let Some(s) = short {
            out.push_str("        [CompletionResult]::new('-");
            out.push(*s);
            out.push_str("', '-");
            out.push(*s);
            out.push_str("', [CompletionResultType]::ParameterName, '--");
            out.push_str(long);
            out.push_str("')\n");
        }
        out.push_str("        [CompletionResult]::new('--");
        out.push_str(long);
        out.push_str("', '--");
        out.push_str(long);
        out.push_str("', [CompletionResultType]::ParameterName, '--");
        out.push_str(long);
        out.push_str("')\n");
    }
    out.push_str("    )\n");
    out.push_str("\n");
    out.push_str("    $completions.Where{ $_.CompletionText -like \"$wordToComplete*\" }\n");
    out.push_str("}\n");

    let path = outdir.join("_rg.ps1");
    File::create(&path)?.write_all(out.as_bytes())?;
    Ok(())
}

fn ioerr(msg: String) -> io::Error {
    io::Error::new(io::ErrorKind::Other, msg)
}
