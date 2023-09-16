import uvicorn
from argparse import ArgumentParser, Namespace
from croydon.command import Command


class Run(Command):

    NAME = "run"
    HELP = "run server"
    ASYNC_RUN = False

    host: str
    port: int
    watch: bool

    async def setup(self, args: Namespace) -> None:
        self.host = args.host
        self.port = args.port
        self.watch = args.watch

    def run_sync(self):
        uvicorn.run("app:app", host=self.host, port=self.port, reload=self.watch)

    def init_argument_parser(self, parser: ArgumentParser) -> None:
        parser.add_argument("-P", "--port", type=int, help="port to listen on", default=8000)
        parser.add_argument("-H", "--host", type=str, help="host to bind to", default="127.0.0.1")
        parser.add_argument("-w", "--watch", action="store_true", default=False, help="reload on source code changes")
