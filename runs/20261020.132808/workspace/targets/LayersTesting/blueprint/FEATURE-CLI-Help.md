# FEATURE: CLI Help

| Field       | Value |
|-------------|-------|
| Version     | 20261020 V1 |
| Description | Print one usage line per command in the stderr usage diagnostic when ledger is run without a valid command. |
| Depends On  | FEATURE-CLI-Dispatch.md |
| Provides    | usage listing on stderr, cli.usage.usage_lines |

## Purpose

When `ledger` is run with no arguments, or with a command that lacks its required sub-verb or
arguments, the usage diagnostic lists every command in the Commands table. The listing is written
to standard error and the exit code is 2. The text lives in `cli/usage.py`, inside the `cli`
package.

## Rules

- `usage_lines()` returns the usage listing as a list of strings with one string per command. It
  has no trailing newline characters.
- The Commands table has 15 rows. The listing has exactly one line for each row.
- Each line contains the command words and a short description, separated by a space.
- The stderr output equals the `usage_lines()` output, one line per entry.
- Standard output stays empty for every usage error.
- No `help` command is added. The word `help` is an unknown command and exits 2.

## Programmatic Acceptance

=== AC help-no-args-exits-2 ===
Intent: Running ledger with no arguments exits 2 and writes nothing to standard output.

from cli.testing import cli_runner

code, out, err = cli_runner()
assert code == 2
assert len(out) == 0
=== END AC help-no-args-exits-2 ===

=== AC help-one-line-per-command ===
Intent: The usage listing has one unique stderr line for each of the 15 rows in the Commands table.

from cli.testing import cli_runner

command_count = 15
code, out, err = cli_runner()
usage = [line for line in err.splitlines() if line.strip()]
print(f"{len(usage)} usage lines")
assert len(usage) == command_count
assert len(set(usage)) == len(usage)
=== END AC help-one-line-per-command ===

=== AC help-stderr-matches-usage-lines ===
Intent: The stderr usage diagnostic is exactly the lines returned by usage_lines.

from cli.testing import cli_runner
from cli.usage import usage_lines

code, out, err = cli_runner()
lines = usage_lines()
assert err.splitlines() == lines
=== END AC help-stderr-matches-usage-lines ===

=== AC help-no-help-command ===
Intent: The word help is not a command, so it exits 2 and writes nothing to standard output.

from cli.testing import cli_runner

code, out, err = cli_runner("help")
assert code == 2
assert len(out) == 0
=== END AC help-no-help-command ===

=== AC help-incomplete-commands ===
Intent: Command words given without their sub-verb or arguments exit 2 with a usage diagnostic on stderr.

from cli.testing import cli_runner

for argv in (("account",), ("txn",), ("report",)):
    code, out, err = cli_runner(*argv)
    assert code == 2
    assert len(out) == 0
    assert len(err.strip()) > 0
=== END AC help-incomplete-commands ===

## User Acceptance

- None.

## Guardrails

- The usage listing never reads the database.
- No `help` command or `--help` option is added by this feature.
- Usage text is written only to standard error.
