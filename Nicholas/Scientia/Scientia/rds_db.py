import pymysql


conn = pymysql.connect(
        host= 'tip-db.cjmc081jd1av.us-east-1.rds.amazonaws.com',
        port = 3306,
        user = 'admin',
        password = '123123123',
        db = 'Tipping')

#conn = pymysql.connect('tip-db.cjmc081jd1av.us-east-1.rds.amazonaws.com', 'admin', '123123123')




def insert_details(tname,amount):
    cur=conn.cursor()
    cur.execute("insert into Tips (tname,amount) values (%s,%s)", (tname,amount))
    conn.commit()

def get_details():
    cur=conn.cursor()
    cur.execute("select * from Tips")
    tips = cur.fetchall()
    return tips