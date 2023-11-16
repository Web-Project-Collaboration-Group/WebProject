from flask import Flask, render_template, request, url_for, redirect, session

from dbSqlite3 import *

app = Flask(__name__)
app.secret_key = 'abcdefgh!@#$%'


def CheckLogin():
    if 'userid' not in session:
        return False
    else:
        return True


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        return render_template('login.html')
    if 1 == 1:

        result, _ = GetSql2(
            "select * from users where username='%s' and pwd='%s'" % (request.form['username'], request.form['pwd']))
        print(result)
        if len(result) > 0:
            session["userid"] = result[0][0]
            return redirect(url_for('/'))
        else:
            return render_template('login.html')


@app.route('/', methods=['GET'])
@app.route('/<id>/', methods=['GET'])
def index(id=None):
    global index_page
    index_page = 1

    tablename = "student_info"
    items_per_page = 15  # 每页显示的数据条数

    # 查询数据的总条数
    total_items_sql = f"SELECT COUNT(*) FROM student_info"
    total_items_result, _ = GetSql2(total_items_sql)
    total_items = total_items_result[0][0]

    # 计算总页数
    total_pages = (total_items + items_per_page - 1) // items_per_page

    if id is not None:
        if int(id) == 0:
            index_page = 1
        elif int(id) >= total_pages:
            index_page = total_pages
        else:
            index_page = int(id)

    if not CheckLogin():
        return redirect(url_for('login'))

    # 计算每个数据集的起始位置和结束位置
    start_index = (index_page - 1) * items_per_page
    end_index = start_index + items_per_page

    sql = f"SELECT s.*,  p.stu_profession FROM student_info s INNER JOIN stu_profession p " \
          f"on s.stu_profession_id=p.stu_profession_id LIMIT {start_index}, {items_per_page}"

    strWhere = []
    if "name" in request.args:
        name = request.args["name"]
        if name != "":
            strWhere.append(f"stu_name LIKE '%%%s%%'" % name)

    if "stuno" in request.args:
        stuno = request.args["stuno"]
        if stuno != "":
            strWhere.append(f"stu_id = '%s'" % stuno)

    if len(strWhere) > 0:
        sql = sql + " WHERE " + " AND ".join(strWhere)
        print(sql)

    result, fields = GetSql2(sql)
    return render_template('show1.html', datas=result, fields=fields, index_page=index_page, total_pages=total_pages)



@app.route('/add', methods=['GET', 'post'])
def add():
    if not CheckLogin():
        return redirect(url_for('login'))

    if request.method == "GET":
        datas, _ = GetSql2("select * from stu_profession")
        return render_template('add.html', datas=datas)

    else:
        data = dict(
            stu_id=request.form['stu_id'],
            stu_name=request.form['stu_name'],
            stu_sex=request.form['stu_sex'],
            stu_age=request.form['stu_age'],
            stu_origin=request.form['stu_origin'],
            stu_profession_id=request.form['stu_profession']
        )

        InsertData(data, "student_info")
        return redirect(url_for('index', id=index_page))


@app.route('/del2/<idi>', methods=['GET'])
def delete2(idi):
    if not CheckLogin():
        return redirect(url_for('login'))
    DelDataById("stu_id", idi, "student_info")
    return redirect(url_for('index', id=index_page))


@app.route('/update', methods=['GET', 'post'])
def update():
    if not CheckLogin():
        return redirect(url_for('login'))

    if request.method == "GET":
        id = request.args['id']
        result, _ = GetSql2("select * from student_info where stu_id='%s'" % id)
        # result, _ = GetSql2("SELECT s.*,  p.stu_profession FROM student_info s INNER JOIN stu_profession p " \
        #                     "on s.stu_profession_id=p.stu_profession_id where stu_id='%s'" % id)
        print(result[0])
        print(type(result[0]))
        datas, _ = GetSql2("select * from stu_profession")
        # for p in pro:
        #     print(p)+
        return render_template('update.html', data=result[0], datas=datas)
    else:

        data = dict(
            stu_id=request.form['stu_id'],
            stu_name=request.form['stu_name'],
            stu_sex=request.form['stu_sex'],
            stu_age=request.form['stu_age'],
            stu_origin=request.form['stu_origin'],
            stu_profession_id=request.form['stu_profession']
        )
        UpdateData(data, "student_info")

        return redirect(url_for('index'))


if __name__ == '__main__':
    # app.run("0.0.0.0",debug=True)
    app.run(debug=True)
    # app.run()
