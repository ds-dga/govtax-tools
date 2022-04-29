import csv
from gfmis.utils import THAI_MONTH_CONV, printProgressBar, wc_like
import os

ANNUAL_PAY_COLS = [
    "budget_year",
    "transaction_year",
    "transaction_month",
    "min",
    "agc",
    "province",
    "nfunc",
    "objc",
    "fund",
    "budget_amount",
    "adjust_amount",
    "amount",
    "percentage_amount",
    "stg",
    "transaction_type",
    "nfunc1",
    "nfunc2",
]


def raw2row(raw, wantedType="bulk_insert"):
    """GFMIS raw data to ready-to-insert row

    ## raw data

    "รหัสยุทธศาสตร์การจัดสรร"|"รหัสหน่วยงาน"|"รหัสจังหวัด (พื้นที่)"|"รหัสลักษณะงาน"|"รหัสหมวดรายจ่าย"|"รหัสงบประมาณ"|"เดือน/ปีงบประมาณ"|"รหัสรายจ่ายประจำ/ลงทุน"|"พรบ. (บาท)"|"งบฯ หลังโอน/ปป. ทั้งสิ้น (บาท)"|"เบิกจ่ายทั้งสิ้น (YTM) (บาท)"|"%เบิกจ่าย YTM ต่องบฯ หลังโอน/ปป.ทั้งสิ้น"
    "07"|"97001"|"1000"|"0112"|"500"|"9700166002"|"ต.ค. 2565"|"1"|"24978560000.00"|"24978560000.00"|"24960670000.00"|"99.93"

    """
    row = [i.strip() for i in raw]
    strategy, agc, province, nfunc = row[0], row[1], row[2], row[3]
    objc, fund, th_mmyy, tx_type = row[4], row[5], row[6], row[7]
    budget_amount, adj_amount = row[8], row[9]
    amount, percentage_amount = row[10], row[11]

    """
    INSERT into gfmis_transaction
    (budget_year, transaction_year, transaction_month, min, agc, province, nfunc, objc, fund, budget_amount, adjust_amount, amount, percentage_amount, stg, transaction_type, nfunc1, nfunc2)

        $stg = str_to_utf8(trim($row[0]));
        $agc = str_to_utf8(trim($row[1]));
        $province = str_to_utf8(trim($row[2]));
        $nfunc = str_to_utf8(trim($row[3]));
        $objc = str_to_utf8(trim($row[4]));
        $fund = str_to_utf8(trim($row[5]));
        $rawTransactionDate = str_to_utf8(trim($row[6])); // ต.ค. 2564
        $type = str_to_utf8(trim($row[7]));
        $budgetAmount = str_replace(",", "", str_to_utf8(trim($row[8])));
        $adjustAmount = str_replace(",", "", str_to_utf8(trim($row[9])));
        $amount = str_replace(",", "", str_to_utf8(trim($row[10])));
        $percentageAmount = str_replace(",", "", str_to_utf8(trim($row[11])));
        $nfunc1 = str_to_utf8(substr($nfunc, 0, 2));
        $nfunc2 = str_to_utf8(substr($nfunc, 0, 3));

        $transaction = explode(' ', $rawTransactionDate);
        $budgetYear = intval($transaction[1]);
        $transactionMonth = getMonthValueFromAbbr($transaction[0]);

        $transactionYear = $transactionMonth > 9 ? $budgetYear - 1 : $budgetYear;
        $transactionYear = strval($transactionYear);

        $min = substr($agc, 0, 2) . '000';

        if ($stg == '0') {
            $stg = '#';
        } else if (strlen($stg) <= 2 && $stg != '#') {
            $stg = str_pad(strval($stg), 2, '0', STR_PAD_LEFT);
        }

        $content = '';
        if($row_num > 3 && ($row_num % 50000 != 1)){
        $content .= ','.PHP_EOL;
        }
        $content .= "('". $year . "','" . $transactionYear . "','" . $transactionMonth . "','" . $min . "','" . $agc . "','" . $province . "','" . $nfunc . "','" . $objc . "','" . $fund . "'," . floatval($budgetAmount)
                        . "," . floatval($adjustAmount) . "," . floatval($amount) . "," . floatval($percentageAmount) . ",'" . $stg . "'," . $type . ",'" . $nfunc1 . "','" . $nfunc2 . "')";

    """
    # "ต.ค. 2565" --> month, budget_year
    th_mo, budget_year = th_mmyy.split()
    mm = THAI_MONTH_CONV[th_mo]
    th_yr = budget_year
    if int(mm) > 9:
        th_yr = int(budget_year) - 1

    ministry_code = f"{agc[:2]}000"
    # extra process
    # (1) get rid of comma
    budget_amount = budget_amount.replace(",", "")
    adj_amount = adj_amount.replace(",", "")
    amount = amount.replace(",", "")
    percentage_amount = percentage_amount.replace(",", "")
    # (2) nfunc1 รหัสลักษณะงาน ระดับที่ 1 / nfunc2 รหัสลักษณะงาน ระดับที่ 2
    nfunc1, nfunc2 = nfunc[:2], nfunc[:3]
    if wantedType == "dict":
        one = {
            "budget_year": budget_year,  # ปีงบ
            "transaction_year": th_yr,  # ปี
            "transaction_month": mm,  # เดือน
            "min": ministry_code,
            "agc": agc,  # รหัสหน่วยงาน
            "province": province,
            "nfunc": nfunc,  # รหัสลักษณะงาน
            "objc": objc,  # รหัสหมวดรายจ่าย
            "fund": fund,  # รหัสงบประมาณ
            "budget_amount": budget_amount,  # วงเงินงบประมาณตาม พ.ร.บ.
            "adjust_amount": adj_amount,  # งบประมาณหลังโอน / เปลี่ยนแปลงทั้งสิ้น
            "amount": amount,  # ยอดเงินการเบิกจ่ายทั้งสิ้น
            "percentage_amount": percentage_amount,  # ร้อยละการเบิกจ่าย ต่อ งบประมาณหลังโอน / เปลี่ยนแปลงทั้งสิ้น
            "stg": strategy,  # รหัสยุทธศาสตร์
            "transaction_type": tx_type,  # ประเภทของรายการเบิกจ่าย
            "nfunc1": nfunc1,  # รหัสลักษณะงาน ระดับที่ 1
            "nfunc2": nfunc2,  # รหัสลักษณะงาน ระดับที่ 1
        }
        return one

    # if wantedType == 'bulk_insert':
    bulk_ins_items = f"\n('{budget_year}','{th_yr}','{mm}','{ministry_code}','{agc}','{province}','{nfunc}','{objc}','{fund}','{budget_amount}','{adj_amount}','{amount}','{percentage_amount}','{strategy}','{tx_type}','{nfunc1}','{nfunc2}')"

    return bulk_ins_items


def annualpay_query(items):
    txt = f"""--\n\nINSERT INTO gfmis_transaction (budget_year, transaction_year, transaction_month, min, agc, province, nfunc, objc, fund, budget_amount, adjust_amount, amount, percentage_amount, stg, transaction_type, nfunc1, nfunc2) VALUES {','.join(items)}
    -- ON CONFLICT ON CONSTRAINT gf_tx_unique DO UPDATE SET
    --    adjust_amount = EXCLUDED.adjust_amount,
    --    amount = EXCLUDED.amount,
    --    percentage_amount = EXCLUDED.percentage_amount
    ;\n\n--"""
    return txt


def annual_pay_converter(fp):
    total = wc_like(fp)
    count = 1
    budget_year = None
    results = []
    lines = []
    with open(fp, "rt", encoding="iso-8859-11") as f:
        cf = csv.reader(f, delimiter="|")
        next(cf)  # skip header
        for row in cf:
            if row[0] == "Grand Total":
                continue

            if budget_year is None:
                h = raw2row(row, "dict")
                budget_year = h["budget_year"]

            one = raw2row(row)
            results.append(one)

            if len(results) % 30000 == 0:
                txt = annualpay_query(results)
                lines.append(txt)
                results = []

            count += 1

            printProgressBar(
                count + 1,
                total,
                prefix="Progress:",
                suffix=f"{budget_year}",
                length=50,
            )

        if results:  # leftover clean up
            txt = annualpay_query(results)
            lines.append(txt)
            results = []

    if lines:
        base_path = 'output'
        if not os.path.exists(base_path):
            os.mkdir('output')

        out_path = os.path.join(base_path, f'annual_pay_{budget_year}.sql')
        if os.path.exists(out_path):
            of = open(out_path, "at", encoding="utf-8")
        else:
            of = open(out_path, "wt", encoding="utf-8")
            of.write(f"--\n")
            of.write(f"-- delete the existing data first before adding new stuffs\n")
            of.write(f"--\n\n")
            of.write(
                f"DELETE FROM gfmis_transaction WHERE budget_year = '{budget_year}';\n"
            )
            of.write(f"--\n")
            of.write(f"--\n\n")

        of.write("--\n")
        of.writelines(lines)
        of.write("--- EOF ---")
        of.close()
