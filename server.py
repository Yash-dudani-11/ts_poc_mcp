from typing import Optional
from mcp.server import MCPServer
from schema import CreateProductResult, Product

mcp = MCPServer("Product CRUD MCP Server")

products = {}
next_id = 1

@mcp.tool()
def create_product(
    name: str, 
    price: float, 
    description: Optional[str] = None
) -> CreateProductResult:
    """
    Create a new product.

    Args:
        name: Name of the product.
        price: Price of the product.
        description: Optional description of the product.

    Returns:
        The newly created product.
    """
    
    global next_id
    
    product = Product(
        id=next_id,
        name=name,
        description=description,
        price=price
    )
    
    products[next_id] = product
    next_id += 1

    return CreateProductResult(
        success=True,
        message="Product created successfully.",
        product=product
    )


@mcp.tool()
def get_product(product_id: int) -> dict:
    """
    Get a product by its ID.
    
    Args:
        product_id: Unique ID of the product.

    Returns:
        The matching product if it exists.
    """
    
    product = products.get(product_id)
    
    if product is None:
        return {
            "success": False,
            "message": f"Product {product_id} was not found"
        }
    
    return {
        "success": True,
        "product": product
    }


@mcp.tool()
def list_products() -> dict:
    """
    Return all available products.

    Returns:
        All products currently stored by the MCP server.
    """

    return {
        "success": True,
        "count": len(products),
        "products": list(products.values()),
    }


@mcp.tool()
def update_product(
    product_id: int,
    name: Optional[str] = None,
    price: Optional[float] = None,
    description: Optional[str] = None,
) -> dict:
    """
    Update an existing product.

    Only fields supplied by the caller are updated.

    Args:
        product_id: Unique ID of the product.
        name: New product name.
        price: New product price.
        description: New product description.

    Returns:
        The updated product.
    """

    product = products.get(product_id)

    if product is None:
        return {
            "success": False,
            "message": f"Product {product_id} was not found.",
        }

    if name is not None:
        product.name = name

    if price is not None:
        product.price = price

    if description is not None:
        product.description = description

    return {
        "success": True,
        "message": "Product updated successfully.",
        "product": product,
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

    product = products.pop(product_id, None)

    if product is None:
        return {
            "success": False,
            "message": f"Product {product_id} was not found.",
        }

    return {
        "success": True,
        "message": "Product deleted successfully.",
        "deleted_product": product,
    }

# ---------------------------------------------------------------------------
# Start MCP server
# ---------------------------------------------------------------------------

# if __name__ == "__main__":
#     mcp.run(
#         "streamable-http",
#         host="0.0.0.0",
#         port=8000,
#     )

app = mcp.streamable_http_app()
