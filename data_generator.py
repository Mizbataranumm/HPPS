import pandas as pd
import numpy as np
import random
import os

np.random.seed(42)
random.seed(42)

NUM_RECORDS = 1500

# Base multipliers in Lakhs (1 Lakh = 100,000 INR)
# Mumbai/Delhi will have higher base rates
def generate_data(num_records):
    data = []
    
    city_tiers = [1, 2, 3]
    # Tier 1a: Mumbai, Delhi
    # Tier 1b: Bangalore, Pune, Hyderabad, Chennai
    # Tier 2: Jaipur, Ahmedabad, Lucknow
    # Tier 3: Small towns
    
    for _ in range(num_records):
        tier_choice = random.choices([1.1, 1.2, 2, 3], weights=[0.2, 0.4, 0.25, 0.15])[0]
        
        if tier_choice == 1.1:
            city_tier = 1 # Mumbai/Delhi
            base_rate_sqft = random.uniform(15000, 35000) # INR per sqft
        elif tier_choice == 1.2:
            city_tier = 1 # Bangalore/Pune
            base_rate_sqft = random.uniform(6000, 15000)
        elif tier_choice == 2:
            city_tier = 2
            base_rate_sqft = random.uniform(3000, 6000)
        else:
            city_tier = 3
            base_rate_sqft = random.uniform(1500, 3000)
            
        area = int(random.triangular(400, 4000, 1200))
        bhk = max(1, min(5, int(area / 400) + random.randint(-1, 1)))
        bathrooms = max(1, min(bhk + 1, bhk + random.randint(-1, 1)))
        age = random.randint(0, 30)
        garage = 1 if (city_tier == 3 or area > 1000 or random.random() > 0.5) else 0
        location_score = round(random.uniform(4.0, 10.0), 1)
        quality_score = round(random.uniform(4.0, 10.0), 1)
        
        # Calculate price based on sensible rules
        # 1. Base price by area
        base_price = area * base_rate_sqft
        
        # 2. Add premium for extra bedrooms/baths (assumes better layout)
        layout_premium = (bhk * 200000) + (bathrooms * 150000)
        
        # 3. Deduction for age (depreciation)
        age_deduction = base_price * (age * 0.01) # 1% deduction per year
        
        # 4. Premium for garage
        garage_premium = 300000 if garage == 1 else 0
        
        # 5. Location and Quality multipliers
        loc_mult = 1.0 + ((location_score - 5.0) * 0.05) # +/- 25% max
        qual_mult = 1.0 + ((quality_score - 5.0) * 0.05) # +/- 25% max
        
        final_price = (base_price + layout_premium + garage_premium - age_deduction) * loc_mult * qual_mult
        
        # Add some random noise
        final_price *= random.uniform(0.95, 1.05)
        
        # Convert to Lakhs for easier reading/training target
        price_lakhs = round(final_price / 100000, 2)
        
        # Clip to ensure it matches realistic boundaries
        if tier_choice == 1.1:
            price_lakhs = max(80.0, min(500.0, price_lakhs))
        elif tier_choice == 1.2:
            price_lakhs = max(40.0, min(250.0, price_lakhs))
        elif tier_choice == 2:
            price_lakhs = max(20.0, min(80.0, price_lakhs))
        else:
            price_lakhs = max(8.0, min(35.0, price_lakhs))
        
        data.append({
            'area_sqft': area,
            'bhk': bhk,
            'bathrooms': bathrooms,
            'age_years': age,
            'garage': garage,
            'location_score': location_score,
            'quality_score': quality_score,
            'city_tier': city_tier,
            'price_lakhs': price_lakhs
        })
        
    df = pd.DataFrame(data)
    df.to_csv('indian_housing_data.csv', index=False)
    print(f"Generated {len(df)} records. Saved to indian_housing_data.csv")
    print(df.head())
    print("\nPrice ranges by tier:")
    print(df.groupby('city_tier')['price_lakhs'].describe())

if __name__ == "__main__":
    generate_data(NUM_RECORDS)
