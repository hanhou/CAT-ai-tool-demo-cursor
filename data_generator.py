import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_example_data(n_samples=1000):
    """Generate example dataset for testing the visualization app"""
    
    np.random.seed(42)  # For reproducible results
    
    # Generate various column types
    data = {
        # Numeric columns
        'price': np.random.lognormal(mean=3, sigma=0.5, size=n_samples),
        'quantity': np.random.poisson(lam=50, size=n_samples),
        'rating': np.random.normal(loc=4.2, scale=0.8, size=n_samples),
        'discount_pct': np.random.beta(a=2, b=5, size=n_samples) * 100,
        'revenue': None,  # Will calculate based on price and quantity
        
        # Categorical columns
        'category': np.random.choice(['Electronics', 'Clothing', 'Books', 'Home', 'Sports'], 
                                   size=n_samples, p=[0.3, 0.25, 0.2, 0.15, 0.1]),
        'region': np.random.choice(['North', 'South', 'East', 'West'], size=n_samples),
        'customer_type': np.random.choice(['Premium', 'Standard', 'Basic'], 
                                        size=n_samples, p=[0.2, 0.5, 0.3]),
        
        # Text columns
        'product_name': [f"Product_{i:04d}" for i in range(n_samples)],
        'description': [f"Description for product {i}" for i in range(n_samples)],
        
        # Date column
        'purchase_date': [datetime(2023, 1, 1) + timedelta(days=np.random.randint(0, 365)) 
                         for _ in range(n_samples)],
    }
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Calculate derived columns
    df['revenue'] = df['price'] * df['quantity'] * (1 - df['discount_pct'] / 100)
    
    # Clip rating to valid range
    df['rating'] = np.clip(df['rating'], 1, 5)
    
    # Add some correlations for interesting scatter plots
    # Higher priced items tend to have better ratings
    mask = df['price'] > df['price'].quantile(0.75)
    df.loc[mask, 'rating'] += np.random.normal(0, 0.3, sum(mask))
    df['rating'] = np.clip(df['rating'], 1, 5)
    
    # Premium customers tend to buy more expensive items
    premium_mask = df['customer_type'] == 'Premium'
    df.loc[premium_mask, 'price'] *= np.random.uniform(1.2, 2.0, sum(premium_mask))
    
    return df

if __name__ == "__main__":
    # Test the data generator
    df = generate_example_data(100)
    print("Generated data shape:", df.shape)
    print("\nColumn info:")
    print(df.dtypes)
    print("\nFirst few rows:")
    print(df.head())
    print("\nSummary statistics:")
    print(df.describe()) 