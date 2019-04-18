from docstr_coverage import coverage
import glob

FORMAT = "%-74s %5s  %5s  %3d%%"


# Temp monkeypatch.
# See https://github.com/HunterMcGushion/docstr_coverage/pull/3
def monkeypatched_open(filename, mode):
    return open(filename, mode, encoding="utf-8")


coverage.open = monkeypatched_open
# End of monkeypatch.


def main():
    filenames = glob.glob("**/*.py", recursive=True)
    filenames = [
        filename
        for filename in filenames
        if not (filename.startswith("external")
                or filename.startswith("help")
                or filename.endswith("waterbalance_widget.py")
                or "/test" in filename)
    ]
    file_results, total_results = coverage.get_docstring_coverage(
        filenames,
        skip_magic=True,
        skip_file_docstring=False,
        skip_init=True,
        skip_class_def=False,
        verbose=0,
    )

    for filename in filenames:
        result = file_results.get(filename)
        print(
            FORMAT
            % (
                filename,
                result["needed_count"],
                result["missing_count"],
                result["coverage"],
            )
        )

    print(
        FORMAT
        % (
            "TOTAL",
            total_results["needed_count"],
            total_results["missing_count"],
            total_results["coverage"],
        )
    )


if __name__ == "__main__":
    main()