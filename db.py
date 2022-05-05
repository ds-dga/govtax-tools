import os
import psycopg2
from utils import get_git_revision_short_hash


class Database(object):
    """ """

    def __init__(self, dbconn=None):
        if dbconn is None:
            default_dbconn = "dbname='ckan' user='ckan' host='127.0.0.1' port='35433' password='ckan'"
            dbconn = os.getenv("GOVTAX_DB_URI", default_dbconn)
        self.conn = psycopg2.connect(dbconn)
        self.cursor = self.conn.cursor()

    def get_cursor(self):
        return self.cursor

    def close(self):
        self.conn.close()

    def get_or_create_revenue_dept(self, dept):
        q = f"""SELECT id FROM ref_revenue_department WHERE name = '{dept}' """
        cur = self.cursor
        cur.execute(q)
        item = cur.fetchone()
        if item:
            return item[0]

        q = f"""INSERT INTO ref_revenue_department (name, status)
            VALUES ('{dept}', 'A')
            RETURNING id
        """
        try:
            cur.execute(q)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            print(e, end="\r")
            self.conn.rollback()
            return None

    def get_or_create_revenue_type(self, rtype):
        if not rtype:
            return None
        q = f"""SELECT id FROM ref_revenue_type WHERE name = '{rtype}' """
        cur = self.cursor
        cur.execute(q)
        item = cur.fetchone()
        if item:
            return item[0]

        q = f"""INSERT INTO ref_revenue_type (name, status)
            VALUES ('{rtype}', 'A')
            RETURNING id
        """
        try:
            cur.execute(q)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            print(e, end="\r")
            self.conn.rollback()
            return None

    def get_or_create_revenue_deduct_type(self, rtype):
        if not rtype:
            return None
        q = f"""SELECT id FROM ref_revenue_deduct_type WHERE name = '{rtype}' """
        cur = self.cursor
        cur.execute(q)
        item = cur.fetchone()
        if item:
            return item[0]

        q = f"""INSERT INTO ref_revenue_deduct_type (name, status)
            VALUES ('{rtype}', 'A')
            RETURNING id
        """
        try:
            cur.execute(q)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            print(e, end="\r")
            self.conn.rollback()
            return None

    def insert_revenue_income(
        self, dept_id, rtype_id, budget_year, year, month, amount
    ):
        """The table "revenue_income" should have unique keys

        alter table revenue_income add constraint yyyymm_rtype unique(dept_id, revenue_type_id, year, month);
        """
        q = f"""INSERT INTO revenue_income
        (dept_id, revenue_type_id, budget_year, year, month, amount)
        VALUES ({dept_id}, {rtype_id}, {budget_year}, {year}, {month}, {amount})
        ON CONFLICT do nothing
        RETURNING gid
        """
        try:
            cur = self.cursor
            cur.execute(q)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            print(e, end="\r")
            self.conn.rollback()
            return None

    def insert_revenue_deduct(self, rtype_id, budget_year, year, month, amount):
        """The table "revenue_deduct" should have unique keys

        alter table revenue_deduct add constraint yyyymm_rdtype unique(ref_revenue_deduct_type_id, year, month);
        """
        q = f"""INSERT INTO revenue_deduct
        (ref_revenue_deduct_type_id, budget_year, year, month, amount)
        VALUES ({rtype_id}, {budget_year}, {year}, {month}, {amount})
        ON CONFLICT do nothing
        RETURNING gid
        """
        try:
            cur = self.cursor
            cur.execute(q)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            print(e, end="\r")
            self.conn.rollback()
            return None


    def insert_data_source_update(self, src, note, timestamp=None):
        """The table "revenue_deduct" should have unique keys

        alter table revenue_deduct add constraint yyyymm_rdtype unique(ref_revenue_deduct_type_id, year, month);
        """
        _procr = f'govtax-tools:{get_git_revision_short_hash()}'
        tmsp = timestamp if timestamp is not None else 'NOW()'

        q = f"""INSERT INTO data_source_update
            (created_at, source, note, processor) VALUES
            ('{tmsp}', '{src}', '{note}', '{_procr}')
            ON CONFLICT do nothing
            RETURNING id
            ;
        """
        try:
            cur = self.cursor
            cur.execute(q)
            self.conn.commit()
            return cur.fetchone()[0]
        except Exception as e:
            print(e, end="\r")
            self.conn.rollback()
            return None
