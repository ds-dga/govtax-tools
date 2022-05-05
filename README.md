# what can we do?

* [revenue](#revenue)
* [gfmis](#gfmis) WIP

## revenue

### requirements

All database related variables should be defined in `.env`

    GOVTAX_DB_URI=dbname='ega_tgs' user='staff' host='127.0.0.1' port='5432' password=''

Then the command to deal with it is. Try to `--print` without `--db` first.

    python main.py revenue --path ~/DGA_ผลการจัดเก็บรายได้ 2565.xlsx --print --db

## GFMIS

From the old code (`~/web/sites/all/modules/tgs/EGA_dev_script.php`), it's obvious that old data will be purge before doing anything.

```php
if(in_array($type, array('gf_transaction', 'gf_transaction_new'))){
    output(date("Y/m/d H:i:s").' info --- delete gfmis_transaction (budget_year = '. $year .')');
    $result = pg_query(sprintf("DELETE FROM gfmis_transaction WHERE budget_year = '%s';", $year));
    if ($result) {
        output(date('Y/m/d H:i:s').'--------- end --- delete gfmis_transaction (budget_year = '. $year .')');
    } else {
        $error = pg_last_error($pg_link);
        output(date('Y/m/d H:i:s').'--------- ERROR --- '. $error);
        output(date('Y/m/d H:i:s').'--------- ERROR --- delete gfmis_transaction (budget_year = '. $year .')');
    }
}
```

### govtax version

The procedure is much cleaner, yet it's not yet one-command to rule them all. As of Apr 29, 2022, there will be 2 steps as follows

1. compile GFMIS data to sql files (annual_pay_YYYY.sql & mis_fctr_YYYY.sql)

        python main.py gfmis --path <raw data from GFMIS at that time>

2. push those SQL commands to DB

        cat output/annual_pay_YYYY.sql | psql -hHOST -pPORT -dDB_NAME -Ustaff


### Updates

#### tables needed an improvement.


    ALTER TABLE gfmis_fund_center_name ALTER fund_center SET DATA TYPE text;

    ALTER TABLE gfmis_fund_center_name ADD CONSTRAINT yearly_bb_code UNIQUE (budget_year, fund_center);

    ALTER TABLE gfmis_transaction ALTER fund_center SET DATA TYPE text;

    ALTER TABLE gfmis_transaction ADD CONSTRAINT gf_tx_unique UNIQUE (fund, objc, nfunc, transaction_year, transaction_month, transaction_type, province);

    ALTER TABLE gfmis_tx ADD CONSTRAINT gf_tx_unique UNIQUE (fund, objc, nfunc, transaction_year, transaction_month, transaction_type, province);




select * from gfmis_transaction where fund = '1600317002701008' and objc = '500' and transaction_year = '2559' and transaction_month = '09' and province = '1000' order by transaction_year, transaction_month;


select * from gfmis_transaction where fund = '0900298002' and objc = '220' and transaction_year = '2559' and transaction_month = '08' and province = '3000' and adjust_amount = '0' order by transaction_year, transaction_month;

select * from gfmis_transaction where fund = '2000404002410?4?' and objc = '320' and nfunc = '0912' and transaction_year = '2559' and transaction_month = '08' and province = '1000' and adjust_amount = '500000' order by transaction_year, transaction_month;


select * from gfmis_transaction where fund = '1500858042600H82' and objc = '420' and nfunc = '0421' and transaction_year = '2562' and transaction_month = '09' and province = '1000' order by transaction_year, transaction_month;


select * from gfmis_transaction where fund = '90909730160105??' and objc = '410' and nfunc = '0160' and transaction_year = '2559' and transaction_month = '09' and province = '5600' and transaction_type = '1' order by transaction_year, transaction_month, transaction_type, amount desc;


select * from gfmis_transaction where fund = '90909730160105??' and objc = '410' and nfunc = '0160' and transaction_year = '2559' and transaction_month = '09' and province = '5600' and transaction_type = '1' order by transaction_year, transaction_month, transaction_type, amount desc;


(fund, objc, nfunc, transaction_year, transaction_month, transaction_type, province)=(90909730160105??, 410, 0160, 2559, 09, 1, 5600)


### Pre govtax-tools

This is what Metamedia did for each file.

#### MIS_FCTR_LONG_TEXT.csv

##### source

    "รหัสงบประมาณ"|"วันที่สิ้นสุด"|"วันที่เริ่มต้น"|"ชื่อรหัสงบประมาณ"
    "01001010014003220001"|"20220930"|"20211001"|"ค่าก่อสร้างอาคารของกองทัพบก เขตวังทองหลาง กรุงเทพมหานคร"

##### result (SQL)

    UPDATE gfmis_fund_center_name SET name = 'เงินสำรอง เงินสมทบ และเงินชดเชยของข้าราชการ' WHERE fund_center = '9090960004' AND budget_year = 2565;
    INSERT INTO gfmis_fund_center_name (fund_center, name, budget_year) SELECT '9090960004', 'เงินสำรอง เงินสมทบ และเงินชดเชยของข้าราชการ', 2565 WHERE NOT EXISTS (SELECT 1 FROM gfmis_fund_center_name WHERE fund_center = '9090960004' AND budget_year = 2565);



#### DGA_AnnualPay_01.csv

##### source

    "รหัสยุทธศาสตร์การจัดสรร"|"รหัสหน่วยงาน"|"รหัสจังหวัด (พื้นที่)"|"รหัสลักษณะงาน"|"รหัสหมวดรายจ่าย"|"รหัสงบประมาณ"|"เดือน/ปีงบประมาณ"|"รหัสรายจ่ายประจำ/ลงทุน"|"พรบ. (บาท)"|"งบฯ หลังโอน/ปป. ทั้งสิ้น (บาท)"|"เบิกจ่ายทั้งสิ้น (YTM) (บาท)"|"%เบิกจ่าย YTM ต่องบฯ หลังโอน/ปป.ทั้งสิ้น"
    "Grand Total"|"Grand Total"|"Grand Total"|"Grand Total"|"Grand Total"|"Grand Total"|"Grand Total"|"Grand Total"|"3100000000000.00"|"3100000000000.01"|"1589924161283.16"|"51.29"
    "#"|"03007"|"1000"|"0112"|"150"|"0300714702000000"|"พ.ย. 2565"|"1"|"0.00"|"0.00"|"936475.00"|"0.00"
    "#"|"03007"|"1000"|"0112"|"150"|"0300714702000000"|"ธ.ค. 2565"|"1"|"0.00"|"0.00"|"-936475.00"|"0.00"
    ...

    "01"|"01008"|"1000"|"0160"|"500"|"0100804019700005"|"มี.ค. 2565"|"1"|"0.00"|"0.00"|"151420.00"|"0.00"
    "01"|"01008"|"1000"|"0160"|"500"|"0100804019700006"|"ต.ค. 2565"|"1"|"4078600.00"|"4078600.00"|"45000.00"|"1.10"
    "01"|"01008"|"1000"|"0160"|"500"|"0100804019700006"|"พ.ย. 2565"|"1"|"0.00"|"0.00"|"45000.00"|"0.00"
    ...
    "07"|"90909"|"9600"|"0760"|"200"|"9090962043000182"|"มี.ค. 2565"|"1"|"0.00"|"22951500.00"|"0.00"|"0.00"
    "07"|"95001"|"1000"|"0160"|"500"|"9500164001"|"ต.ค. 2565"|"1"|"596666700.00"|"596666700.00"|"596666692.00"|"100.00"
    "07"|"97001"|"1000"|"0112"|"500"|"9700166002"|"ต.ค. 2565"|"1"|"24978560000.00"|"24978560000.00"|"24960670000.00"|"99.93"

##### result (SQL)

    INSERT INTO gfmis_transaction (budget_year, transaction_year, transaction_month, min, agc, province, nfunc, objc, fund, budget_amount, adjust_amount, amount, percentage_amount, stg, transaction_type, nfunc1, nfunc2) VALUES
        ('2565','2564','10','01000','01001','1000','0111','200','0100101042000000',0,0,0,0,'01',1,'01','011'),
        ('2565','2564','10','01000','01001','1000','0111','210','0100101042000000',2409900,2409900,0,0,'01',1,'01','011'),
        ('2565','2564','10','01000','01001','1000','0111','220','0100101042000000',1845800,1845800,0,0,'01',1,'01','011'),




#### DGA_AnnualPay_02.csv

##### source

    "รหัสยุทธศาสตร์การจัดสรร"|"รหัสหน่วยงาน"|"รหัสจังหวัด (พื้นที่)"|"รหัสลักษณะงาน"|"รหัสหมวดรายจ่าย"|"รหัสงบประมาณ"|"เดือน/ปีงบประมาณ"|"รหัสรายจ่ายประจำ/ลงทุน"|พรบ. (บาท)|งบฯ หลังโอน/ปป. ทั้งสิ้น (บาท)|เบิกจ่ายทั้งสิ้น (YTM) (บาท)|%เบิกจ่าย YTM ต่องบฯ หลังโอน/ปป.ทั้งสิ้น

##### result (SQL)

remains to be seen