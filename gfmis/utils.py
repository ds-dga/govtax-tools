from datetime import datetime
import subprocess


def get_git_revision_short_hash() -> str:
    try:
        return (
            subprocess.check_output(["git", "rev-parse", "--short", "HEAD"])
            .decode("ascii")
            .strip()
        )
    except:
        return "-"


def insert_src_update_query(fp, output_file, src, note=""):
    # get mtime from file
    mod_datetime = datetime.fromtimestamp(os.path.getmtime(fp))
    output_file.write("-- INSERT data_source_update \n\n")
    _procr = f"govtax-tools:{get_git_revision_short_hash()}"
    output_file.write(
        f"""
        INSERT INTO data_source_update
            (created_at, source, note, processor) VALUES
            ('{mod_datetime.isoformat()}', '{src}', '{note} '{_procr}');
    """
    )


# Print iterations progress
def printProgressBar(
    iteration,
    total,
    prefix="",
    suffix="",
    decimals=1,
    length=100,
    fill="█",
    printEnd="\r",
):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + "-" * (length - filledLength)
    print(f"\r{prefix} |{bar}| {percent}% {suffix}", end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()


def wc_like(fp):
    # open file in read mode
    with open(fp, "rt", encoding="iso-8859-11") as fp:
        for count, line in enumerate(fp):
            pass
    return count + 1


THAI_MONTH_CONV = {
    "ม.ค.": 1,
    "ก.พ.": 2,
    "มี.ค.": 3,
    "เม.ย.": 4,
    "พ.ค.": 5,
    "มิ.ย.": 6,
    "ก.ค.": 7,
    "ส.ค.": 8,
    "ก.ย.": 9,
    "ต.ค.": 10,
    "พ.ย.": 11,
    "ธ.ค.": 12,
}
