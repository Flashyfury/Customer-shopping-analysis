"""
Customer Shopping Analytics - Dashboard Image Generator
Generates all charts and KPI cards matching the Power BI dashboard layout.
Run: .venv/bin/python powerbi/generate_dashboard_images.py
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import warnings
warnings.filterwarnings("ignore")

# ── Colour palette ──────────────────────────────────────────────────────────
PALETTE = {
    "bg":      "#0D1117",
    "panel":   "#161B22",
    "card":    "#1C2128",
    "accent1": "#58A6FF",
    "accent2": "#3FB950",
    "accent3": "#F78166",
    "accent4": "#D2A8FF",
    "accent5": "#FFA657",
    "accent6": "#79C0FF",
    "text":    "#E6EDF3",
    "subtext": "#8B949E",
    "grid":    "#21262D",
}

CHART_COLORS = [
    PALETTE["accent1"], PALETTE["accent2"], PALETTE["accent3"],
    PALETTE["accent4"], PALETTE["accent5"], PALETTE["accent6"],
    "#FF7B72", "#56D364", "#FFA657", "#A5D6FF",
]

def apply_dark_style(ax, title="", xlabel="", ylabel=""):
    ax.set_facecolor(PALETTE["panel"])
    ax.tick_params(colors=PALETTE["text"], labelsize=9)
    ax.xaxis.label.set_color(PALETTE["subtext"])
    ax.yaxis.label.set_color(PALETTE["subtext"])
    for spine in ax.spines.values():
        spine.set_edgecolor(PALETTE["grid"])
    ax.grid(axis="y", color=PALETTE["grid"], linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)
    if title:
        ax.set_title(title, color=PALETTE["text"], fontsize=11, fontweight="bold", pad=10)
    if xlabel:
        ax.set_xlabel(xlabel, color=PALETTE["subtext"], fontsize=9)
    if ylabel:
        ax.set_ylabel(ylabel, color=PALETTE["subtext"], fontsize=9)

# ── Load data ────────────────────────────────────────────────────────────────
df = pd.read_csv("data/customer_shopping_behavior.csv")
df.columns = df.columns.str.strip()
df["Revenue"] = df["Purchase Amount (USD)"]

bins   = [0, 18, 25, 35, 45, 60, 100]
labels = ["<18", "18-25", "26-35", "36-45", "46-60", "60+"]
df["Age Group"] = pd.cut(df["Age"], bins=bins, labels=labels, right=True)

# ── Aggregations ─────────────────────────────────────────────────────────────
total_revenue   = df["Revenue"].sum()
total_customers = df["Customer ID"].nunique()
avg_purchase    = df["Revenue"].mean()
avg_rating      = df["Review Rating"].mean()

rev_category = df.groupby("Category")["Revenue"].sum().sort_values(ascending=False)
rev_gender   = df.groupby("Gender")["Revenue"].sum().sort_values(ascending=False)
rev_state    = df.groupby("Location")["Revenue"].sum().sort_values(ascending=False).head(15)
rev_age      = df.groupby("Age Group", observed=True)["Revenue"].sum()
ship_counts  = df["Shipping Type"].value_counts()
payment_dist = df["Payment Method"].value_counts()
sub_status   = df["Subscription Status"].value_counts()
discount_dist= df["Discount Applied"].value_counts()
top10_prod   = df.groupby("Item Purchased")["Revenue"].sum().sort_values(ascending=False).head(10)
freq_dist    = df["Frequency of Purchases"].value_counts()

print("Data loaded. Generating images...")

# ════════════════════════════════════════════════════════════════════════════
# 1. KPI CARDS
# ════════════════════════════════════════════════════════════════════════════
fig, axes = plt.subplots(1, 4, figsize=(16, 3.5))
fig.patch.set_facecolor(PALETTE["bg"])
kpis = [
    ("Total Revenue",    f"${total_revenue:,.0f}", PALETTE["accent2"]),
    ("Total Customers",  f"{total_customers:,}",   PALETTE["accent1"]),
    ("Avg Purchase",     f"${avg_purchase:.2f}",   PALETTE["accent5"]),
    ("Avg Rating",       f"{avg_rating:.2f} / 5",  PALETTE["accent4"]),
]
for ax, (label, value, color) in zip(axes, kpis):
    ax.set_facecolor(PALETTE["card"])
    for sp in ax.spines.values():
        sp.set_edgecolor(color); sp.set_linewidth(2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.axhline(y=0.92, xmin=0.05, xmax=0.95, color=color, linewidth=3, alpha=0.9)
    ax.text(0.5, 0.62, value, transform=ax.transAxes,
            ha="center", va="center", fontsize=22, fontweight="bold",
            color=color, fontfamily="monospace")
    ax.text(0.5, 0.28, label, transform=ax.transAxes,
            ha="center", va="center", fontsize=10, color=PALETTE["subtext"])
plt.suptitle("Customer Shopping Analytics — KPI Overview",
             color=PALETTE["text"], fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout(pad=1.5)
plt.savefig("images/kpi_cards.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: kpi_cards.png")

# ════════════════════════════════════════════════════════════════════════════
# 2. REVENUE BY CATEGORY
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(8, 5))
fig.patch.set_facecolor(PALETTE["bg"])
apply_dark_style(ax, "Revenue by Category", ylabel="Revenue (USD)")
bars = ax.bar(rev_category.index, rev_category.values,
              color=CHART_COLORS[:len(rev_category)], edgecolor="none", width=0.6)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+500,
            f"${bar.get_height():,.0f}", ha="center", va="bottom",
            color=PALETTE["text"], fontsize=9, fontweight="bold")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
plt.tight_layout()
plt.savefig("images/revenue_category.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: revenue_category.png")

# ════════════════════════════════════════════════════════════════════════════
# 3. REVENUE BY GENDER
# ════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
fig.patch.set_facecolor(PALETTE["bg"])
wc = [PALETTE["accent1"], PALETTE["accent3"]]
wedges,texts,autotexts = ax1.pie(rev_gender.values, labels=rev_gender.index,
    autopct="%1.1f%%", colors=wc, startangle=90,
    wedgeprops={"width":0.55,"edgecolor":PALETTE["bg"],"linewidth":3})
for t in texts:  t.set_color(PALETTE["text"]); t.set_fontsize(11)
for at in autotexts: at.set_color(PALETTE["bg"]); at.set_fontweight("bold"); at.set_fontsize(10)
ax1.set_facecolor(PALETTE["panel"])
ax1.set_title("Revenue Share by Gender", color=PALETTE["text"], fontsize=11, fontweight="bold")
apply_dark_style(ax2, "Revenue by Gender", ylabel="Revenue (USD)")
bars = ax2.bar(rev_gender.index, rev_gender.values, color=wc, edgecolor="none", width=0.5)
for bar in bars:
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+1000,
             f"${bar.get_height():,.0f}", ha="center", va="bottom",
             color=PALETTE["text"], fontsize=10, fontweight="bold")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
plt.suptitle("Gender Revenue Analysis", color=PALETTE["text"], fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("images/revenue_gender.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: revenue_gender.png")

# ════════════════════════════════════════════════════════════════════════════
# 4. REVENUE BY STATE
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 7))
fig.patch.set_facecolor(PALETTE["bg"])
apply_dark_style(ax, "Top 15 States by Revenue", xlabel="Revenue (USD)")
ax.grid(axis="x", color=PALETTE["grid"], linewidth=0.5, alpha=0.7)
ax.grid(axis="y", color="none")
clrs = plt.cm.Blues(np.linspace(0.4, 0.9, len(rev_state)))[::-1]
bars = ax.barh(rev_state.index, rev_state.values, color=clrs, edgecolor="none", height=0.7)
for bar in bars:
    ax.text(bar.get_width()+200, bar.get_y()+bar.get_height()/2,
            f"${bar.get_width():,.0f}", va="center", ha="left",
            color=PALETTE["text"], fontsize=8.5)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
ax.invert_yaxis()
plt.tight_layout()
plt.savefig("images/revenue_state.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: revenue_state.png")

# ════════════════════════════════════════════════════════════════════════════
# 5. REVENUE BY AGE GROUP
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor(PALETTE["bg"])
apply_dark_style(ax, "Revenue by Age Group", xlabel="Age Group", ylabel="Revenue (USD)")
rev_age_ord = rev_age.reindex(labels)
bars = ax.bar(rev_age_ord.index.astype(str), rev_age_ord.values,
              color=CHART_COLORS[:len(rev_age_ord)], edgecolor="none", width=0.65)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+300,
            f"${bar.get_height():,.0f}", ha="center", va="bottom",
            color=PALETTE["text"], fontsize=9, fontweight="bold")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
plt.tight_layout()
plt.savefig("images/age_group.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: age_group.png")

# ════════════════════════════════════════════════════════════════════════════
# 6. SHIPPING TYPE
# ════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
fig.patch.set_facecolor(PALETTE["bg"])
wc2 = CHART_COLORS[:len(ship_counts)]
wedges,texts,autotexts = ax1.pie(ship_counts.values, labels=ship_counts.index,
    autopct="%1.1f%%", colors=wc2, startangle=140,
    wedgeprops={"width":0.55,"edgecolor":PALETTE["bg"],"linewidth":2})
for t in texts:  t.set_color(PALETTE["text"]); t.set_fontsize(9)
for at in autotexts: at.set_color(PALETTE["bg"]); at.set_fontweight("bold"); at.set_fontsize(8.5)
ax1.set_facecolor(PALETTE["panel"])
ax1.set_title("Shipping Type Distribution", color=PALETTE["text"], fontsize=11, fontweight="bold")
rev_ship = df.groupby("Shipping Type")["Revenue"].sum().sort_values(ascending=False)
apply_dark_style(ax2, "Revenue by Shipping Type", ylabel="Revenue (USD)")
bars = ax2.bar(rev_ship.index, rev_ship.values, color=CHART_COLORS[:len(rev_ship)], edgecolor="none", width=0.6)
for bar in bars:
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+200,
             f"${bar.get_height():,.0f}", ha="center", va="bottom",
             color=PALETTE["text"], fontsize=8.5, fontweight="bold")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
ax2.tick_params(axis="x", rotation=20)
plt.suptitle("Shipping Type Analysis", color=PALETTE["text"], fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("images/shipping_analysis.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: shipping_analysis.png")

# ════════════════════════════════════════════════════════════════════════════
# 7. PAYMENT METHOD
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor(PALETTE["bg"])
apply_dark_style(ax, "Payment Method Distribution", ylabel="Number of Transactions")
bars = ax.bar(payment_dist.index, payment_dist.values,
              color=CHART_COLORS[:len(payment_dist)], edgecolor="none", width=0.6)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
            f"{bar.get_height():,}", ha="center", va="bottom",
            color=PALETTE["text"], fontsize=9, fontweight="bold")
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig("images/payment_method.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: payment_method.png")

# ════════════════════════════════════════════════════════════════════════════
# 8. SUBSCRIPTION STATUS
# ════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
fig.patch.set_facecolor(PALETTE["bg"])
cs = [PALETTE["accent2"], PALETTE["accent3"]]
wedges,texts,autotexts = ax1.pie(sub_status.values, labels=sub_status.index,
    autopct="%1.1f%%", colors=cs, startangle=90,
    wedgeprops={"width":0.55,"edgecolor":PALETTE["bg"],"linewidth":3})
for t in texts:  t.set_color(PALETTE["text"]); t.set_fontsize(11)
for at in autotexts: at.set_color(PALETTE["bg"]); at.set_fontweight("bold"); at.set_fontsize(10)
ax1.set_facecolor(PALETTE["panel"])
ax1.set_title("Subscription Status", color=PALETTE["text"], fontsize=11, fontweight="bold")
rev_sub = df.groupby("Subscription Status")["Revenue"].sum()
apply_dark_style(ax2, "Revenue by Subscription Status", ylabel="Revenue (USD)")
bars = ax2.bar(rev_sub.index, rev_sub.values, color=cs, edgecolor="none", width=0.5)
for bar in bars:
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+500,
             f"${bar.get_height():,.0f}", ha="center", va="bottom",
             color=PALETTE["text"], fontsize=10, fontweight="bold")
ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
plt.suptitle("Subscription Analysis", color=PALETTE["text"], fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("images/subscription.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: subscription.png")

# ════════════════════════════════════════════════════════════════════════════
# 9. DISCOUNT APPLIED
# ════════════════════════════════════════════════════════════════════════════
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))
fig.patch.set_facecolor(PALETTE["bg"])
cd = [PALETTE["accent5"], PALETTE["accent6"]]
wedges,texts,autotexts = ax1.pie(discount_dist.values, labels=discount_dist.index,
    autopct="%1.1f%%", colors=cd, startangle=90,
    wedgeprops={"width":0.55,"edgecolor":PALETTE["bg"],"linewidth":3})
for t in texts:  t.set_color(PALETTE["text"]); t.set_fontsize(11)
for at in autotexts: at.set_color(PALETTE["bg"]); at.set_fontweight("bold"); at.set_fontsize(10)
ax1.set_facecolor(PALETTE["panel"])
ax1.set_title("Discount Applied", color=PALETTE["text"], fontsize=11, fontweight="bold")
avg_disc = df.groupby("Discount Applied")["Revenue"].mean()
apply_dark_style(ax2, "Avg Purchase: Discount vs No Discount", ylabel="Avg Purchase (USD)")
bars = ax2.bar(avg_disc.index, avg_disc.values, color=cd, edgecolor="none", width=0.5)
for bar in bars:
    ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.2,
             f"${bar.get_height():.2f}", ha="center", va="bottom",
             color=PALETTE["text"], fontsize=10, fontweight="bold")
plt.suptitle("Discount Applied Analysis", color=PALETTE["text"], fontsize=13, fontweight="bold", y=1.02)
plt.tight_layout()
plt.savefig("images/discount_analysis.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: discount_analysis.png")

# ════════════════════════════════════════════════════════════════════════════
# 10. TOP 10 PRODUCTS
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(10, 6))
fig.patch.set_facecolor(PALETTE["bg"])
apply_dark_style(ax, "Top 10 Products by Revenue", xlabel="Revenue (USD)")
ax.grid(axis="x", color=PALETTE["grid"], linewidth=0.5, alpha=0.7)
ax.grid(axis="y", color="none")
clrs3 = plt.cm.YlOrRd(np.linspace(0.4, 0.9, len(top10_prod)))[::-1]
bars = ax.barh(top10_prod.index, top10_prod.values, color=clrs3, edgecolor="none", height=0.7)
for bar in bars:
    ax.text(bar.get_width()+100, bar.get_y()+bar.get_height()/2,
            f"${bar.get_width():,.0f}", va="center", ha="left",
            color=PALETTE["text"], fontsize=8.5)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
ax.invert_yaxis()
plt.tight_layout()
plt.savefig("images/top10_products.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: top10_products.png")

# ════════════════════════════════════════════════════════════════════════════
# 11. PURCHASE FREQUENCY
# ════════════════════════════════════════════════════════════════════════════
fig, ax = plt.subplots(figsize=(9, 5))
fig.patch.set_facecolor(PALETTE["bg"])
apply_dark_style(ax, "Purchase Frequency Distribution", ylabel="Number of Customers")
freq_sorted = freq_dist.sort_values(ascending=False)
bars = ax.bar(freq_sorted.index, freq_sorted.values,
              color=CHART_COLORS[:len(freq_sorted)], edgecolor="none", width=0.65)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+5,
            f"{bar.get_height():,}", ha="center", va="bottom",
            color=PALETTE["text"], fontsize=9, fontweight="bold")
ax.tick_params(axis="x", rotation=20)
plt.tight_layout()
plt.savefig("images/purchase_frequency.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: purchase_frequency.png")

# ════════════════════════════════════════════════════════════════════════════
# 12. FULL DASHBOARD COMPOSITE
# ════════════════════════════════════════════════════════════════════════════
fig = plt.figure(figsize=(24, 18))
fig.patch.set_facecolor(PALETTE["bg"])
fig.text(0.5, 0.97, "Customer Shopping Analytics Dashboard",
         ha="center", va="top", fontsize=20, fontweight="bold", color=PALETTE["text"])
fig.text(0.5, 0.955,
         f"Total Revenue: ${total_revenue:,.0f}  |  Customers: {total_customers:,}  |  "
         f"Avg Purchase: ${avg_purchase:.2f}  |  Avg Rating: {avg_rating:.2f}",
         ha="center", va="top", fontsize=11, color=PALETTE["subtext"])

gs = gridspec.GridSpec(4, 4, figure=fig, top=0.93, bottom=0.04, hspace=0.45, wspace=0.35)

# KPI row
kpi_data = [
    ("Total Revenue",   f"${total_revenue:,.0f}", PALETTE["accent2"]),
    ("Total Customers", f"{total_customers:,}",   PALETTE["accent1"]),
    ("Avg Purchase",    f"${avg_purchase:.2f}",   PALETTE["accent5"]),
    ("Avg Rating",      f"{avg_rating:.2f} / 5",  PALETTE["accent4"]),
]
for i,(label,val,col) in enumerate(kpi_data):
    ax = fig.add_subplot(gs[0,i])
    ax.set_facecolor(PALETTE["card"])
    for sp in ax.spines.values(): sp.set_edgecolor(col); sp.set_linewidth(2)
    ax.set_xticks([]); ax.set_yticks([])
    ax.axhline(y=0.9, xmin=0.05, xmax=0.95, color=col, linewidth=3, alpha=0.9)
    ax.text(0.5,0.58,val,transform=ax.transAxes,ha="center",va="center",
            fontsize=16,fontweight="bold",color=col,fontfamily="monospace")
    ax.text(0.5,0.25,label,transform=ax.transAxes,ha="center",va="center",
            fontsize=8.5,color=PALETTE["subtext"])

# Revenue by Category
ax = fig.add_subplot(gs[1,:2])
apply_dark_style(ax,"Revenue by Category")
bars=ax.bar(rev_category.index,rev_category.values,color=CHART_COLORS[:len(rev_category)],edgecolor="none",width=0.6)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+200,f"${bar.get_height()/1000:.0f}K",
            ha="center",va="bottom",color=PALETTE["text"],fontsize=8,fontweight="bold")
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))

# Gender donut
ax=fig.add_subplot(gs[1,2])
wc=[PALETTE["accent1"],PALETTE["accent3"]]
wedges,texts,autotexts=ax.pie(rev_gender.values,labels=rev_gender.index,autopct="%1.1f%%",
    colors=wc,startangle=90,wedgeprops={"width":0.55,"edgecolor":PALETTE["bg"],"linewidth":2})
for t in texts: t.set_color(PALETTE["text"]); t.set_fontsize(8)
for at in autotexts: at.set_color(PALETTE["bg"]); at.set_fontweight("bold"); at.set_fontsize(7.5)
ax.set_facecolor(PALETTE["panel"])
ax.set_title("Revenue by Gender",color=PALETTE["text"],fontsize=10,fontweight="bold")

# Subscription donut
ax=fig.add_subplot(gs[1,3])
cs=[PALETTE["accent2"],PALETTE["accent3"]]
wedges,texts,autotexts=ax.pie(sub_status.values,labels=sub_status.index,autopct="%1.1f%%",
    colors=cs,startangle=90,wedgeprops={"width":0.55,"edgecolor":PALETTE["bg"],"linewidth":2})
for t in texts: t.set_color(PALETTE["text"]); t.set_fontsize(8)
for at in autotexts: at.set_color(PALETTE["bg"]); at.set_fontweight("bold"); at.set_fontsize(7.5)
ax.set_facecolor(PALETTE["panel"])
ax.set_title("Subscription Status",color=PALETTE["text"],fontsize=10,fontweight="bold")

# Top 10 Products
ax=fig.add_subplot(gs[2,:2])
apply_dark_style(ax,"Top 10 Products by Revenue")
ax.grid(axis="x",color=PALETTE["grid"],linewidth=0.5,alpha=0.7)
ax.grid(axis="y",color="none")
clrs4=plt.cm.YlOrRd(np.linspace(0.4,0.9,10))[::-1]
bars=ax.barh(top10_prod.index,top10_prod.values,color=clrs4,edgecolor="none",height=0.65)
for bar in bars:
    ax.text(bar.get_width()+50,bar.get_y()+bar.get_height()/2,
            f"${bar.get_width()/1000:.1f}K",va="center",ha="left",color=PALETTE["text"],fontsize=7.5)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
ax.invert_yaxis(); ax.tick_params(labelsize=7.5)

# Shipping donut
ax=fig.add_subplot(gs[2,2])
wcs=CHART_COLORS[:len(ship_counts)]
wedges,texts,autotexts=ax.pie(ship_counts.values,labels=ship_counts.index,autopct="%1.0f%%",
    colors=wcs,startangle=140,wedgeprops={"width":0.55,"edgecolor":PALETTE["bg"],"linewidth":2})
for t in texts: t.set_color(PALETTE["text"]); t.set_fontsize(7)
for at in autotexts: at.set_color(PALETTE["bg"]); at.set_fontweight("bold"); at.set_fontsize(7)
ax.set_facecolor(PALETTE["panel"])
ax.set_title("Shipping Type",color=PALETTE["text"],fontsize=10,fontweight="bold")

# Payment Method
ax=fig.add_subplot(gs[2,3])
apply_dark_style(ax,"Payment Method")
bars=ax.bar(payment_dist.index,payment_dist.values,color=CHART_COLORS[:len(payment_dist)],edgecolor="none",width=0.6)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+2,f"{bar.get_height()}",
            ha="center",va="bottom",color=PALETTE["text"],fontsize=7)
ax.tick_params(axis="x",rotation=30,labelsize=7); ax.tick_params(axis="y",labelsize=7)

# Revenue by State
ax=fig.add_subplot(gs[3,:2])
apply_dark_style(ax,"Top 15 States by Revenue")
ax.grid(axis="x",color=PALETTE["grid"],linewidth=0.5,alpha=0.7); ax.grid(axis="y",color="none")
clrs5=plt.cm.Blues(np.linspace(0.4,0.9,len(rev_state)))[::-1]
bars=ax.barh(rev_state.index,rev_state.values,color=clrs5,edgecolor="none",height=0.7)
for bar in bars:
    ax.text(bar.get_width()+30,bar.get_y()+bar.get_height()/2,
            f"${bar.get_width()/1000:.1f}K",va="center",ha="left",color=PALETTE["text"],fontsize=7)
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
ax.invert_yaxis(); ax.tick_params(labelsize=7.5)

# Age Group
ax=fig.add_subplot(gs[3,2])
apply_dark_style(ax,"Revenue by Age Group")
rev_age_ord=rev_age.reindex(labels)
bars=ax.bar(rev_age_ord.index.astype(str),rev_age_ord.values,
            color=CHART_COLORS[:len(rev_age_ord)],edgecolor="none",width=0.7)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+100,
            f"${bar.get_height()/1000:.0f}K",ha="center",va="bottom",
            color=PALETTE["text"],fontsize=7)
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f"${x/1000:.0f}K"))
ax.tick_params(labelsize=8)

# Purchase Frequency
ax=fig.add_subplot(gs[3,3])
apply_dark_style(ax,"Purchase Frequency")
freq_s=freq_dist.sort_values(ascending=False)
bars=ax.bar(freq_s.index,freq_s.values,color=CHART_COLORS[:len(freq_s)],edgecolor="none",width=0.65)
for bar in bars:
    ax.text(bar.get_x()+bar.get_width()/2,bar.get_height()+2,f"{bar.get_height()}",
            ha="center",va="bottom",color=PALETTE["text"],fontsize=7)
ax.tick_params(axis="x",rotation=25,labelsize=7); ax.tick_params(axis="y",labelsize=7)

plt.savefig("images/dashboard.png", dpi=150, bbox_inches="tight", facecolor=PALETTE["bg"])
plt.close(); print("Done: dashboard.png  — FULL DASHBOARD COMPOSITE")
print("\nAll dashboard images generated successfully!")
