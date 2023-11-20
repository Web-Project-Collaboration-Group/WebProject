# -*- coding: utf-8 -*-
import sqlite3

def OpenDb():
    database = "./db/student_083_2.db"
    conn = sqlite3.connect(database)
    return conn



def GetSql(conn, sql):

    cur = conn.cursor()
    cur.execute(sql)
    fields=[]
    for field in cur.description:
        fields.append(field[0])

    result = cur.fetchall()
    # for item in result:
    #     print(item)
    cur.close()
    return result,fields


def CloseDb(conn):
    conn.close()


def GetSql2(sql):
    conn = OpenDb()
    result,fields = GetSql(conn, sql)
    CloseDb(conn)
    return result,fields


def UpdateData(data, tablename):
    conn = OpenDb()
    values = []
    cusor = conn.cursor()
    idName = list(data)[0]
    
    try:
        for v in list(data)[1:]:
            values.append("%s='%s'" % (v, data[v]))
        sql = "update %s set %s where %s='%s'" % (tablename, ",".join(values), idName, data[idName])
        cusor.execute(sql)
        conn.commit()
        CloseDb(conn)
        return True, "更新成功"
    except Exception as e:
        # 如果发生异常，返回更新失败信息
        CloseDb(conn)
        return False, "更新失败: {}".format(str(e))

def UpdateAge(id, age):
    conn = OpenDb()
    cusor = conn.cursor()
    sql = "update student_info set stu_age=? where stu_id=?"
    cusor.execute(sql, (age, id))
    conn.commit()
    CloseDb(conn)


def InsertData(data, tablename):
    conn = OpenDb()
    values = []
    cursor = conn.cursor()
    fieldNames = list(data)
    for v in fieldNames:
        values.append(data[v])
    
    try:
        sql = "insert into %s (%s) values(%s)" % (tablename, ",".join(fieldNames), ",".join(["?"] * len(fieldNames)))
        cursor.execute(sql, values)
        conn.commit()
        CloseDb(conn)
        return True, None  # 返回成功的标志和无错误消息
    except sqlite3.IntegrityError as e:
        if "UNIQUE constraint failed" in str(e):
            # 处理主键冲突异常
            CloseDb(conn)
            return False, "学号已存在，请使用其他学号"
        else:
            conn.rollback()
            CloseDb(conn)
            return False, str(e)  # 返回失败的标志和错误消息



def DelDataById(id, value, tablename):
    conn = OpenDb()
    values = []
    cusor = conn.cursor()

    sql = "delete from %s  where %s=?" % (tablename, id)
    # print (sql)

    cusor.execute(sql,(value,))
    conn.commit()
    CloseDb(conn)

def GetStudentNameById(student_id):
    conn = OpenDb()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT stu_name FROM student_info WHERE stu_id = ?", (student_id,))
        result = cursor.fetchone()

        if result:
            return result[0]  
        else:
            return None  
    finally:
        CloseDb(conn)
