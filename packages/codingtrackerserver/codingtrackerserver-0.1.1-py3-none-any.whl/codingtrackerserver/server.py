from aiohttp import web
import json

from codingtrackerserver.config import Config
from codingtrackerserver.persistence import Persistence


class App:
    def __init__(self, db: str = "./data/database.db"):
        self.app: web.Application = web.Application()
        self.persistence: Persistence = Persistence(db=db)
        self._init_config()
        self._init_routes()

    def run(self) -> None:
        web.run_app(self.app)

    def _init_routes(self) -> None:
        self.app.add_routes([web.post("/update", self._update)])
        self.app.add_routes([web.get("/languages", self._languages)])

    def _init_config(self) -> None:
        cfg = Config()
        self.app["config"] = cfg.config()

    async def _update(self, request) -> None:
        bcontent: bytes = await request.read()
        if bcontent:
            content: list[tuple[str, float, float, bool]] = json.loads(bcontent)
        else:
            return
        try:
            self.persistence.update(content)
        except Exception as e:
            print("Exception while saving on DB: ", e)
            return web.Response(status=404)
        return web.Response(status=200)

    async def _languages(self, request) -> None:
        tallies: dict[str, float] = self.persistence.get_tallies()
        return web.json_response(tallies)


def main() -> None:
    app = App()
    app.run()

if __name__ == "__main__":
    main()
