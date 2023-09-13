import click


from huhk.case_project.main_fun import get_version, set_key_name, install_project, update_project, fun_project, \
    running_testcase


@click.command()
@click.option('-v', '--version', help='版本, 当前--key/--name', is_eager=True, is_flag=True)
@click.option('-k', '--key', help='项目key, 传*表示所有项目，不传默认去上一次key')
@click.option('-n', '--name', help='项目名称, 传*表示所有项目，不传默认去上一次name')
@click.option('-i', '--install', help='根据key创建项目, 项目存在则更新')
@click.option('-u', '--update', help='根据--key更新项目，--key不存在时默认取之前的值', is_eager=True, is_flag=True)
@click.option('-f', '--fun', help='新增api方法，已存在时更新', is_eager=True, is_flag=True)
@click.option('-r', '--running', help='执行测试用例, 项目或目录', multiple=True)
@click.option('-cp', '--casepath', help='测试用例文件路径')
@click.option('-rp', '--reportpath', help='生成的测试报告文件路径')
def main(version, key, name, install, update, fun, running, casepath, reportpath):
    print(version, key, name, install, update, fun, running, casepath, reportpath)
    if version:
        click.echo(get_version())
    else:
        set_key_name(key, name)
        if install:
            click.echo(install_project(install, name))
        elif update:
            click.echo(update_project(key, name))
        elif fun:
            click.echo(fun_project(app_key=key, name=name))
        elif running:
            click.echo(running_testcase(running, casepath, reportpath))


if __name__ == '__main__':
    main()
