import os
import csv
from gfmis.utils import printProgressBar, wc_like

MIS_FCTR_COLS = ["budget_year", "fund_center", "name"]


def mis_fctr_query(items):
    txt = f"""--\n\nINSERT INTO gfmis_fund_center_name (budget_year, fund_center, name) VALUES {','.join(items)}
    ON CONFLICT ON CONSTRAINT yearly_bb_code DO UPDATE SET name = EXCLUDED.name;\n\n--"""
    return txt


def mis_fctr_converter(fp):
    total = wc_like(fp)
    count = 1
    budget_year = None

    results = []
    lines = []
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

            one = f"\n('{budget_year}','{bb_code}','{title}')"
            results.append(one)

            if len(results) % 25000 == 0:
                txt = mis_fctr_query(results)
                lines.append(txt)
                results = []

            printProgressBar(
                count + 1,
                total,
                prefix="Progress:",
                suffix=f"{start[:4]}-{end[:4]}-{budget_year}",
                length=50,
            )
            count += 1

        if results:  # leftover clean up
            txt = mis_fctr_query(results)
            lines.append(txt)
            results = []

    if lines:

        base_path = 'output'
        if not os.path.exists(base_path):
            os.mkdir('output')

        out_path = os.path.join(base_path, f'mis_fctr_{budget_year}.sql')

        of = open(out_path, "wt", encoding="utf-8")
        of.write("---\n")
        of.writelines(lines)
        of.write("--- EOF ---")
        of.close()
