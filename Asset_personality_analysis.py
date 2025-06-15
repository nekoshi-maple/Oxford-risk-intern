# This script loads and analyses two CSV files: one with financial asset data and another with personality profiles.
# It focuses on GBP-denominated assets and explores their relationships with individual personality traits.
# The analysis includes:
# 1. Identifying the largest GBP asset holder and their risk tolerance.
# 2. Visualizing asset type distribution, value spread, and correlations with personality traits.
# 3. Performing linear regression and Kruskal-Wallis tests to assess statistical relationships.
# 4. Summarizing trait differences by asset type using a heatmap.


# Import library
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import statsmodels.formula.api as smf
from scipy.stats import kruskal

# Load files
assets = pd.read_csv("assets_data.csv")
personality = pd.read_csv("personality.csv")

# Merge and filter for GBP
merged_data = pd.merge(assets, personality, on="_id", how="inner")
gbp_data = merged_data[merged_data["asset_currency"] == "GBP"].copy()

# --- 0. Largest asset in GBP ---
# Largest asset holder ID and their total assets
gbp_totals = (
    gbp_data
    .groupby("_id", as_index=False)["asset_value"]
    .sum()
    .rename(columns={"asset_value": "total_gbp_assets"})
    .sort_values(by="total_gbp_assets", ascending=False)
)
top_row = gbp_totals.iloc[0]
top_id = top_row["_id"]
top_total = top_row["total_gbp_assets"]

# Get risk tolerance score
risk_score = personality[personality["_id"] == top_id]["risk_tolerance"].values[0]

# Print ID, GBP asset and risk tolerance score
print(f"ID: {top_id}\nTotal GBP Assets: {top_total}\nRisk Tolerance Score: {risk_score}")



# Define personality columns
trait_cols = ['confidence', 'risk_tolerance', 'composure', 'impulsivity', 'impact_desire']

# --- 1. Asset Type Distribution ---
plt.figure(figsize=(8, 5))
sns.countplot(data=gbp_data, x="asset_allocation", order=gbp_data["asset_allocation"].value_counts().index)
plt.title("GBP Asset Type Distribution")
plt.xlabel("Asset Type")
plt.ylabel("Count")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --- 2. Boxplot of Asset Values ---
plt.figure(figsize=(8, 5))
sns.boxplot(data=gbp_data, x="asset_allocation", y="asset_value")
plt.title("GBP Asset Value Distribution (Boxplot)")
plt.xlabel("Asset Type")
plt.ylabel("Asset Value")
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

# --- 3. Histogram of Asset Values ---
import matplotlib.ticker as ticker

plt.figure(figsize=(8, 5))
sns.histplot(gbp_data["asset_value"], bins=15, color="steelblue", kde=False)

plt.title("GBP Asset Value Histogram")
plt.xlabel("Asset Value (GBP)")
plt.ylabel("Count")

# Change Count label to integer
plt.gca().yaxis.set_major_locator(ticker.MaxNLocator(integer=True))

plt.tight_layout()
plt.show()

# --- 4. Correlation with Personality Traits ---
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Calculation
gbp_summary = gbp_data.groupby("_id", as_index=False)["asset_value"].sum().rename(columns={"asset_value": "total_assets_gbp"})
gbp_summary = pd.merge(gbp_summary, personality, on="_id", how="left")

# Correlation between GBP value and personality
correlations = gbp_summary.corr(numeric_only=True)["total_assets_gbp"][trait_cols]

# Clean labels
labels_cleaned = [trait.replace("_", " ").title() for trait in correlations.index]

# Create boxplot
plt.figure(figsize=(9, 6))
sns.barplot(x=labels_cleaned, y=correlations.values, color="steelblue")

# Clean boxplot
plt.axhline(0, color='black', linestyle='dashed')
plt.title("Correlation: GBP Assets value vs Personality Traits")
plt.ylabel("Correlation Coefficient")
plt.xlabel("Personality Trait")

# Clean labels
for i, v in enumerate(correlations.values):
    offset = 0.01 if v >= 0 else -0.025
    plt.text(i, v + offset, f"{v:.2f}", ha='center', va='bottom' if v >= 0 else 'top')

# Add margin
ymin = min(correlations.values) - 0.05
ymax = max(correlations.values) + 0.05
plt.ylim(ymin, ymax)

plt.xticks(rotation=30)
plt.tight_layout()
plt.show()


# --- 5. Linear Regression ---
formula = "total_assets_gbp ~ confidence + risk_tolerance + composure + impulsivity + impact_desire"
model = smf.ols(formula=formula, data=gbp_summary).fit()
print(model.summary())
# save in HTML
with open("regression_summary.html", "w") as f:
    f.write(model.summary().as_html())

# --- 6. Mean Personality Scores by Asset Type ---
mean_traits_by_type = gbp_data.groupby("asset_allocation")[trait_cols].mean().round(3)
print(mean_traits_by_type)

# --- 7. Kruskal-Wallis Tests ---
kruskal_results = {}
for trait in trait_cols:
    grouped = [group[trait].dropna() for name, group in gbp_data.groupby("asset_allocation")]
    stat, p = kruskal(*grouped)
    kruskal_results[trait] = {"H-statistic": stat, "p-value": p}
kruskal_df = pd.DataFrame(kruskal_results).T.round(4)
print(kruskal_df)

# --- 8. Heatmap ---
# Clean labels
pretty_trait_cols = [col.replace("_", " ").title() for col in mean_traits_by_type.columns]
mean_traits_pretty = mean_traits_by_type.copy()
mean_traits_pretty.columns = pretty_trait_cols

# Draw heatmap
plt.figure(figsize=(10, 6))
ax = sns.heatmap(mean_traits_pretty, annot=True, cmap="coolwarm", center=0.5, fmt=".3f")

# Put title and labels
plt.title("Personality Trait × Asset Allocation Heatmap")
plt.xlabel("Personality Trait")
plt.ylabel("Asset Type")

# Change scale format
colorbar = ax.collections[0].colorbar
colorbar.ax.yaxis.set_major_formatter(ticker.FormatStrFormatter('%.1f'))

plt.tight_layout()
plt.show()

