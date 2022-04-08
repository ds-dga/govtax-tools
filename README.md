

# Updates

## tables needed an improvement.


    ALTER TABLE gfmis_fund_center_name ALTER fund_center SET DATA TYPE text;

    ALTER TABLE gfmis_fund_center_name ADD CONSTRAINT yearly_bb_code UNIQUE (budget_year, fund_center);