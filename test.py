import asyncio
from wows.dataBase import table_check
from wows.dataBase import update

async def main():
    await update()
    
    pass

if __name__ == '__main__':
    asyncio.run(main())
    pass

