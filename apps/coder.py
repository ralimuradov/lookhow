from textual.app import App, ComposeResult
from textual.containers import Container
from textual.widgets import TextArea, Header, Footer 
from textual.widget import Widget
from textual.containers import Horizontal
from textual.reactive import reactive
import io
import os
import datetime
from contextlib import redirect_stdout
from contextlib import suppress
import asyncio
import websockets

#------------------------------------------------------------------------

CODE_OUTPUT_PREFIX = '>>> '
IP = '127.0.0.1'
PORT = '8001'
IP_PORT = 'ws://' + IP + ':' + PORT
STARTUP_CODE = '#!/usr/bin/python'

#------------------------------------------------------------------------

class RunArea(Widget):
    def compose(self) -> ComposeResult:
        with Horizontal():
            run_area = TextArea(text=CODE_OUTPUT_PREFIX, read_only=True, id='output-area')
            yield run_area

#------------------------------------------------------------------------

# Main app window.
class Main(App):
    show_bottombar = reactive(False)
    CSS_PATH = 'style.tcss'
    BINDINGS = [
        ('f2', 'save_code', 'Save'),
        ('f4', 'show_output', 'Show output'),
        ('f5', 'run_code', 'Run code'),
        ('f10', 'quit', 'Quit')
    ]

    # Main window layout.
    def compose(self) -> ComposeResult:
        with Container():
            yield Header()
            text_area = TextArea.code_editor(text=STARTUP_CODE,
                                            language='python',
                                            theme='vscode_dark',
                                            soft_wrap=False,
                                            tab_behavior='indent',
                                            read_only=False,
                                            show_line_numbers=True,
                                            line_number_start=1,
                                            max_checkpoints=50,
                                            name=None,
                                            id='code-area',
                                            classes=None,
                                            disabled=False,
                                            tooltip=None)
            
            yield text_area
        yield RunArea()
        yield Footer()
  
#------------------------------------------------------------------------

    async def on_mount(self) -> None:
        self.title = 'Look How'
        self.sub_title = 'Coder mode'
        self.set_interval(0.2, self.update_text_area)

 #------------------------------------------------------------------------   

    def msg_for_send(self) -> str:
        return self.query_one('#code-area').text


    async def send_messages(self, websocket) -> None:
        with suppress(KeyboardInterrupt):
            send_message = await asyncio.get_event_loop().run_in_executor(None, self.msg_for_send)
            await websocket.send(send_message)
            

    async def update_text_area(self) -> None:
        async with websockets.connect(IP_PORT) as websocket:
            send_task = asyncio.create_task(self.send_messages(websocket))
            await asyncio.gather(send_task)
            _, pending = await asyncio.wait([send_task], return_when=asyncio.FIRST_COMPLETED)
            
            for task in pending:
                task.cancel()

#------------------------------------------------------------------------

    def action_save_code(self) -> None:
        os.makedirs('saves', exist_ok=True)
	
        code_for_save = self.query_one('#code-area').text
        
        dt_now = str(datetime.datetime.now())
        dt_stamp = dt_now.replace('-', '').replace(' ', '').replace(':', '')[0:-7]
        filename = 'saves/' + dt_stamp + '.py'
        
        with open(filename, 'w') as f_save:
            try:
                f_save.write(str(code_for_save))
            except Exception:
                self.notify('File save error!', severity='error', timeout=4)


    def action_show_output(self) -> None:
        self.show_bottombar = not self.show_bottombar

    def watch_show_bottombar(self, show_bottombar: bool) -> None:
        '''Set or unset visible class when reactive changes.'''
        self.query_one(RunArea).set_class(show_bottombar, '-visible')


    def action_run_code(self) -> None:
        code_for_run = self.query_one('#code-area').text
        os.makedirs('temp', exist_ok=True)

        with open('temp/runcode.py', 'w') as f_run:
            try:
                f_run.write(str(code_for_run))
            except Exception:
                self.notify('File save error!', severity='error', timeout=4)

        with open('temp/runcode.py', 'r') as f_run:
            try:
                code_for_run = f_run.read()
            except Exception:
                self.notify('File read error!', severity='error', timeout=4)

        stdout = io.StringIO()

        with redirect_stdout(stdout):
            try:
                exec(code_for_run)
                out_from_code = CODE_OUTPUT_PREFIX + stdout.getvalue()
                self.query_one('#output-area').text = out_from_code
            except Exception:
                self.notify('Code execution error!', severity='error', timeout=4)


    def action_quit(self) -> None:
        self.app.exit()

#------------------------------------------------------------------------

if __name__ == '__main__':
    app = Main()
    app.run()