import time
import click

from pathlib import Path
from progressbar import Bar, Percentage, ProgressBar


@click.group(context_settings=dict(help_option_names=["-h", "--help"]))
def process():
    """
    CLI that provides several file management scripts.
    """
    ...


@process.command(name="deleter")
@click.option(
    "-d",
    "--dry",
    is_flag=True,
    help="Indicates if files are deleted. When set, the script only prints the amount of files that it would delete.",
    type=bool,
)
@click.option(
    "-se",
    "--slave-extension",
    default=".NEF",
    help="Files of the specified extension are deleted if they do not have a matching file with 'master' extension.",
    type=str,
)
@click.option(
    "-me",
    "--master-extension",
    default=".JPG",
    help="Used to define the reference set of files. Slave files will be reduced to a subset of Master files.",
    type=str,
)
@click.option(
    "-w",
    "--work-directory",
    help="Relative path to directory where both sets of files are located.",
)
def deleter(dry, slave_extension, master_extension, work_directory):
    """Deletes slave files in directory which do not have a counterpart in master set."""

    base_dir = Path(__file__).resolve(strict=True).parent
    work_dir = Path.resolve(base_dir / work_directory, strict=True)

    if not work_dir.is_dir():
        raise ValueError(f"Working directory '{work_dir}' does not exist.")

    master_stem_set = set()
    slave_stem_set = set()
    slave_set = set()

    for item in work_dir.iterdir():
        if item.suffix == master_extension:
            master_stem_set.add(item.stem)
        elif item.suffix == slave_extension:
            slave_stem_set.add(item.stem)
            slave_set.add(item)

    union = master_stem_set | slave_stem_set
    intersection = master_stem_set & slave_stem_set
    items_to_delete = union - intersection

    number_of_items_to_delete = len(items_to_delete)
    if number_of_items_to_delete == 0:
        return print(f"Done. Nothing to delete.")

    print(f"Now to deleting {number_of_items_to_delete} files...\n")

    if dry:
        return print(f"Done. Items not deleted, since this was a dry run.")

    count = 0
    with click.progressbar(slave_set) as bar:
        for item in bar:
            if item.stem not in master_stem_set:
                try:
                    item.unlink()
                    time.sleep(0.025)
                    count += 1
                except PermissionError as e:
                    print(f"Failed to unlink {item.stem} due to permission error: {e}")

    print(f"Done. Deleted {count} items out of {number_of_items_to_delete}.")


if __name__ == "__main__":
    process()
