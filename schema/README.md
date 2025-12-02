
# Golden Invoice Schema – README

## Purpose
Defines the **Golden Invoice JSON v0.1** contract for Billing Recon MVP.  
All parsers must output this schema for consistency.

---

## Mandatory Fields

| Field | Type | Notes |
|-------|------|-------|
| `invoice_id` | string | **Required**, minLength=1 |
| `side` | string | Enum: `buy` or `sell` (MVP = `buy`) |
| `source.type` | string | Enum: `edi210`, `pdf`, `image`, `csv`, `api` |
| `dates.invoice` | string | ISO `YYYY-MM-DD` |
| `currency` | string | ISO 4217 (e.g., `USD`) |
| `charges.base_freight` | number | **Required** |
| `total` | number | **Required** |
| `metadata.golden_schema_version` | string | Must equal `"0.1"` |
| `metadata.parser_version` | string | **Required** |

---

## Fallback Mechanism for Profiles

Profiles allow runtime adaptation to partner-specific EDI quirks.

**Resolution Order:**
1. `profiles/{PARTNER}/{EDI_VERSION}/profile.json`
2. `profiles/{PARTNER}/default/profile.json`
3. `profiles/global/default/profile.json`

If none found → emit `profile_fallback_default` warning and proceed with global defaults.

---

## Complete Example – sample_l1.json
```json
{
  "invoice_id": "INV1001",
  "side": "buy",
  "source": { "type": "edi210", "doc_uri": null },
  "carrier": { "name": null, "scac": null },
  "customer": { "name": null, "account_id": null },
  "refs": { "bol": "BOL778231", "pro": "PR0123456", "po": null, "load_id": "LD-56712" },
  "parties": { "ship_from": "XYZ CORP", "ship_to": "ABC DISTRIBUTION", "bill_to": "OURBROKER AP" },
  "dates": { "invoice": "2025-11-01", "pickup": "2025-10-30", "delivery": "2025-11-02" },
  "currency": "USD",
  "charges": {
    "base_freight": 2201.35,
    "fuel_surcharge": 192.45,
    "detention": 150.0,
    "other": []
  },
  "total": 2543.8,
  "metadata": {
    "golden_schema_version": "0.1",
    "parser_version": "1.0.0",
    "edi_version": "004010",
    "trading_partner": "CARRIERX",
    "confidence": 0.95
  },
  "evidence": { "doc_uri": null, "attachments": [] }
}
