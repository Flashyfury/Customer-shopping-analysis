# Customer Shopping Analytics – Power BI Dashboard Guide

## Overview
This document describes how to recreate the Customer Shopping Analytics dashboard
in Power BI Desktop using the dataset in `data/customer_shopping_behavior.csv`.

---

## 1. Load Data into Power BI

1. Open **Power BI Desktop**
2. Click **Home → Get Data → Text/CSV**
3. Select `data/customer_shopping_behavior.csv`
4. Click **Load**

---

## 2. Power Query Transformations

Open **Transform Data** and apply these steps:

| Step | Action |
|------|--------|
| Rename Column | `Purchase Amount (USD)` → `Revenue` |
| Add Column | `Age Group` (Conditional Column) |
| Change Type | `Review Rating` → Decimal Number |
| Change Type | `Previous Purchases` → Whole Number |

### Age Group Conditional Column Logic
```
<= 18  → "<18"
<= 25  → "18-25"
<= 35  → "26-35"
<= 45  → "36-45"
<= 60  → "46-60"
else   → "60+"
```

---

## 3. DAX Measures

Create these measures in a dedicated `_Measures` table:

```dax
Total Revenue = SUM('customer_shopping_behavior'[Revenue])

Total Customers = DISTINCTCOUNT('customer_shopping_behavior'[Customer ID])

Average Purchase = AVERAGE('customer_shopping_behavior'[Revenue])

Average Rating = AVERAGE('customer_shopping_behavior'[Review Rating])

Revenue by Category = 
CALCULATE(
    SUM('customer_shopping_behavior'[Revenue]),
    ALLEXCEPT('customer_shopping_behavior', 'customer_shopping_behavior'[Category])
)

Subscription Rate = 
DIVIDE(
    CALCULATE(COUNTROWS('customer_shopping_behavior'),
              'customer_shopping_behavior'[Subscription Status] = "Yes"),
    COUNTROWS('customer_shopping_behavior'),
    0
)

Discount Rate = 
DIVIDE(
    CALCULATE(COUNTROWS('customer_shopping_behavior'),
              'customer_shopping_behavior'[Discount Applied] = "Yes"),
    COUNTROWS('customer_shopping_behavior'),
    0
)

Top 10 Products Revenue = 
CALCULATE(
    SUM('customer_shopping_behavior'[Revenue]),
    TOPN(10, VALUES('customer_shopping_behavior'[Item Purchased]),
         [Total Revenue], DESC)
)
```

---

## 4. Dashboard Layout

### Page 1 — Executive Summary

#### KPI Cards (Top Row)
| Card | Measure | Icon |
|------|---------|------|
| Total Revenue | `[Total Revenue]` | 💰 |
| Total Customers | `[Total Customers]` | 👥 |
| Average Purchase | `[Average Purchase]` | 🛒 |
| Average Rating | `[Average Rating]` | ⭐ |

**Format settings for KPI cards:**
- Background: Dark (#161B22)
- Accent border: top border colored by theme
- Font size: 28pt for value, 11pt for label

#### Charts (Middle Row)
| Visual | Type | X-Axis | Y-Axis / Value |
|--------|------|--------|----------------|
| Revenue by Category | Clustered Bar | Category | Total Revenue |
| Revenue by Gender | Donut Chart | Legend: Gender | Values: Total Revenue |
| Revenue by State | Map / Bar Chart | Location | Total Revenue |
| Revenue by Age Group | Clustered Bar | Age Group | Total Revenue |

#### Charts (Bottom Row)
| Visual | Type | Fields |
|--------|------|--------|
| Shipping Type Analysis | Donut + Bar | Shipping Type, Revenue |
| Payment Method | Clustered Bar | Payment Method, Count |
| Subscription Status | Donut Chart | Subscription Status |
| Discount Applied | Donut Chart | Discount Applied |
| Top 10 Products | Horizontal Bar | Item Purchased, Revenue |
| Purchase Frequency | Bar Chart | Frequency of Purchases |

---

### Page 2 — Filters / Slicers Panel

Add these slicers on the left panel:

| Slicer | Field | Style |
|--------|-------|-------|
| Gender | Gender | Dropdown / Tile |
| Season | Season | Dropdown / Tile |
| Category | Category | Dropdown |
| Shipping Type | Shipping Type | Dropdown |
| Subscription Status | Subscription Status | Toggle / Tile |

---

## 5. Theme Settings

Use the custom JSON theme below to match the dark GitHub-inspired palette.
Save as `powerbi/theme_dark.json` and apply via:
**View → Themes → Browse for themes**

```json
{
  "name": "Customer Shopping Dark",
  "dataColors": [
    "#58A6FF", "#3FB950", "#F78166", "#D2A8FF",
    "#FFA657", "#79C0FF", "#FF7B72", "#56D364"
  ],
  "background": "#0D1117",
  "foreground": "#E6EDF3",
  "tableAccent": "#58A6FF",
  "visualStyles": {
    "*": {
      "*": {
        "background": [{"color": {"solid": {"color": "#161B22"}}}],
        "fontColor": [{"color": {"solid": {"color": "#E6EDF3"}}}]
      }
    }
  }
}
```

---

## 6. File Structure Reference

```
powerbi/
├── Customer_Shopping_Dashboard_Guide.md   ← This file
├── generate_dashboard_images.py           ← Python image generator
├── theme_dark.json                        ← Power BI theme file
└── Customer_Shopping_Dashboard.pbix       ← Power BI file (create manually)
```

---

## 7. Preview Images

All chart previews have been pre-generated to `images/`:
- `dashboard.png` — Full composite view
- `kpi_cards.png` — KPI summary
- `revenue_gender.png` — Gender analysis
- `age_group.png` — Age group breakdown
- `subscription.png` — Subscription analysis
- `revenue_category.png` — Category revenue
- `revenue_state.png` — State-level revenue
- `shipping_analysis.png` — Shipping breakdown
- `payment_method.png` — Payment distribution
- `discount_analysis.png` — Discount impact
- `top10_products.png` — Top products
- `purchase_frequency.png` — Purchase frequency
