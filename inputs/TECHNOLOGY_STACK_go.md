# Technology Stack

**Approved:** 2026-10-19

Technology decisions of record for this Target. One row per technology, naming the
Rigging best-practice file that governs building it.

A `—` in the Rigging column means no Rigging guidance exists for that technology; the
builder applies general best practice instead. Adding a row never requires a matching
Rigging file.

This file is owned by the UAT kit. It is seeded into the Target before `analyze`, which
never overwrites it, and `drydock plan` reads it to assign per-story `stack:` guidance.

| Technology | Rigging | Notes |
|---|---|---|
| Go | go.md | Implementation language; Go 1.22 or newer, standard library plus the shipped persistence package. |
| SQLite | sqlite.md | Database, reached through the shipped persistence library. |
| go test | go.md | Test runner behind `bin/test.sh`. |
| Shell | common.md | POSIX sh for `bin/test.sh` and the supplied grader. |
