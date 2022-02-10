import os
import psycopg2


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
