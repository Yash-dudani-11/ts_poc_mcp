import os
import psycopg
from typing import Optional
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings
from schema import CreateProductResult, Product

mcp = MCPServer("Product CRUD MCP Server")

DATABASE_URL = os.environ["DATABASE_URL"]

@mcp.tool()
def create_product(
    name: str, 
    price: float, 
    product_description: Optional[str] = None
) -> CreateProductResult:
    """
    Create a new product in the product database.

    Use this tool when the user asks to add or create a product.
    """
    
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO products (name, description, price)
                VALUES (%s, %s, %s)
                RETURNING id, name, description, price
                """,
                (name, product_description, price),
            )

            row = cur.fetchone()

    product = Product(
        id=row[0],
        name=row[1],
        description=row[2],
        price=row[3],
    )

    return CreateProductResult(
        success=True,
        message="Product created successfully.",
        product=product,
    )


@mcp.tool()
def get_product(product_id: int) -> dict:
    """
    Retrieve one product by its unique product ID.

    Use this tool when the user asks for details about
    a specific product and provides its product ID.
    """
    
    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, price
                FROM products
                WHERE id = %s
                """,
                (product_id,),
            )

            row = cur.fetchone()

    if row is None:
        return {
            "success": False,
            "message": f"Product {product_id} was not found.",
        }

    return {
        "success": True,
        "product": {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
        },
    }


@mcp.tool()
def list_products() -> dict:
    """
    List all products stored in the product database.

    Use this tool when the user asks to view, show, retrieve,
    or list all available products.

    Returns:
        A result containing:
        - success: Whether the operation succeeded.
        - count: Number of products returned.
        - products: List of all products.
    """

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT id, name, description, price
                FROM products
                ORDER BY id
                """
            )

            rows = cur.fetchall()

    products = [
        {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
        }
        for row in rows
    ]

    return {
        "success": True,
        "count": len(products),
        "products": products,
    }


@mcp.tool()
def update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    product_description: Optional[str] = None,
) -> dict:
    """
    Update an existing product.

    Only fields supplied by the caller are updated.

    Args:
        product_id: Unique ID of the product.
        name: New product name.
        price: New product price.
        product_description: New product description.

    Returns:
        The updated product.
    """

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:

            cur.execute(
                """
                SELECT id, name, description, price
                FROM products
                WHERE id = %s
                """,
                (product_id,),
            )

            existing = cur.fetchone()

            if existing is None:
                return {
                    "success": False,
                    "message": f"Product {product_id} was not found.",
                }

            new_name = name if name is not None else existing[1]
            new_description = (
                product_description if product_description is not None else existing[2]
            )
            new_price = price if price is not None else existing[3]

            cur.execute(
                """
                UPDATE products
                SET name = %s,
                    description = %s,
                    price = %s
                WHERE id = %s
                RETURNING id, name, description, price
                """,
                (
                    new_name,
                    new_description,
                    new_price,
                    product_id,
                ),
            )

            row = cur.fetchone()

    return {
        "success": True,
        "message": "Product updated successfully.",
        "product": {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
        },
    }


@mcp.tool()
def delete_product(product_id: int) -> dict:
    """
    Delete a product.

    Args:
        product_id: Unique ID of the product.

    Returns:
        Confirmation that the product was deleted.
    """

    with psycopg.connect(DATABASE_URL) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                DELETE FROM products
                WHERE id = %s
                RETURNING id, name, description, price
                """,
                (product_id,),
            )

            row = cur.fetchone()

    if row is None:
        return {
            "success": False,
            "message": f"Product {product_id} was not found.",
        }

    return {
        "success": True,
        "message": "Product deleted successfully.",
        "deleted_product": {
            "id": row[0],
            "name": row[1],
            "description": row[2],
            "price": row[3],
        },
    }

# ---------------------------------------------------------------------------
# Start MCP server
# ---------------------------------------------------------------------------

app = mcp.streamable_http_app(
    transport_security=TransportSecuritySettings(
        allowed_hosts=[
            "ts-poc-mcp-zhrk.vercel.app",
            "localhost",
            "localhost:8000",
            "127.0.0.1",
            "127.0.0.1:8000",
        ],
        allowed_origins=[
            "https://ts-poc-mcp-zhrk.vercel.app",
            "http://localhost:8000",
            "http://127.0.0.1:8000",
        ],
    )
)
