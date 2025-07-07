#!/usr/bin/env python3
"""
Quick dataset analysis for XOFlowers optimization
"""

import pandas as pd
import json
from collections import Counter

def analyze_dataset():
    """Analyze the current dataset"""
    print("🔍 ANALYZING XOFLOWERS DATASET")
    print("="*50)
    
    # Load dataset
    df = pd.read_csv('chunks_data.csv')
    
    print(f"📊 Dataset Statistics:")
    print(f"   Total products: {len(df)}")
    print(f"   Unique categories: {df['category'].nunique()}")
    print(f"   Unique flower types: {df['flower_type'].nunique()}")
    
    print(f"\n📂 Categories:")
    for cat, count in df['category'].value_counts().items():
        print(f"   {cat}: {count} products")
    
    print(f"\n🌸 Flower Types:")
    for flower, count in df['flower_type'].value_counts().head(10).items():
        print(f"   {flower}: {count} products")
    
    print(f"\n💰 Price Range:")
    prices = pd.to_numeric(df['price'], errors='coerce')
    print(f"   Min: {prices.min():.0f} MDL")
    print(f"   Max: {prices.max():.0f} MDL")
    print(f"   Average: {prices.mean():.0f} MDL")
    
    # Analyze text content for optimization opportunities
    print(f"\n📝 Text Analysis:")
    all_text = ' '.join(df['primary_text'].astype(str))
    
    # Common Romanian flower terms
    flower_terms = ['trandafir', 'floare', 'buchet', 'lalele', 'garoafe', 'crizanteme', 'orhidee']
    print(f"   Common flower terms found:")
    for term in flower_terms:
        count = all_text.lower().count(term)
        if count > 0:
            print(f"     {term}: {count} occurrences")
    
    # Color analysis
    color_terms = ['roșu', 'alb', 'roz', 'galben', 'violet', 'albastru', 'verde', 'portocaliu']
    print(f"   Color terms found:")
    for color in color_terms:
        count = all_text.lower().count(color)
        if count > 0:
            print(f"     {color}: {count} occurrences")

if __name__ == "__main__":
    analyze_dataset()
