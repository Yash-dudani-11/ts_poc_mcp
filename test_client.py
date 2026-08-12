
import asyncio
from mcp import Client
from mcp import types


MCP_SERVER_URL = "http://localhost:8000/mcp"


def print_result(result):
    print(f"is_error: {result.is_error}")
    print(f"structured_content: {result.structured_content}")

    print("content:")

    for item in result.content:
        if isinstance(item, types.TextContent):
            print(item.text)
        else:
            print(item)


async def main():
    async with Client(MCP_SERVER_URL) as client:

        print("\n--- Available tools ---")

        tools = await client.list_tools()

        for tool in tools.tools:
            print(tool.name)

        print("\n--- Creating product ---")

        result = await client.call_tool(
            "create_product",
            {
                "name": "Test Laptop",
                "price": 999.0,
                "description": "Created from MCP client",
            },
        )

        print_result(result)

        print("\n--- Listing products ---")

        result = await client.call_tool(
            "list_products",
            {},
        )

        print_result(result)


if __name__ == "__main__":
    asyncio.run(main())