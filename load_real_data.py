#!/usr/bin/env python3
"""
Script pentru încărcarea datelor XOFlowers în ChromaDB
Încarcă toate cele 709 produse din chunks_data.csv
"""

import csv
import json
import os
import sys
from datetime import datetime

def load_xoflowers_data():
    """Load XOFlowers products from CSV into ChromaDB"""
    
    # Check if CSV exists
    csv_path = "chunks_data.csv"
    if not os.path.exists(csv_path):
        print(f"❌ Error: {csv_path} not found!")
        print("Please ensure chunks_data.csv is in the current directory.")
        return False
    
    try:
        # Import here to avoid circular imports
        from app import agent
        
        print("🌸 Starting XOFlowers data loading...")
        print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        products_loaded = 0
        categories_stats = {}
        price_ranges = {"budget": 0, "medium": 0, "premium": 0, "luxury": 0}
        
        # Category mapping for ChromaDB collections
        category_mapping = {
            "Chando": "gifts",
            "Peonies": "bouquets", 
            "French roses": "bouquets",
            "Basket / Boxes with flowers": "boxes",
            "Author's bouquets": "compositions"
        }
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            print("📊 Processing products...")
            
            for row in reader:
                if row['chunk_type'] == 'product':
                    try:
                        # Extract product information
                        description = row['primary_text']
                        name = description.split(' - ')[0] if ' - ' in description else description[:100]
                        price = float(row['price']) if row['price'] else 0.0
                        original_category = row['category']
                        
                        # Map to collection
                        collection_name = category_mapping.get(original_category, "bouquets")
                        
                        # Extract colors intelligently
                        colors = extract_colors_from_text(description)
                        
                        # Extract occasions
                        occasions = extract_occasions_from_text(description)
                        
                        # Create enhanced product object
                        product = {
                            "id": row['chunk_id'],
                            "name": name,
                            "description": description,
                            "price": price,
                            "category": original_category,
                            "flower_type": row['flower_type'],
                            "colors": colors,
                            "occasions": occasions,
                            "url": row['url'],
                            "in_stock": True
                        }
                        
                        # Add to ChromaDB
                        agent.chroma_manager.add_product(product, collection_name)
                        
                        # Update statistics
                        products_loaded += 1
                        categories_stats[original_category] = categories_stats.get(original_category, 0) + 1
                        
                        # Price range statistics
                        if price < 500:
                            price_ranges["budget"] += 1
                        elif price < 1000:
                            price_ranges["medium"] += 1
                        elif price < 2500:
                            price_ranges["premium"] += 1
                        else:
                            price_ranges["luxury"] += 1
                        
                        # Progress indicator
                        if products_loaded % 50 == 0:
                            print(f"   📦 Loaded {products_loaded} products...")
                    
                    except Exception as e:
                        print(f"⚠️  Error processing product {row.get('chunk_id', 'unknown')}: {e}")
        
        # Print statistics
        print(f"\n✅ Successfully loaded {products_loaded} products!")
        print("\n📊 **Loading Statistics:**")
        print(f"   Total products: {products_loaded}")
        
        print(f"\n🏷️  **Categories:**")
        for category, count in categories_stats.items():
            percentage = (count / products_loaded) * 100
            print(f"   • {category}: {count} products ({percentage:.1f}%)")
        
        print(f"\n💰 **Price Ranges:**")
        for range_name, count in price_ranges.items():
            percentage = (count / products_loaded) * 100
            print(f"   • {range_name.title()}: {count} products ({percentage:.1f}%)")
        
        print(f"\n🗂️  **ChromaDB Collections:**")
        for name, collection in agent.chroma_manager.collections.items():
            try:
                count = collection.count()
                print(f"   • {name}: {count} items")
            except:
                print(f"   • {name}: Error getting count")
        
        print(f"\n🎉 Data loading completed successfully!")
        print(f"📅 Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error importing app: {e}")
        print("Please ensure app.py is in the current directory and dependencies are installed.")
        return False
    
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return False

def extract_colors_from_text(text: str) -> list:
    """Extract color information from product description"""
    colors = []
    text_lower = text.lower()
    
    # Romanian color keywords
    color_mapping = {
        "roșu": ["roșu", "red", "scarlet", "crimson", "burgundy"],
        "alb": ["alb", "white", "ivory", "cream", "alb"],
        "roz": ["roz", "pink", "rose", "pastel"],
        "galben": ["galben", "yellow", "golden", "gold"],
        "violet": ["violet", "purple", "lilac", "lavender", "mov"],
        "albastru": ["albastru", "blue", "navy", "cyan"],
        "portocaliu": ["portocaliu", "orange", "peach"],
        "coral": ["coral", "salmon", "apricot"],
        "verde": ["verde", "green", "eucalyptus"],
        "multicolor": ["mix", "mixed", "multicolor", "various", "colorat"]
    }
    
    for color, keywords in color_mapping.items():
        if any(keyword in text_lower for keyword in keywords):
            colors.append(color)
    
    return colors if colors else ["mixt"]

def extract_occasions_from_text(text: str) -> list:
    """Extract occasion information from product description"""
    occasions = []
    text_lower = text.lower()
    
    occasion_mapping = {
        "romantic": ["romantic", "love", "valentine", "kiss", "iubire", "romantic"],
        "birthday": ["birthday", "celebration", "party", "ziua de naștere", "aniversare"],
        "wedding": ["wedding", "bridal", "bride", "nuntă", "mireasă"],
        "anniversary": ["anniversary", "special", "aniversare"],
        "luxury": ["luxury", "premium", "exclusive", "elegant", "lux", "exclusiv"],
        "sympathy": ["sympathy", "funeral", "memorial", "înmormântare"],
        "thank_you": ["thank", "gratitude", "appreciation", "mulțumire"],
        "spring": ["spring", "fresh", "morning", "primăvară", "proaspăt"],
        "autumn": ["autumn", "fall", "toamnă"],
        "summer": ["summer", "vară", "estival"]
    }
    
    for occasion, keywords in occasion_mapping.items():
        if any(keyword in text_lower for keyword in keywords):
            occasions.append(occasion)
    
    return occasions if occasions else ["general"]

def verify_data_integrity():
    """Verify that data was loaded correctly"""
    try:
        from app import agent
        
        print("\n🔍 Verifying data integrity...")
        
        # Test search functionality
        test_queries = [
            "trandafiri roșii",
            "buchete pentru nuntă", 
            "cutii cu flori",
            "difuzor aromă",
            "bujori"
        ]
        
        for query in test_queries:
            results = agent.chroma_manager.search_products(query, n_results=3)
            print(f"   🔍 '{query}': {len(results)} results found")
            
            if results:
                best_result = results[0]
                similarity = int(best_result['similarity'] * 100)
                print(f"      Best match: {best_result['name']} ({similarity}% similarity)")
        
        print("✅ Data integrity verification completed!")
        return True
        
    except Exception as e:
        print(f"❌ Error during verification: {e}")
        return False

def create_summary_report():
    """Create a summary report of loaded data"""
    try:
        from app import agent
        
        print("\n📋 Creating summary report...")
        
        report = {
            "loading_date": datetime.now().isoformat(),
            "total_products": 0,
            "collections": {},
            "categories": {},
            "price_analysis": {
                "min_price": float('inf'),
                "max_price": 0,
                "avg_price": 0
            }
        }
        
        # Collect statistics from all collections
        total_items = 0
        all_prices = []
        
        for name, collection in agent.chroma_manager.collections.items():
            try:
                count = collection.count()
                report["collections"][name] = count
                total_items += count
            except:
                report["collections"][name] = 0
        
        report["total_products"] = total_items
        
        # Save report
        with open("data_loading_report.json", "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Report saved to: data_loading_report.json")
        return True
        
    except Exception as e:
        print(f"❌ Error creating report: {e}")
        return False

if __name__ == "__main__":
    print("🌸 XOFlowers Data Loader - ChromaDB Edition")
    print("=" * 50)
    
    # Load the data
    success = load_xoflowers_data()
    
    if success:
        # Verify data integrity
        verify_data_integrity()
        
        # Create summary report
        create_summary_report()
        
        print("\n🎉 All done! Your XOFlowers agent is ready with real data.")
        print("🚀 Run: python app.py to start the chatbot server")
        print("🧪 Run: python test_agent.py to test the functionality")
    else:
        print("\n❌ Data loading failed. Please check the errors above.")
        sys.exit(1)
