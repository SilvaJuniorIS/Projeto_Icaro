from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BasketRequest(BaseModel):
    title: str
    central_object: str
    category: str = ""
    contracting_context: str = ""
    status: str = "draft"


class BasketItemRequest(BaseModel):
    basket_id: int
    lot_group: str = ""
    description: str
    unit: str
    quantity: float = Field(gt=0)
    catmat_catser: str = ""
    keywords: list[str] = Field(default_factory=list)
    classifications: list[str] = Field(default_factory=list)
    technical_notes: str = ""
    status: str = "pending"


class ItemSourceRequest(BaseModel):
    basket_item_id: int
    source_type: str
    origin: str
    url: str
    source_date: str = ""
    access_date: str = ""
    organization: str
    modality: str = ""
    process_number: str = ""
    supplier: str = ""
    contracting_context: str
    unit_price: float = Field(gt=0)
    total_price: float | None = None
    quantity: float = Field(gt=0)
    unit: str = ""
    accepted: bool = True
    discard_reason: str = ""
    notes: str = ""
    raw_payload: dict[str, Any] = Field(default_factory=dict)


class SearchLogRequest(BaseModel):
    basket_id: int
    basket_item_id: int | None = None
    source_type: str
    query: str
    normalized_query: str = ""
    status: str = "started"
    results_count: int = 0
    error: str = ""


class AutomatedSearchRequest(BaseModel):
    query: str = ""
    source_types: list[str] = Field(default_factory=lambda: ["pncp"])
    start_date: str = ""
    end_date: str = ""
    page_size: int = Field(default=20, ge=1, le=50)
    save_results: bool = True
