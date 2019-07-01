#导入库
from flask import  Flask,render_template,redirect,request,session,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Column, String
import requests
from lxml import html
from flask_bootstrap import Bootstrap


#配置
s = requests.session()
s.keep_alive = False
app=Flask(__name__)
Bootstrap(app)
app.secret_key='123'

#配置数据库
app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://root:19970719@127.0.0.1/keyan'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db=SQLAlchemy(app)
class User(db.Model):
    __tablename__='users'
    id = Column(String(20), primary_key=True)#注意这里py2和py3的区别，py2再用Column的时候需要用db.Column而py3则不需要
    password=Column(String(20), unique=True)

#登录页面
@app.route('/',methods=['POST','GET'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        userid = request.form.get('userid')
        password = request.form.get('password')
        usr = User.query.filter(User.id == userid, User.password == password).first()
        if usr:
            session['userid'] = userid
            session.permanet = True
            return render_template('tongzhi.html')
        elif not all([userid, password]):
            return render_template('index.html', error='用户名或密码不能为空')
        else:
            return render_template('index.html', error='用户名或密码错误')

#母页面
# @app.route('/main',methods=['POST','GET'])
# def main():
#     return render_template('main.html')

#主页面
@app.route('/tongzhi',methods=['POST','GET'])
def tongzhi():
    return render_template('tongzhi.html')

#成果
@app.route('/chengguo',methods=['POST','GET'])
def chengguo():
    return render_template('chengguo.html')

#论文管理
@app.route('/guanli',methods=['POST','GET'])
def guanli():
    return render_template('guanli.html')

#上传论文
@app.route('/shangchuan',methods=['POST','GET'])
def shangchuan():
    return render_template('shangchuan.html')

#爬取论文
@app.route('/pachong',methods=['POST','GET'])
def pachong():
    if request.method == 'GET':
        return render_template('pachong.html')
    else:
        guanjianzi=request.form.get('guanjianzi')
        KeyWords = guanjianzi  # 搜索关键词
        MaxPage = 1  # 爬取的页面数目，即确定爬取第几页
        #URL = 'https://www.cn-ki.net/'
        URL = 'https://www.cn-ki.net//'
        # Num_Paper = 0
        data = {'keyword': KeyWords}

        def get_html(url, para_data):  # 获取网页源码
            content = requests.get(url, params=para_data)
            return content

        content = get_html(URL + 'search', data)
        page_url = content.url
        page_ii = 0

        while page_ii < MaxPage:
            content = get_html(page_url, '')
            tree = html.fromstring(content.text)
            e1 = tree.xpath('//div[@class="mdui-col-xs-12 mdui-col-md-9 mdui-typo"]')
            for ei in e1:
                title = '标题:' + ''.join(ei.xpath('h3/a/text()'))
                author = '   作者:' + ''.join(ei.xpath('div[1]/span[1]/text()'))
                href = ''.join(ei.xpath('h3/a/@href'))
                if URL not in href:  # 优化下载地址内容爬取
                        href = URL + href
                href = '   链接: ' + href
                JnName = '   期刊:' + ''.join(ei.xpath('div[1]/span[3]/text()'))

                # Num_Paper += 1 #将这行注释不改变，甚至可以不要
                page_ii += 1  # 将这行注释会一直爬取
                # if page_ii == 16:  # 控制爬取次数
                #     break
                # 写入txt文件操作，把w模式(覆盖)换成a模式(不覆盖)就ok了
                f = open(KeyWords + '.txt', 'a')
                f.write("{}\n{}\n{}\n{}\n\n".format(title, author, href, JnName))
                f.close()

    #读取txt文件操作，并将其展示到前端
    f = open(KeyWords + '.txt', 'r')
    layout = f.readlines()
    for line in layout:
        # print(line)
        return render_template('pachongshow.html', line=line,layout=layout)

#爬取结果展示
@app.route('/pachongshow',methods=['POST','GET'])
def pachongshow():
    return render_template('pachongshow.html')

if __name__ =='__main__':
    app.run(debug=True)
