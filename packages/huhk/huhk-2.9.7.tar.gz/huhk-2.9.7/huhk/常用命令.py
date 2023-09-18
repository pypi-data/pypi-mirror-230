"""
@REM 创建一个新项目和一个单个应用
python manage.py  startproject ardar_test
python manage.py startapp autotest

@REM 如果关闭debug模式后，请执行以下命令将simpleui静态文件静态文件克隆到根目录
python manage.py collectstatic

@REM 执行迁移
python manage.py makemigrations
python manage.py migrate

@REM 创建admin超级管理员
python manage.py createsuperuser

@REM 三方包记录
pip freeze > requirements.txt

@REM linux 虚拟环境
mkvirtualenv -p python3.10 py310
workon py310
deactivate
rmvirtualenv venv

@REM 打包上传
python setup_set.py sdist

@REM 打包命令
python setup_set.py sdist bdist_wheel
python -m twine upload dist/*

@REM linux 命令
yum  install  -y  java-1.8.0-openjdk.x86_64

"""