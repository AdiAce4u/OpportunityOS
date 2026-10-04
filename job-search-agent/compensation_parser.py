import re
from typing import Dict, Any, Tuple, Optional

class CompensationParser:
    @staticmethod
    def parse_compensation(job_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extracts and normalizes salary / stipend from job dict and description.
        Returns:
          - normalized_yearly_salary: float (used for descending sorting)
          - display_salary: str (formatted for UI)
          - currency: str
        """
        import math
        min_amt = job_dict.get("min_amount")
        max_amt = job_dict.get("max_amount")
        
        # Check if float NaN
        if isinstance(min_amt, float) and math.isnan(min_amt):
            min_amt = None
        if isinstance(max_amt, float) and math.isnan(max_amt):
            max_amt = None

        interval_raw = job_dict.get("interval")
        interval = str(interval_raw).lower() if (interval_raw and not (isinstance(interval_raw, float) and math.isnan(interval_raw))) else ""

        currency_raw = job_dict.get("currency")
        currency = str(currency_raw).upper() if (currency_raw and not (isinstance(currency_raw, float) and math.isnan(currency_raw))) else ""

        desc_raw = job_dict.get("description")
        desc = str(desc_raw) if (desc_raw and not (isinstance(desc_raw, float) and math.isnan(desc_raw))) else ""

        # 1. If structured amount is already present from scraper
        if min_amt or max_amt:
            avg_amt = ((min_amt or max_amt) + (max_amt or min_amt)) / 2.0
            annual_val = CompensationParser._to_annual(avg_amt, interval, currency)
            display_str = CompensationParser._format_display(min_amt, max_amt, interval, currency)
            return {
                "normalized_yearly_salary": annual_val,
                "display_salary": display_str,
                "currency": currency or "INR"
            }

        # 2. Fallback: Parse from job description text (LPA, /month, /year, $, ₹)
        text_parsed = CompensationParser._parse_from_text(desc)
        if text_parsed:
            return text_parsed

        return {
            "normalized_yearly_salary": 0.0,
            "display_salary": "Not Disclosed",
            "currency": ""
        }

    @staticmethod
    def _to_annual(amount: float, interval: str, currency: str) -> float:
        rate_to_inr = 85.0 if currency in ["USD", "$"] else (92.0 if currency in ["EUR", "€"] else 1.0)
        
        annual = amount
        if "hour" in interval:
            annual = amount * 2080  # 40 hrs/wk * 52 wks
        elif "month" in interval:
            annual = amount * 12
        elif "week" in interval:
            annual = amount * 52

        # Convert to unified INR scale for consistent sorting
        return annual * rate_to_inr

    @staticmethod
    def _format_display(min_amt: Optional[float], max_amt: Optional[float], interval: str, currency: str) -> str:
        curr_sym = "₹" if currency in ["INR", ""] else ("$" if currency == "USD" else currency)
        inter_label = f"/{interval[:2]}" if interval else ""
        
        if min_amt and max_amt and min_amt != max_amt:
            if min_amt >= 100000 and "INR" in currency:
                return f"{curr_sym}{min_amt/100000:.1f} - {max_amt/100000:.1f} LPA"
            return f"{curr_sym}{min_amt:,.0f} - {curr_sym}{max_amt:,.0f}{inter_label}"
        elif max_amt or min_amt:
            val = max_amt or min_amt
            if val >= 100000 and "INR" in currency:
                return f"{curr_sym}{val/100000:.1f} LPA"
            return f"{curr_sym}{val:,.0f}{inter_label}"
        return "Not Disclosed"

    @staticmethod
    def _parse_from_text(text: str) -> Optional[Dict[str, Any]]:
        # Check for LPA (Lakhs Per Annum) e.g., "12-18 LPA", "15 LPA"
        lpa_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:-|to)\s*(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lac)', text, re.IGNORECASE)
        if lpa_match:
            low, high = float(lpa_match.group(1)), float(lpa_match.group(2))
            avg_lpa = (low + high) / 2.0
            return {
                "normalized_yearly_salary": avg_lpa * 100000,
                "display_salary": f"₹{low:.1f} - {high:.1f} LPA",
                "currency": "INR"
            }
        
        single_lpa = re.search(r'(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lac)', text, re.IGNORECASE)
        if single_lpa:
            val = float(single_lpa.group(1))
            return {
                "normalized_yearly_salary": val * 100000,
                "display_salary": f"₹{val:.1f} LPA",
                "currency": "INR"
            }

        # Check for monthly stipend e.g., "₹30,000 / month", "30k/month", "$5,000/mo"
        monthly_match = re.search(r'(?:₹|rs\.?|\$)\s*(\d{1,3}(?:,\d{3})+|\d+k?)\s*(?:-|to)?\s*(?:₹|rs\.?|\$)?\s*(\d{1,3}(?:,\d{3})+|\d+k?)?\s*(?:/|\s+per\s+)?\s*(?:month|mo|pm)', text, re.IGNORECASE)
        if monthly_match:
            raw_val = monthly_match.group(1).replace(',', '').lower()
            val = float(raw_val.replace('k', '')) * (1000 if 'k' in raw_val else 1)
            is_usd = '$' in monthly_match.group(0)
            annual = val * 12 * (85.0 if is_usd else 1.0)
            sym = "$" if is_usd else "₹"
            return {
                "normalized_yearly_salary": annual,
                "display_salary": f"{sym}{val:,.0f}/month",
                "currency": "USD" if is_usd else "INR"
            }

        return None
