from mcp.client.stdio import stdio_client
from mcp import ClientSession
import asyncio

async def main():

    server = {
        "command": "python",
        "args": ["mcp_server.py"]
    }

    async with stdio_client(server) as (reader, writer):

        async with ClientSession(reader, writer) as session:

            await session.initialize()

            result = await session.call_tool(
                "get_song_recommendation",
                {}
            )

            print("\nSong Recommendation:\n")
            print(result)

asyncio.run(main())