import json
from typing import Final

import pyperclip
from beni import bcolor, bfunc, btask
from rich.console import Console
from rich.syntax import Syntax

app: Final = btask.app


@app.command('json')
@bfunc.syncCall
async def format_json():
    '格式化 JSON （使用复制文本）'
    content = pyperclip.paste()
    try:
        data = json.loads(content)
        content = json.dumps(data, indent=4, ensure_ascii=False, sort_keys=True)
        syntax = Syntax(content, "json", line_numbers=True)
        console = Console()
        console.print(syntax)
        pyperclip.copy(content)
    except:
        bcolor.printRed('无效的 JSON')
        bcolor.printRed(content)
