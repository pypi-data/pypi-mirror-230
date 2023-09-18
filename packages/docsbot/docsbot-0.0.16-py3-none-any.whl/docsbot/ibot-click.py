import click
import os

CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

@click.group(context_settings=CONTEXT_SETTINGS)
def cli():
    """聊天机器人CLI工具"""
    pass

@cli.command()
@click.option('--import-log', type=click.File('r'), help='导入以前的聊天记录文件.')
def chat(import_log):
    """与机器人交互式对话"""
    history = []
    if import_log:
        history.extend(import_log.readlines())
        click.echo("成功导入聊天记录！")

    while True:
        user_input = click.prompt('您', prompt_suffix=': ')
        if user_input.lower() in ["exit", "退出"]:
            with open("chat.log", "w") as f:
                for line in history:
                    f.write(line)
            click.echo("聊天记录已保存到 chat.log 文件中。再见！")
            break
        else:
            history.append("您：" + user_input + "\n")
            click.echo(f"机器人：{user_input}")
            history.append(f"机器人：{user_input}\n")

if __name__ == '__main__':
    cli()
