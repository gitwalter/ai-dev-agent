"""
Test program for pandas data analysis.
Reads test.csv and performs comprehensive statistical analysis.
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Get the directory where this script is located
script_dir = Path(__file__).parent
csv_path = script_dir / "test.csv"

def load_data():
    """Load the CSV file into a pandas DataFrame."""
    print("=" * 80)
    print("LOADING DATA")
    print("=" * 80)
    df = pd.read_csv(csv_path)
    print(f"Data loaded successfully from: {csv_path}")
    print(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
    return df

def display_basic_info(df):
    """Display basic information about the dataset."""
    print("=" * 80)
    print("BASIC INFORMATION")
    print("=" * 80)
    print("\nFirst 5 rows:")
    print(df.head())
    print("\nData types:")
    print(df.dtypes)
    print("\nColumn names:")
    print(df.columns.tolist())
    print("\nMissing values:")
    print(df.isnull().sum())
    print()

def calculate_statistics(df):
    """Calculate statistical measures for numerical columns."""
    print("=" * 80)
    print("STATISTICAL ANALYSIS - NUMERICAL COLUMNS")
    print("=" * 80)
    
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    print(f"\nNumerical columns: {list(numerical_cols)}\n")
    
    # Descriptive statistics
    print("Descriptive Statistics:")
    print(df[numerical_cols].describe())
    print()
    
    # Additional statistics
    stats_df = pd.DataFrame({
        'Mean': df[numerical_cols].mean(),
        'Median': df[numerical_cols].median(),
        'Std Dev': df[numerical_cols].std(),
        'Variance': df[numerical_cols].var(),
        'Min': df[numerical_cols].min(),
        'Max': df[numerical_cols].max(),
        'Range': df[numerical_cols].max() - df[numerical_cols].min(),
        'Q1 (25%)': df[numerical_cols].quantile(0.25),
        'Q3 (75%)': df[numerical_cols].quantile(0.75),
        'IQR': df[numerical_cols].quantile(0.75) - df[numerical_cols].quantile(0.25),
        'Skewness': df[numerical_cols].skew(),
        'Kurtosis': df[numerical_cols].kurtosis()
    })
    
    print("\nDetailed Statistics:")
    print(stats_df.round(2))
    print()

def find_outliers(df):
    """Identify outliers using IQR method."""
    print("=" * 80)
    print("OUTLIER DETECTION (IQR Method)")
    print("=" * 80)
    
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numerical_cols:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]
        
        if len(outliers) > 0:
            print(f"\n{col}:")
            print(f"  Q1: {Q1:.2f}, Q3: {Q3:.2f}, IQR: {IQR:.2f}")
            print(f"  Lower bound: {lower_bound:.2f}, Upper bound: {upper_bound:.2f}")
            print(f"  Found {len(outliers)} outlier(s):")
            print(f"  {outliers[['product_name', col]].to_string(index=False)}")
        else:
            print(f"\n{col}: No outliers detected")
    print()

def categorical_analysis(df):
    """Analyze categorical columns."""
    print("=" * 80)
    print("CATEGORICAL ANALYSIS")
    print("=" * 80)
    
    categorical_cols = df.select_dtypes(include=['object']).columns
    
    for col in categorical_cols:
        if col != 'sale_date':  # Skip date column for now
            print(f"\n{col}:")
            value_counts = df[col].value_counts()
            print(value_counts)
            print(f"Unique values: {df[col].nunique()}")
            print(f"Most frequent: {df[col].mode()[0]} ({value_counts.iloc[0]} occurrences)")
    print()

def group_analysis(df):
    """Perform group-by analysis."""
    print("=" * 80)
    print("GROUP-BY ANALYSIS")
    print("=" * 80)
    
    # Group by category
    print("\nBy Category:")
    category_stats = df.groupby('category').agg({
        'price': ['mean', 'min', 'max', 'count'],
        'quantity_sold': ['sum', 'mean'],
        'revenue': ['sum', 'mean'],
        'rating': 'mean'
    }).round(2)
    print(category_stats)
    print()
    
    # Group by region
    print("\nBy Region:")
    region_stats = df.groupby('region').agg({
        'revenue': ['sum', 'mean'],
        'quantity_sold': 'sum',
        'rating': 'mean',
        'customer_age': 'mean'
    }).round(2)
    print(region_stats)
    print()

def correlation_analysis(df):
    """Calculate correlation matrix."""
    print("=" * 80)
    print("CORRELATION ANALYSIS")
    print("=" * 80)
    
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    correlation_matrix = df[numerical_cols].corr()
    
    print("\nCorrelation Matrix:")
    print(correlation_matrix.round(3))
    print()
    
    # Find strong correlations
    print("Strong Correlations (|r| > 0.7):")
    for i in range(len(correlation_matrix.columns)):
        for j in range(i+1, len(correlation_matrix.columns)):
            corr_value = correlation_matrix.iloc[i, j]
            if abs(corr_value) > 0.7:
                print(f"  {correlation_matrix.columns[i]} <-> {correlation_matrix.columns[j]}: {corr_value:.3f}")
    print()

def min_max_analysis(df):
    """Find min and max values with context."""
    print("=" * 80)
    print("MIN/MAX VALUE ANALYSIS")
    print("=" * 80)
    
    numerical_cols = df.select_dtypes(include=[np.number]).columns
    
    for col in numerical_cols:
        min_val = df[col].min()
        max_val = df[col].max()
        
        min_row = df.loc[df[col].idxmin()]
        max_row = df.loc[df[col].idxmax()]
        
        print(f"\n{col}:")
        print(f"  Minimum: {min_val:.2f} (Product: {min_row['product_name']})")
        print(f"  Maximum: {max_val:.2f} (Product: {max_row['product_name']})")
    print()

def summary_report(df):
    """Generate a summary report."""
    print("=" * 80)
    print("SUMMARY REPORT")
    print("=" * 80)
    
    total_revenue = df['revenue'].sum()
    total_quantity = df['quantity_sold'].sum()
    avg_price = df['price'].mean()
    avg_rating = df['rating'].mean()
    
    print(f"\nTotal Revenue: ${total_revenue:,.2f}")
    print(f"Total Quantity Sold: {total_quantity:,}")
    print(f"Average Price: ${avg_price:.2f}")
    print(f"Average Rating: {avg_rating:.2f}")
    print(f"Total Products: {len(df)}")
    print(f"Unique Categories: {df['category'].nunique()}")
    print(f"Unique Regions: {df['region'].nunique()}")
    
    # Best and worst performing products
    best_product = df.loc[df['revenue'].idxmax()]
    worst_product = df.loc[df['revenue'].idxmin()]
    
    print(f"\nBest Performing Product:")
    print(f"  {best_product['product_name']} - Revenue: ${best_product['revenue']:.2f}")
    
    print(f"\nWorst Performing Product:")
    print(f"  {worst_product['product_name']} - Revenue: ${worst_product['revenue']:.2f}")
    print()

def main():
    """Main function to run all analyses."""
    try:
        # Load data
        df = load_data()
        
        # Perform analyses
        display_basic_info(df)
        calculate_statistics(df)
        find_outliers(df)
        categorical_analysis(df)
        group_analysis(df)
        correlation_analysis(df)
        min_max_analysis(df)
        summary_report(df)
        
        print("=" * 80)
        print("ANALYSIS COMPLETE")
        print("=" * 80)
        
    except FileNotFoundError:
        print(f"Error: Could not find test.csv in {csv_path}")
        print("Please ensure test.csv exists in the same directory as this script.")
    except Exception as e:
        print(f"Error during analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

