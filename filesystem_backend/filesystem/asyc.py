import asyncio

async def worker():
    print("Worker started")
    # await asyncio.sleep(1)
    print("Worker finished")

async def main():
    task = asyncio.create_task(worker())
    print("working")

asyncio.run(main())