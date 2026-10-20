## Project Overview

Command-line cash ledger with a root `ledger` executable.

## Architecture

Python 3.11+, with CLI, configuration, services, validation, and persistence boundaries. The
`persistence` package is the only database access boundary.

## Dev Commands

```sh
./bin/test.sh
./ledger init
./ledger count
```

## Service Endpoints

None; this is a command-line application.

## Bookmarks

None.

