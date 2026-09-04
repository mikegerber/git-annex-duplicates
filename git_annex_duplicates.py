import collections
import subprocess
from pathlib import Path

import click


def collect_files(exclude, directories):
    # build command
    find_cmd = [
        "git",
        "annex",
        "find",
        "--include",
        "*",
        "--format=${key}:${file}\n",
        *directories,
    ]
    for e in exclude:
        find_cmd += ["--exclude", e]

    # run
    result = subprocess.run(find_cmd, capture_output=True, check=True)

    # collect output
    files = collections.defaultdict(list)
    for l in result.stdout.decode("utf-8").split("\n"):
        if l == "":
            continue
        key, file = l.split(":", maxsplit=1)

        files[key].append(file)

    return files


def print_files(fs):
    for f in fs:
        print(f)


def resolve_parent(p):
    return p.parent.resolve() / p.stem


@click.command()
@click.option("--exclude", multiple=True, default=[])
@click.option("--across", is_flag=True, default=False)
@click.argument(
    "directories",
    nargs=-1,
    default=["."],
    type=click.Path(exists=True, file_okay=False, path_type=Path),
)
def main(exclude, across, directories):

    if across and len(directories) < 2:
        raise click.UsageError("--across requires at least two directories")

    directories = [d.resolve() for d in directories]  # for is_relative_to()

    files = collect_files(exclude, directories)

    for k in files:
        if len(files[k]) > 1:
            if not across:
                print_files(files[k])
                print()
            else:
                # A file is a duplicate across the directories iff it's in more than one
                # directory.
                count = 0
                found_across = False
                for directory in directories:
                    if any(
                        resolve_parent(Path(f)).is_relative_to(directory)
                        for f in files[k]
                    ):
                        count += 1

                    if count > 1:
                        found_across = True
                        break
                if found_across:
                    print_files(files[k])
                    print()


if __name__ == "__main__":
    main()
