"""
DCF Calculator API Endpoints

Simple, validated Discounted Cash Flow (DCF) calculation endpoint intended for MVP usage.
"""

from __future__ import annotations

from typing import List, Optional, Dict, Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

router = APIRouter(prefix="/api", tags=["DCF"])


class DCFInput(BaseModel):
    current_fcf: float = Field(..., description="Current free cash flow (base year).")
    growth_rate: float = Field(..., description="Annual growth rate during explicit forecast (decimal, e.g. 0.15).")
    forecast_years: int = Field(5, ge=1, le=50, description="Number of explicit forecast years.")
    terminal_growth: float = Field(0.03, description="Perpetuity growth rate (decimal, e.g. 0.03).")
    discount_rate: float = Field(..., gt=0, description="Discount rate / WACC (decimal, e.g. 0.10).")
    net_debt: float = Field(0.0, description="Net debt to subtract from enterprise value.")
    shares_outstanding: float = Field(1.0, gt=0, description="Shares outstanding for per-share value.")
    manual_fcfs: Optional[List[float]] = Field(
        default=None,
        description="Optional explicit FCFs override (length must equal forecast_years).",
    )


@router.post("/dcf")
def calculate_dcf(data: DCFInput) -> Dict[str, Any]:
    """
    Calculate a simple DCF using:
    - Explicit forecast FCFs (either generated via growth_rate or manually provided)
    - Gordon Growth (perpetuity) terminal value
    """

    # Basic economic sanity checks
    if data.discount_rate <= data.terminal_growth:
        raise HTTPException(
            status_code=400,
            detail="discount_rate must be greater than terminal_growth for Gordon Growth terminal value.",
        )
    if data.terminal_growth <= -1:
        raise HTTPException(status_code=400, detail="terminal_growth must be greater than -1.0")
    if data.growth_rate <= -1:
        raise HTTPException(status_code=400, detail="growth_rate must be greater than -1.0")

    # Generate/accept explicit FCF projections
    if data.manual_fcfs is not None:
        if len(data.manual_fcfs) != data.forecast_years:
            raise HTTPException(
                status_code=400,
                detail="manual_fcfs length must equal forecast_years when provided.",
            )
        fcfs = [float(x) for x in data.manual_fcfs]
    else:
        fcfs = [
            float(data.current_fcf) * (1.0 + float(data.growth_rate)) ** year
            for year in range(1, data.forecast_years + 1)
        ]

    # Discount explicit FCFs
    discounted_fcfs: List[float] = []
    discount_factors: List[float] = []
    for i, fcf in enumerate(fcfs, start=1):
        df = (1.0 + float(data.discount_rate)) ** i
        discount_factors.append(df)
        discounted_fcfs.append(float(fcf) / df)

    pv_explicit = float(sum(discounted_fcfs))

    # Terminal value (Gordon Growth, at end of forecast_years)
    final_fcf = float(fcfs[-1])
    terminal_value = final_fcf * (1.0 + float(data.terminal_growth)) / (float(data.discount_rate) - float(data.terminal_growth))
    discounted_terminal_value = terminal_value / ((1.0 + float(data.discount_rate)) ** int(data.forecast_years))

    enterprise_value = pv_explicit + float(discounted_terminal_value)
    equity_value = enterprise_value - float(data.net_debt)
    per_share_value = equity_value / float(data.shares_outstanding)

    rows = [
        {
            "year": i + 1,
            "fcf": float(f),
            "discount_factor": float(discount_factors[i]),
            "present_value": float(discounted_fcfs[i]),
        }
        for i, f in enumerate(fcfs)
    ]

    return {
        "inputs": data.model_dump(),
        "rows": rows,
        "pv_explicit": pv_explicit,
        "terminal_value": float(terminal_value),
        "discounted_terminal_value": float(discounted_terminal_value),
        "enterprise_value": float(enterprise_value),
        "equity_value": float(equity_value),
        "per_share_value": float(per_share_value),
    }

