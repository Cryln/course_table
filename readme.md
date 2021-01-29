## 东北大学课表日程生成
> 我自己每次上课看课表，都是要点开智慧东大，繁琐至极。上个学期看到小米的小爱课程表支持了东北大学，我用一加也可以安装小爱课程表，但始终没法设置成功。于是就有了做这个项目的想法。


### **Features**
-------------
### 该分支，为了尽可能方便，使用了Github Actions，自动爬取教务处的数据，生成iCalendar *.ics文件，并通过邮件发送到指定对象。

--------
### **使用该项目**
> 只需要设置相关的secrets即可
1. 东北大学统一身份认证，学号：USERNAME，密码：PASSWORD

2. 邮件发送方，邮箱地址：MAIL_USERNAME；密码：MAIL_PASSWORD。

3. 还需要更改 ./.github/workflows/main.yml 中的jobs->emailbot->steps->'Send mail'->with->server_address 设置为对应的邮箱服务器地址

4. 邮件接收方，邮箱地址：EMAIL_ADDR

   如下，为./.github/workflows/main.yml 的内容
5. Actions 的执行需要触发条件，在 on: 语句下设置，这里设置的是，当main分支发生push或者pull_request。 还有其他触发条件，For more information, see "[Events that trigger workflows](https://docs.github.com/articles/events-that-trigger-workflows)."

``` yml
# This is a basic workflow to help you get started with Actions

name: NEU CourseTable Email Bot

# Controls when the action will run. 
on:
  # Triggers the workflow on push or pull request events but only for the main branch
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

  # Allows you to run this workflow manually from the Actions tab
  workflow_dispatch:

# A workflow run is made up of one or more jobs that can run sequentially or in parallel
jobs:
  emailbot:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2
      - name: 'Set up Python'
        uses: actions/setup-python@v1
        with:
          python-version: 3.7
      - name: 'Install lib'
        run: pip install lxml && pip install ics
      - name: 'Working'
        run: python main.py ${{ secrets.USERNAME }} ${{ secrets.PASSWORD }}

      - name: 'Send mail'
        uses: dawidd6/action-send-mail@master
        with:
          server_address: smtp.gmail.com 
          server_port: 465
          username: ${{ secrets.MAIL_USERNAME }}
          password: ${{ secrets.MAIL_PASSWORD }}
          subject: test
          body: file://mail.md
          to: ${{ secrets.EMAIL_ADDR }}
          from: GitHub Actions
          content_type: text/plain
          attachments: ./my.ics

```
其他须知：
    发送方邮箱，最初用的163网易邮箱，但是被判定为垃圾邮件，频繁失败。然后换成GMAIL，但因为谷歌有保护机制，会拦截登录，参考了[这篇帖子](https://segmentfault.com/q/1010000008458788/a-1020000008470509)。

1、将【安全性较低的应用程式取权限】设置为启用
进入网页[https://www.google.com/settin...](https://www.google.com/settings/security/lesssecureapps)，设置为【启用】。

2、解除人机验证锁定
进入网页[https://accounts.google.com/b...](https://accounts.google.com/b/0/DisplayUnlockCaptcha)，点击【继续】。

​	不同的邮箱服务都会有Anti-Spamming，都需要设置一下，接收方还可以添加邮箱地址白名单，来防止误判。最后来个效果图。

当然，你可能不需要邮箱服务，你也可以clone到本地使用

```shell

python main.py [学号] [密码]
#例如：
python main.py 20180001 password123

```
然后会生成并覆盖my.ics,将其导入日历即可。

![](https://user-images.githubusercontent.com/49862786/106231771-6ad00480-622d-11eb-99a3-80517b5c07f4.jpg)

TODOS: 目前暂不能选择学期，看了教务处网站里的semester.id设置，找不到规律，目前默认为2021春季。