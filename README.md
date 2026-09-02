# git-annex-duplicates

Find duplicate file paths in a [git-annex](https://git-annex.branchable.com/)
repository.

`git-annex-duplicates` groups files by their annex key and prints every group
that contains more than one path. It is read-only: it reports duplicates but
does not remove or otherwise modify any files.


## Requirements

- git-annex
- Python 3.11 or newer
- [uv](https://docs.astral.sh/uv/) (recommended for installation)


## Installation

Install the command directly from the Git repository:

```sh
uv tool install "git+https://cvs.moegen-wir.net/mikegerber/git-annex-duplicates.git"
```

Alternatively, run it from a checkout:

```sh
git clone https://cvs.moegen-wir.net/mikegerber/git-annex-duplicates.git
cd git-annex-duplicates
uv run git-annex-duplicates --help
```


## Usage

Run the command from inside a git-annex repository:

```sh
git-annex-duplicates
```

The output contains one group of duplicate paths at a time, with groups
separated by a blank line:

```text
photos/holiday.jpg
backup/holiday.jpg

documents/report.pdf
archive/report-final.pdf
```

Exclude one or more path patterns with `--exclude`:

```sh
git-annex-duplicates --exclude '*.iso' --exclude 'archive/**'
```

Additional arguments are passed to `git annex find`. Place `--` before options
that belong to `git annex find`, so they are not interpreted as options to
`git-annex-duplicates`:

```sh
# Only report duplicates whose content is present in this repository
git-annex-duplicates -- --in=here

# Combine a local exclusion with a git-annex find option
git-annex-duplicates --exclude 'archive/**' -- --in=here
```

See `git annex find --help` for the available filters.


## How it works

The command runs `git annex find`, requests each file's annex key, groups the
returned paths by that key, and prints groups containing at least two paths.
Files with the same annex key refer to the same content as far as git-annex is
concerned.

Only annexed files are considered. Regular Git files and untracked files are
not included, and file content does not need to be downloaded to produce the
report.
