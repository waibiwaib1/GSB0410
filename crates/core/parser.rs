use std::collections::{HashMap, VecDeque};
use std::ffi::{OsStr, OsString};

use lexopt::{self, Parser, ValueExt};

use crate::flags::FlagKind;
use crate::{flags, Result};

#[derive(Clone, Debug)]
pub struct ParsedFlags {
    switches: HashMap<&'static str, u64>,
    flags: HashMap<&'static str, VecDeque<OsString>>,
    positionals: VecDeque<OsString>,
}

impl ParsedFlags {
    pub fn new() -> Self {
        ParsedFlags {
            switches: HashMap::new(),
            flags: HashMap::new(),
            positionals: VecDeque::new(),
        }
    }

    pub fn is_present(&self, name: &str) -> bool {
        self.switches.get(name).map_or(false, |&count| count > 0)
    }

    pub fn occurrences_of(&self, name: &str) -> u64 {
        self.switches.get(name).copied().unwrap_or(0)
    }

    pub fn value_of_os(&self, name: &str) -> Option<&OsStr> {
        self.flags.get(name).and_then(|v| v.back()).map(|s| s.as_os_str())
    }

    pub fn values_of_os(&self, name: &str) -> Option<VecDeque<OsString>> {
        self.flags.get(name).cloned()
    }

    pub fn value_of_lossy(&self, name: &str) -> Option<String> {
        self.value_of_os(name).map(|s| s.to_string_lossy().into_owned())
    }

    pub fn values_of_lossy(&self, name: &str) -> Option<Vec<String>> {
        self.values_of_os(name).map(|v| {
            v.iter().map(|s| s.to_string_lossy().into_owned()).collect()
        })
    }

    pub fn positionals(&self) -> &VecDeque<OsString> {
        &self.positionals
    }

    fn add_switch(&mut self, name: &'static str) {
        let count = self.switches.get(name).copied().unwrap_or(0);
        self.switches.insert(name, count + 1);
    }

    fn add_flag(&mut self, name: &'static str, value: OsString) {
        let values = self.flags.entry(name).or_insert_with(VecDeque::new());
        values.push_back(value);
    }

    fn add_positional(&mut self, value: OsString) {
        self.positionals.push_back(value);
    }
}

pub fn parse_args<I, T>(args: I) -> Result<ParsedFlags>
where
    I: IntoIterator<Item = T>,
    T: Into<OsString> + Clone,
{
    let mut parsed = ParsedFlags::new();
    let mut parser = Parser::from_iter(args);

    while let Some(arg) = parser.next()? {
        match arg {
            lexopt::Arg::Short(short) => {
                handle_short(&mut parser, &mut parsed, short)?;
            }
            lexopt::Arg::Long(long) => {
                handle_long(&mut parser, &mut parsed, &long)?;
            }
            lexopt::Arg::Value(value) => {
                parsed.add_positional(value);
            }
        }
    }

    Ok(parsed)
}

fn handle_short(
    parser: &mut Parser,
    parsed: &mut ParsedFlags,
    short: char,
) -> Result<()> {
    if let Some(flag) = flags::find_flag_by_short(short) {
        match flag.kind {
            FlagKind::Switch { .. } => {
                apply_overrides(parsed, flag.name);
                parsed.add_switch(flag.name);
            }
            FlagKind::Flag { allow_leading_hyphen, .. } => {
                apply_overrides(parsed, flag.name);
                let value = if allow_leading_hyphen {
                    parser.optional_value()?.unwrap_or_else(|| {
                        OsString::from(parser.next()?.expect("expected value for flag"))
                    })
                } else {
                    parser.value()?
                };
                parsed.add_flag(flag.name, value);
            }
            FlagKind::Positional { .. } => {
                return Err(format!("unexpected positional flag: -{}", short).into());
            }
        }
    } else {
        return Err(lexopt::Error::UnexpectedOption(format!("-{}", short)).into());
    }
    Ok(())
}

fn handle_long(
    parser: &mut Parser,
    parsed: &mut ParsedFlags,
    long: &str,
) -> Result<()> {
    if let Some(flag) = flags::find_flag_by_long(long) {
        match flag.kind {
            FlagKind::Switch { .. } => {
                apply_overrides(parsed, flag.name);
                parsed.add_switch(flag.name);
            }
            FlagKind::Flag { allow_leading_hyphen, .. } => {
                apply_overrides(parsed, flag.name);
                let value = if allow_leading_hyphen {
                    parser.optional_value()?.unwrap_or_else(|| {
                        OsString::from(parser.next()?.expect("expected value for flag"))
                    })
                } else {
                    parser.value()?
                };
                parsed.add_flag(flag.name, value);
            }
            FlagKind::Positional { .. } => {
                return Err(format!("unexpected positional flag: --{}", long).into());
            }
        }
    } else {
        return Err(lexopt::Error::UnexpectedOption(format!("--{}", long)).into());
    }
    Ok(())
}

fn apply_overrides(parsed: &mut ParsedFlags, flag_name: &str) {
    let overrides = get_overrides_for(flag_name);
    for override_name in overrides {
        if parsed.switches.contains_key(override_name) {
            parsed.switches.remove(override_name);
        }
        if parsed.flags.contains_key(override_name) {
            parsed.flags.remove(override_name);
        }
    }
}

fn get_overrides_for(flag_name: &str) -> &'static [&'static str] {
    match flag_name {
        "case-sensitive" => &["ignore-case", "smart-case"],
        "ignore-case" => &["case-sensitive", "smart-case"],
        "smart-case" => &["case-sensitive", "ignore-case"],
        "no-ignore" => &["ignore"],
        "ignore" => &["no-ignore"],
        "no-ignore-dot" => &["ignore-dot"],
        "ignore-dot" => &["no-ignore-dot"],
        "no-ignore-exclude" => &["ignore-exclude"],
        "ignore-exclude" => &["no-ignore-exclude"],
        "no-ignore-files" => &["ignore-files"],
        "ignore-files" => &["no-ignore-files"],
        "no-ignore-global" => &["ignore-global"],
        "ignore-global" => &["no-ignore-global"],
        "no-ignore-parent" => &["ignore-parent"],
        "ignore-parent" => &["no-ignore-parent"],
        "no-ignore-vcs" => &["ignore-vcs"],
        "ignore-vcs" => &["no-ignore-vcs"],
        "no-ignore-messages" => &["ignore-messages"],
        "ignore-messages" => &["no-ignore-messages"],
        "no-messages" => &["messages"],
        "messages" => &["no-messages"],
        "no-unicode" => &["unicode", "pcre2-unicode"],
        "unicode" => &["no-unicode", "no-pcre2-unicode"],
        "no-pcre2-unicode" => &["pcre2-unicode", "unicode"],
        "pcre2-unicode" => &["no-pcre2-unicode", "no-unicode"],
        "hidden" => &["no-hidden"],
        "no-hidden" => &["hidden"],
        "follow" => &["no-follow"],
        "no-follow" => &["follow"],
        "fixed-strings" => &["no-fixed-strings"],
        "no-fixed-strings" => &["fixed-strings"],
        "crlf" => &["no-crlf", "null-data"],
        "no-crlf" => &["crlf"],
        "null-data" => &["crlf", "no-crlf"],
        "multiline" => &["no-multiline", "stop-on-nonmatch"],
        "no-multiline" => &["multiline"],
        "multiline-dotall" => &["no-multiline-dotall"],
        "no-multiline-dotall" => &["multiline-dotall"],
        "line-number" => &["no-line-number"],
        "no-line-number" => &["line-number"],
        "column" => &["no-column"],
        "no-column" => &["column"],
        "heading" => &["no-heading"],
        "no-heading" => &["heading"],
        "with-filename" => &["no-filename"],
        "no-filename" => &["with-filename"],
        "line-buffered" => &["no-line-buffered", "block-buffered", "no-block-buffered"],
        "no-line-buffered" => &["line-buffered"],
        "block-buffered" => &["no-block-buffered", "line-buffered", "no-line-buffered"],
        "no-block-buffered" => &["block-buffered"],
        "mmap" => &["no-mmap"],
        "no-mmap" => &["mmap"],
        "json" => &["no-json", "count", "count-matches", "files", "files-with-matches", "files-without-match"],
        "no-json" => &["json"],
        "stats" => &["no-stats"],
        "no-stats" => &["stats"],
        "max-columns-preview" => &["no-max-columns-preview"],
        "no-max-columns-preview" => &["max-columns-preview"],
        "trim" => &["no-trim"],
        "no-trim" => &["trim"],
        "glob-case-insensitive" => &["no-glob-case-insensitive"],
        "no-glob-case-insensitive" => &["glob-case-insensitive"],
        "ignore-file-case-insensitive" => &["no-ignore-file-case-insensitive"],
        "no-ignore-file-case-insensitive" => &["ignore-file-case-insensitive"],
        "text" => &["no-text", "binary", "no-binary"],
        "no-text" => &["text"],
        "binary" => &["no-binary", "text", "no-text"],
        "no-binary" => &["binary"],
        "search-zip" => &["no-search-zip", "pre", "no-pre"],
        "no-search-zip" => &["search-zip"],
        "pre" => &["no-pre", "search-zip", "no-search-zip"],
        "no-pre" => &["pre"],
        "auto-hybrid-regex" => &["no-auto-hybrid-regex", "pcre2", "no-pcre2", "engine"],
        "no-auto-hybrid-regex" => &["auto-hybrid-regex"],
        "pcre2" => &["no-pcre2", "auto-hybrid-regex", "no-auto-hybrid-regex", "engine"],
        "no-pcre2" => &["pcre2"],
        "engine" => &["pcre2", "no-pcre2", "auto-hybrid-regex", "no-auto-hybrid-regex"],
        "passthru" => &["after-context", "before-context", "context"],
        "after-context" => &["passthru"],
        "before-context" => &["passthru"],
        "context" => &["passthru"],
        "sort-files" => &["no-sort-files", "sort", "sortr"],
        "no-sort-files" => &["sort-files"],
        "sort" => &["sortr", "sort-files", "no-sort-files"],
        "sortr" => &["sort", "sort-files", "no-sort-files"],
        "count" => &["count-matches"],
        "count-matches" => &["count"],
        "files-with-matches" => &["files-without-match"],
        "files-without-match" => &["files-with-matches"],
        "line-regexp" => &["word-regexp"],
        "word-regexp" => &["line-regexp"],
        "context-separator" => &["no-context-separator"],
        "no-context-separator" => &["context-separator"],
        "one-file-system" => &["no-one-file-system"],
        "no-one-file-system" => &["one-file-system"],
        "no-require-git" => &["require-git"],
        "require-git" => &["no-require-git"],
        _ => &[],
    }
}
