from pydantic import BaseModel

class Product(BaseModel):
    id: int
    name: str
    description: str | None = None
    price: float

class CreateProductResult(BaseModel):
    success: bool
    message: str
    product: Product