""" basically this handles the GFMIS incoming data and turns into another CSV
for BULK INSERT or bunches of INSERT ... I'm not sure yet. We might need to
try both and let the performance talk

There are 3 files:
1. DGA_AnnualPay_01.csv
2. DGA_AnnualPay_02.csv
3. MIS_FCTR_LONG_TEXT.csv
"""
import os
import csv

from .utils import printProgressBar


def check_fieldnames(fp):
    """check if fieldnames are valid for particular file

    Args:
        fp (str): file path

    Returns:
        bool: return if the file is valid
        list: return the valid headers, [] if invalid
    """
    MIS_FCTR_HEADERS = (
        '"รหัสงบประมาณ"|"วันที่สิ้นสุด"|"วันที่เริ่มต้น"|"ชื่อรหัสงบประมาณ"'
    )
    DGA_ANNUALPAY_HEADERS = '"รหัสยุทธศาสตร์การจัดสรร"|"รหัสหน่วยงาน"|"รหัสจังหวัด (พื้นที่)"|"รหัสลักษณะงาน"|"รหัสหมวดรายจ่าย"|"รหัสงบประมาณ"|"เดือน/ปีงบประมาณ"|"รหัสรายจ่ายประจำ/ลงทุน"|"พรบ. (บาท)"|"งบฯ หลังโอน/ปป. ทั้งสิ้น (บาท)"|"เบิกจ่ายทั้งสิ้น (YTM) (บาท)"|"%เบิกจ่าย YTM ต่องบฯ หลังโอน/ปป.ทั้งสิ้น"'
    headers = None
    title = ""
    if fp.find("DGA_AnnualPay") > -1:
        headers = DGA_ANNUALPAY_HEADERS
        title = "DGA_AnnualPay"
    elif fp.find("MIS_FCTR_LONG_TEXT") > -1:
        headers = MIS_FCTR_HEADERS
        title = "MIS_FCTR_LONG_TEXT"

    if not headers:
        return False, "", []

    headers = headers.replace('"', "").split("|")
    # print(f'[CHECK] file path: {fp}')
    row = False
    with open(fp, "rt", encoding="iso-8859-11") as f:
        cf = csv.reader(f, delimiter="|")
        row = next(cf)
        # print("HEADER : ", row)
    return row == headers, title, headers


def handle_gfmis_dir(fp, **kw):
    """handle dir will check all the files if applicable at all.

    Args:
        fp (str): file path
    """
    if not fp:
        raise Exception("No path provided")

    verbose = save2db = False
    if "args" in kw:
        verbose = kw["args"].print
        save2db = kw["args"].db

    for _base, dirs, fs in os.walk(fp):
        for f in fs:
            full_path = os.path.join(_base, f)
            valid, title, headers = check_fieldnames(full_path)
            print(f'[{valid and "/" or "X"}] {f} -- {",".join(headers)}')
            if not valid:
                continue

            if title == "DGA_AnnualPay":
                # annual_pay_converter(full_path, headers)
                print()
            elif title == "MIS_FCTR_LONG_TEXT":
                mis_fctr_converter(full_path, headers)
                print()


def wc_like(fp):
    # open file in read mode
    with open(fp, "rt", encoding="iso-8859-11") as fp:
        for count, line in enumerate(fp):
            pass
    return count + 1


def annual_pay_converter(fp, headers):
    total = wc_like(fp)
    count = 1
    with open(fp, "rt", encoding="iso-8859-11") as f:
        cf = csv.reader(f, delimiter="|")
        next(cf)  # skip header

        for row in cf:
            if row[0] == "Grand Total":
                continue
            printProgressBar(
                count + 1, total, prefix="Progress:", suffix="DONE", length=50
            )
            count += 1


MIS_FCTR_COLS = ["budget_year", "fund_center", "name"]


def mis_fctr_converter(fp, headers):
    total = wc_like(fp)
    count = 1
    budget_year = None
    of = None
    with open(fp, "rt", encoding="iso-8859-11") as f:
        cf = csv.reader(f, delimiter="|")
        next(cf)  # skip header
        for row in cf:
            start, end = row[2], row[1]
            bb_code, title = row[0], row[3]
            y1, y2 = int(start[:4]), int(end[:4])
            if y1 < y2:
                budget_year = y2 + 543

            if not budget_year:
                continue

            if of is None:
                of = open(f"./mis_fctr_{budget_year}.csv", "wt", encoding="utf-8")
                output = csv.DictWriter(of, fieldnames=MIS_FCTR_COLS)
                output.writeheader()

            row = {
                "fund_center": bb_code,
                "name": title,
                "budget_year": budget_year,
            }
            # print(row)
            output.writerow(row)
            printProgressBar(
                count + 1,
                total,
                prefix="Progress:",
                suffix=f"{start[:4]}-{end[:4]}-{budget_year}",
                length=50,
            )
            count += 1
