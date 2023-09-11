from codingtrackerserver.session import Session
from codingtrackerserver.sqlhandler import SqlHandler
from codingtrackerserver.process import EditorProcess


class Persistence:
    def __init__( self,
            db: str = None,
            encoding: str = "utf-8",
    ) -> None:
        self.sql: SqlHandler = SqlHandler(db)
        self.encoding = encoding

    def update(self, data: list[tuple[str, float, float, bool]]):
        content: list[Session] = self._sql_format(data)
        self.sql.update(content)

    def _sql_format(self, data: list[tuple[str, float, float, bool]]) -> list[Session]:
        return [Session(language=r[0], start_time=r[1], end_time=r[2], running=r[3])
                for r in data]

    def terminate(self):
        self.sql.terminate()

    def get_tallies(self):
        tallies: dict[str, float] = {}
        data: list[tuple[str, float, float]] = self.sql.get_data()
        print(data)
        for datum in data:
            if datum[0] in tallies.keys():
                tallies[datum[0]] += self._calculate_time(datum[1], datum[2])
            else:
                tallies[datum[0]] = self._calculate_time(datum[1], datum[2])
        return tallies

    def _calculate_time(self, start: float = 0, end: float = 0) -> float:
        return end - start
