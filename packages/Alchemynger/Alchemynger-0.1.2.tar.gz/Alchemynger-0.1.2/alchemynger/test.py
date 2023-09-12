from asyncio import run
from sqlalchemy import Column, String, Integer
from sqlalchemy import select, delete, update, insert

from manager import SyncManager


manager = SyncManager('sqlite:///temp.db')

class User(manager.Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))

    def __repr__(self) -> str:
        return f"User(id={self.id}, name={self.name})"
    

class Auto(manager.Base):
    __tablename__ = 'auto'
    id = Column(Integer, primary_key=True, autoincrement=True)
    model = Column(String(20))

    def __repr__(self) -> str:
        return f"Auto(id={self.id}, model={self.model})"
    

async def main():
    manager.connect()
    
    stmt = manager[User].select

    print(stmt)

    print(manager.execute(stmt))


if __name__ == '__main__':
    run(main())