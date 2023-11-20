import os

from flask import Flask, render_template, request, url_for, redirect, session
#显示相关信息成功的库
from flask import flash

#实现验证码功能相关库
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import random
import io
import os

from dbSqlite3 import *

app = Flask(__name__)
app.secret_key = 'abcdefgh!@#$%'


def CheckLogin():
    if 'userid' not in session:
        return False
    else:
        return True


def generate_captcha():
    # 生成验证码
    captcha = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))

    # 创建一个Image对象
    image = Image.new('RGB', (150, 50), color='white')

    # 创建Draw对象
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("arial.ttf", size=30)  # 使用字体

    # 在图像上绘制验证码
    for i, char in enumerate(captcha):
        char_color = tuple(random.randint(0, 255) for _ in range(3))
        char_position = (10 + i * 30, 10)
        draw.text(char_position, char, font=font, fill=char_color)

    # 随机划线
    for _ in range(random.randint(2, 5)):
        line_color = tuple(random.randint(0, 255) for _ in range(3))
        line_start = (random.randint(0, 150), random.randint(0, 50))
        line_end = (random.randint(0, 150), random.randint(0, 50))
        draw.line([line_start, line_end], fill=line_color, width=2)

    # 高斯模糊
    image = image.filter(ImageFilter.GaussianBlur(radius=random.uniform(0, 2)))

    # 将图像保存
    image_stream = io.BytesIO()
    image.save(image_stream, format='PNG')
    image_stream.seek(0)
    image.save(os.path.join("static", "captchas", "captcha_image.png"))

    return captcha, image_stream

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        # 生成验证码并将验证码图像保存到session
        captcha, captcha_image = generate_captcha()
        session['captcha'] = captcha

        return render_template('login.html', captcha_image=captcha_image, error=None)

    entered_captcha = request.form['captcha']
    stored_captcha = session.get('captcha')

    if entered_captcha.lower() == stored_captcha.lower():
        # 验证码匹配
        result, _ = GetSql2(
            "select * from users where username='%s' and pwd='%s'" % (request.form['username'], request.form['pwd']))
        print(result)
        if len(result) > 0:
            session["userid"] = result[0][0]
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='用户名或密码错误', captcha_image=generate_captcha()[1])
    else:
        # 验证码不匹配
        return render_template('login.html', error='验证码错误!', captcha_image=generate_captcha()[1])


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
        sql = "SELECT s.*,  p.stu_profession FROM student_info s INNER JOIN stu_profession p " \
          "on s.stu_profession_id=p.stu_profession_id"
        sql = sql + " WHERE " + " AND ".join(strWhere)
        total_pages=1
        print(sql)

    result, fields = GetSql2(sql)
    if result:
        pass
    else:
        flash('找不到结果', 'error')

    fields = ["学号", "姓名", "性别", "年龄", "籍贯", "专业号", "专业"]  # 替换表头
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

        # 调用 InsertData 函数插入数据
        success, error_message = InsertData(data, "student_info")

    if success:
        flash('添加学生成功: {}'.format(request.form['stu_name']), 'success')
    else:
        flash('添加学生失败: {}'.format(error_message), 'error')

    return redirect(url_for('index', id=index_page))



@app.route('/del2/<idi>', methods=['GET'])
def delete2(idi):
    if not CheckLogin():
        return redirect(url_for('login'))
    
    student_name = GetStudentNameById(idi)  # 获取学生姓名
    
    DelDataById("stu_id", idi, "student_info")
    # 在删除成功后，使用 flash 传递消息
    flash('删除学生成功: {}'.format(student_name), 'success')
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
        success, error_message = UpdateData(data, "student_info")

        if success:
            flash('修改学生成功: {}'.format(request.form['stu_name']), 'success')
        else:
            flash('修改学生失败: {}'.format(error_message), 'error')

        return redirect(url_for('index'))

@app.route('/update_s', methods=['GET','POST'])
def update_s():
    if not CheckLogin():
        return redirect(url_for('index'))
    id_str = request.args['id']
    id = id_str.split(',')
    datas = []
    for i in range(0, len(id)):
        datas.append(GetSql2("select stu_id, stu_name from student_info where stu_id='%s'" % id[i])[0])
    return render_template('update_age.html', datas=datas, id=id)


@app.route('/update_s2/<id>', methods=['GET','POST'])
def update_s2(id):
    if not CheckLogin():
        return redirect(url_for('login'))
    if request.method == 'POST':
        id = id.split(',')
        for i in range(0, len(id)):
            UpdateAge(id[i].strip("[]").strip(" ").strip("'"), list(request.form.to_dict().values())[i])
        return redirect(url_for('index'))

@app.route('/del_s',methods=['GET', 'POST'])
def del_s():
    if not CheckLogin():
        return redirect(url_for('login'))
    id_str = request.args['id']
    id = id_str.split(',')
    for i in range(0, len(id)):
        DelDataById("stu_id", id[i], "student_info")
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.add_url_rule('/', 'default_route', lambda: redirect(url_for('login')))
    app.run(debug=True)
