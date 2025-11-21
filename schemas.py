"""
Database Schemas

Define your MongoDB collection schemas here using Pydantic models.
These schemas are used for data validation in your application.

Each Pydantic model represents a collection in your database.
Model name is converted to lowercase for the collection name:
- User -> "user" collection
- Product -> "product" collection
- BlogPost -> "blogs" collection
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal

# Example schemas (replace with your own):

class User(BaseModel):
    """
    Users collection schema
    Collection name: "user" (lowercase of class name)
    """
    name: str = Field(..., description="Full name")
    email: str = Field(..., description="Email address")
    address: str = Field(..., description="Address")
    age: Optional[int] = Field(None, ge=0, le=120, description="Age in years")
    is_active: bool = Field(True, description="Whether user is active")

class Product(BaseModel):
    """
    Products collection schema
    Collection name: "product" (lowercase of class name)
    """
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    price: float = Field(..., ge=0, description="Price in dollars")
    category: str = Field(..., description="Product category")
    in_stock: bool = Field(True, description="Whether product is in stock")

# Lead capture schema for NV Media website
class Lead(BaseModel):
    """
    Leads captured from the NV Media website contact form
    Collection name: "lead"
    """
    full_name: str = Field(..., min_length=2, description="Full name of the inquirer")
    email: EmailStr = Field(..., description="Contact email")
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Business/Company Name")
    service: Literal[
        "Social Media Management",
        "Performance Marketing (Google & Meta Ads)",
        "Branding & Design",
        "Website Development",
        "Video Production",
        "Creative Strategy",
        "Other",
    ] = Field(..., description="Selected service of interest")
    budget: Literal[
        "<$1,000",
        "$1,000 - $3,000",
        "$3,000 - $5,000",
        "$5,000 - $10,000",
        ">$10,000"
    ] = Field(..., description="Estimated budget range")
    message: Optional[str] = Field(None, description="Additional details")
    source: Optional[str] = Field("website", description="Lead source identifier")
