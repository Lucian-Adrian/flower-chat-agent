from typing import List, Dict
import os
import argparse
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent / "src/database"))
from src.database.manager import DatabaseManager

PRODUCTS_CSV = os.path.join("src", "database", "products.csv")
COLLECTION_NAME = 'products'

def load_products_from_csv(csv_path: str) -> List[Dict]:
    products = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                price = float(row.get('price', 0))
            except Exception:
                price = 0.0
            product = {
                'id': row.get('id', row.get('product_id', '')),
                'name': row.get('name', ''),
                'description': row.get('description', row.get('full_description', '')),
                'price': price,
                'category': row.get('category', ''),
                'url': row.get('url', ''),
                'metadata': {k: v for k, v in row.items() if k not in ['id','name','description','price','category','url']}
            }
            products.append(product)
    return products

def index_products_to_chromadb():
    print(f"🔄 Indexing products from {PRODUCTS_CSV} into ChromaDB...")
    db = DatabaseManager()
    products = load_products_from_csv(PRODUCTS_CSV)
    docs = []
    for prod in products:
        docs.append({
            'id': prod['id'],
            'text': f"{prod['name']} {prod['description']} {prod['category']}",
            'metadata': {
                'price': prod['price'],
                'category': prod['category'],
                'url': prod['url'],
                **prod['metadata']
            }
        })
    db.add_documents(COLLECTION_NAME, docs)
    print(f"✅ Indexed {len(docs)} products into ChromaDB collection '{COLLECTION_NAME}'")

def search_products_chromadb(query: str, n_results: int = 5):
    db = DatabaseManager()
    results = db.search_documents(COLLECTION_NAME, query, n_results)
    print(f"\n🔍 Search results for: '{query}'")
    for i, res in enumerate(results):
        print(f"{i+1}. {res['text']}")
        print(f"   Category: {res['metadata'].get('category','')}, Price: {res['metadata'].get('price','')} MDL")
        print(f"   URL: {res['metadata'].get('url','')}")
        print(f"   Distance: {res.get('distance')}")
# test_cart_payment_with_real_data.py

import asyncio
import json
import os
import sys
import time
import random
import csv
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime, timedelta

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from tools.cart_tools import CartTools
from tools.payment_tools import PaymentTools

class CSVProductLoader:
    """Load and cache real products from CSV file"""
    
    def __init__(self, csv_path="final_products_case_standardized.csv"):
        self.csv_path = csv_path
        self.products_cache = {}
        self.categories_cache = {}
        self.price_ranges_cache = {}
        self.loaded = False
        
    def load_csv_products(self) -> List[Dict]:
        """Load real products from final_products_case_standardized.csv"""
        print("📂 Loading real products from CSV...")
        
        # Try multiple possible paths
        possible_paths = [
            self.csv_path,
            f"data/{self.csv_path}",
            f"src/database/{self.csv_path}",
            f"database/{self.csv_path}"
        ]
        
        csv_file = None
        for path in possible_paths:
            if os.path.exists(path):
                csv_file = path
                break
        
        if not csv_file:
            print(f"❌ CSV file not found in any of: {possible_paths}")
            return []
        
        products = []
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Only process product entries that exist
                if (row.get('chunk_type') == 'product' and 
                    row.get('product_exists', 'True').lower() == 'true'):
                    
                    # Parse price safely
                    try:
                        price = float(row.get('price', 0))
                    except (ValueError, TypeError):
                        price = 0.0
                    
                    # Extract product name from primary_text
                    primary_text = row.get('primary_text', '')
                    name_parts = primary_text.split(' - ')
                    product_name = name_parts[0].strip() if name_parts else primary_text[:50]
                    
                    product = {
                        'id': row.get('chunk_id', ''),
                        'name': product_name,
                        'full_description': primary_text,
                        'price': price,
                        'category': row.get('category', ''),
                        'flower_type': row.get('flower_type', ''),
                        'url': row.get('url', '')
                    }
                    
                    products.append(product)
        
        print(f"✅ Loaded {len(products)} real products from CSV")
        self.loaded = True
        return products
    
    def cache_products_by_attributes(self, products: List[Dict]):
        """Cache products by category, price range, etc."""
        print("💾 Caching products by attributes...")
        
        # Cache by category
        for product in products:
            category = product['category']
            if category not in self.categories_cache:
                self.categories_cache[category] = []
            self.categories_cache[category].append(product)
        
        # Cache by price ranges
        price_ranges = {
            'budget': (0, 100),      # Sub 100 MDL
            'medium': (100, 300),    # 100-300 MDL  
            'premium': (300, 1000),  # 300-1000 MDL
            'luxury': (1000, 10000)  # Peste 1000 MDL
        }
        
        for range_name, (min_price, max_price) in price_ranges.items():
            self.price_ranges_cache[range_name] = [
                p for p in products 
                if min_price <= p['price'] <= max_price
            ]
        
        # Cache all products for quick access
        for product in products:
            self.products_cache[product['id']] = product
        
        print(f"📊 Cached by categories: {list(self.categories_cache.keys())}")
        print(f"💰 Cached by price ranges: {list(self.price_ranges_cache.keys())}")
    
    def get_random_products(self, count: int = 5) -> List[Dict]:
        """Get random products from cache"""
        if not self.products_cache:
            return []
        
        available_products = list(self.products_cache.values())
        return random.sample(available_products, min(count, len(available_products)))
    
    def get_products_by_category(self, category: str, count: int = 3) -> List[Dict]:
        """Get products from specific category"""
        category_products = self.categories_cache.get(category, [])
        return random.sample(category_products, min(count, len(category_products)))
    
    def get_products_by_price_range(self, range_name: str, count: int = 3) -> List[Dict]:
        """Get products from specific price range"""
        range_products = self.price_ranges_cache.get(range_name, [])
        return random.sample(range_products, min(count, len(range_products)))

class RealDataTestScenarios:
    """Test scenarios using real CSV data"""
    
    def __init__(self, product_loader: CSVProductLoader):
        self.product_loader = product_loader
        self.cart_tools = CartTools()
        self.payment_tools = PaymentTools(self.cart_tools)
        self.performance_stats = {}
    
    def log_performance(self, operation: str, duration: float):
        """Track performance metrics"""
        if operation not in self.performance_stats:
            self.performance_stats[operation] = []
        self.performance_stats[operation].append(duration)
    
    async def test_category_based_shopping(self):
        """Test shopping by real product categories"""
        print("\n🏷️  Testing Category-Based Shopping with Real Data...")
        
        # Get available categories from CSV
        categories = list(self.product_loader.categories_cache.keys())
        print(f"📂 Available categories: {categories}")
        
        for category in categories[:5]:  # Test first 5 categories
            if not self.product_loader.categories_cache[category]:
                continue
                
            print(f"\n🛍️  Testing category: {category}")
            user_id = f"category_test_{category.lower().replace(' ', '_')}_{int(time.time())}"
            
            # Get products from this category
            products = self.product_loader.get_products_by_category(category, 3)
            
            for product in products:
                start_time = time.time()
                result = self.cart_tools.add_to_cart(
                    user_id, 
                    product['name'], 
                    product['price'], 
                    product['url']
                )
                duration = time.time() - start_time
                self.log_performance(f"add_to_cart_{category}", duration)
                
                print(f"   ✅ {result}")
            
            # View cart for this category
            cart_view = self.cart_tools.view_cart(user_id)
            print(f"   🛒 {category} cart overview:")
            print(f"      Items: {len(self.cart_tools.carts.get(user_id, []))}")
            
            # Calculate total
            total = sum(item['price'] * item['quantity'] 
                       for item in self.cart_tools.carts.get(user_id, []))
            print(f"      Total: {total} MDL")
    
    async def test_price_range_scenarios(self):
        """Test shopping by different price ranges"""
        print("\n💰 Testing Price Range Scenarios with Real Data...")
        
        price_scenarios = {
            'budget_conscious': 'budget',      # Sub 100 MDL
            'mid_range_shopper': 'medium',     # 100-300 MDL
            'premium_buyer': 'premium',        # 300-1000 MDL
            'luxury_customer': 'luxury'        # Peste 1000 MDL
        }
        
        for scenario_name, price_range in price_scenarios.items():
            products = self.product_loader.get_products_by_price_range(price_range, 4)
            
            if not products:
                print(f"   ⚠️  No products found for {price_range} range")
                continue
            
            print(f"\n👤 Scenario: {scenario_name} ({price_range} range)")
            user_id = f"{scenario_name}_{int(time.time())}"
            
            total_expected = 0
            for product in products:
                result = self.cart_tools.add_to_cart(
                    user_id,
                    product['name'],
                    product['price'],
                    product['url']
                )
                total_expected += product['price']
                print(f"   💸 {product['name']}: {product['price']} MDL")
            
            cart_view = self.cart_tools.view_cart(user_id)
            print(f"   📊 Total cart value: {total_expected} MDL")
            
            # Test payment for this price range
            if total_expected > 0:
                payment_result = self.payment_tools.process_payment(
                    user_id, 
                    f"Customer {scenario_name}", 
                    "+373 69 123 456"
                )
                print(f"   💳 Payment processed for {total_expected} MDL")
    
    async def test_realistic_flower_shopping(self):
        """Test realistic flower shopping scenarios"""
        print("\n🌹 Testing Realistic Flower Shopping Scenarios...")
        
        # Wedding shopping scenario
        print("\n💍 Wedding Shopping Scenario")
        wedding_user = f"wedding_shopper_{int(time.time())}"
        
        # Look for wedding-related products
        wedding_categories = ["Bride'S Bouquet", "Premium", "Author'S Bouquets"]
        wedding_products = []
        
        for category in wedding_categories:
            if category in self.product_loader.categories_cache:
                wedding_products.extend(
                    self.product_loader.get_products_by_category(category, 2)
                )
        
        for product in wedding_products[:4]:  # Limit to 4 products
            result = self.cart_tools.add_to_cart(
                wedding_user,
                product['name'],
                product['price'],
                product['url']
            )
            print(f"   💐 {result}")
        
        # Valentine's Day scenario
        print("\n💕 Valentine's Day Scenario")
        valentine_user = f"valentine_shopper_{int(time.time())}"
        
        # Look for romantic products
        valentine_categories = ["St. Valentine'S Day", "French Roses", "Premium"]
        valentine_products = []
        
        for category in valentine_categories:
            if category in self.product_loader.categories_cache:
                valentine_products.extend(
                    self.product_loader.get_products_by_category(category, 2)
                )
        
        for product in valentine_products[:3]:
            result = self.cart_tools.add_to_cart(
                valentine_user,
                product['name'],
                product['price'],
                product['url']
            )
            print(f"   💕 {result}")
    
    async def test_bulk_operations_with_real_data(self):
        """Test bulk operations using real product data"""
        print("\n📦 Testing Bulk Operations with Real Data...")
        
        bulk_user = f"bulk_test_{int(time.time())}"
        
        # Get 20 random products for bulk testing
        bulk_products = self.product_loader.get_random_products(20)
        
        print(f"🔄 Adding {len(bulk_products)} real products to cart...")
        
        start_time = time.time()
        for i, product in enumerate(bulk_products):
            add_start = time.time()
            
            result = self.cart_tools.add_to_cart(
                bulk_user,
                product['name'],
                product['price'],
                product['url']
            )
            
            add_duration = time.time() - add_start
            self.log_performance("bulk_add_operation", add_duration)
            
            if i % 5 == 0:  # Progress indicator
                print(f"   📈 Progress: {i+1}/{len(bulk_products)}")
        
        total_time = time.time() - start_time
        self.log_performance("bulk_total_time", total_time)
        
        # Verify bulk cart
        cart_items = self.cart_tools.carts.get(bulk_user, [])
        total_value = sum(item['price'] * item['quantity'] for item in cart_items)
        
        print(f"   ✅ Bulk operation completed in {total_time:.2f}s")
        print(f"   📊 Cart stats: {len(cart_items)} items, {total_value} MDL total")
    
    async def test_cart_management_scenarios(self):
        """Test cart management with real products"""
        print("\n🛒 Testing Cart Management Scenarios...")
        
        cart_user = f"cart_management_{int(time.time())}"
        
        # Add some products
        products = self.product_loader.get_random_products(5)
        
        print("   📝 Adding products to cart...")
        for product in products:
            result = self.cart_tools.add_to_cart(
                cart_user,
                product['name'],
                product['price'],
                product['url']
            )
            print(f"      ✅ {product['name']}")
        
        # Test viewing cart
        print("\n   👀 Viewing cart...")
        cart_view = self.cart_tools.view_cart(cart_user)
        print(f"      🛒 Cart contents displayed")
        
        # Test removing a product
        if products:
            product_to_remove = products[0]['name']
            print(f"\n   ❌ Removing: {product_to_remove}")
            remove_result = self.cart_tools.remove_from_cart(cart_user, product_to_remove)
            print(f"      {remove_result}")
        
        # Test adding duplicate (quantity increment)
        if len(products) > 1:
            duplicate_product = products[1]
            print(f"\n   🔄 Adding duplicate: {duplicate_product['name']}")
            dup_result = self.cart_tools.add_to_cart(
                cart_user,
                duplicate_product['name'],
                duplicate_product['price'],
                duplicate_product['url']
            )
            print(f"      {dup_result}")
        
        # Final cart state
        final_cart = self.cart_tools.view_cart(cart_user)
        print(f"\n   🏁 Final cart state ready")

def print_performance_report(test_scenarios: RealDataTestScenarios):
    """Print comprehensive performance report"""
    print("\n" + "="*60)
    print("📊 PERFORMANCE REPORT - Real Data Testing")
    print("="*60)
    
    stats = test_scenarios.performance_stats
    
    for operation, times in stats.items():
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n🔍 {operation.upper()}:")
            print(f"   Operations: {len(times)}")
            print(f"   Average: {avg_time:.4f}s")
            print(f"   Fastest: {min_time:.4f}s")
            print(f"   Slowest: {max_time:.4f}s")
    
    print(f"\n💾 Cache Statistics:")
    print(f"   Categories cached: {len(test_scenarios.product_loader.categories_cache)}")
    print(f"   Products cached: {len(test_scenarios.product_loader.products_cache)}")
    print(f"   Price ranges: {len(test_scenarios.product_loader.price_ranges_cache)}")

async def main():
    """Main test execution with real CSV data"""
    parser = argparse.ArgumentParser(description="Cart/Payment & ChromaDB test runner")
    parser.add_argument('--index', action='store_true', help='Index all products from products.csv into ChromaDB')
    parser.add_argument('--search', type=str, help='Search query for products in ChromaDB')
    parser.add_argument('--n', type=int, default=5, help='Number of results to return for search')
    args, unknown = parser.parse_known_args()

    if args.index:
        index_products_to_chromadb()
        return
    if args.search:
        search_products_chromadb(args.search, args.n)
        return

    print("🧪 Starting Cart & Payment Tests with Real CSV Data")
    print("=" * 70)
    # ...existing code for product_loader, test_scenarios, etc...
    product_loader = CSVProductLoader()
    products = product_loader.load_csv_products()
    if not products:
        print("❌ No products loaded. Cannot continue testing.")
        return
    product_loader.cache_products_by_attributes(products)
    test_scenarios = RealDataTestScenarios(product_loader)
    await test_scenarios.test_category_based_shopping()
    await test_scenarios.test_price_range_scenarios()
    await test_scenarios.test_realistic_flower_shopping()
    await test_scenarios.test_bulk_operations_with_real_data()
    await test_scenarios.test_cart_management_scenarios()
    print_performance_report(test_scenarios)
    print("\n" + "="*70)
    print("🔍 Final Data Verification")
    data_files = ["data/user_carts.json", "data/orders.json"]
    for file_path in data_files:
        if os.path.exists(file_path):
            file_size = os.path.getsize(file_path)
            print(f"✅ {file_path}: {file_size} bytes")
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    print(f"   📄 Valid JSON with {len(data)} entries")
            except json.JSONDecodeError as e:
                print(f"   ❌ JSON Error: {e}")
        else:
            print(f"❌ Missing: {file_path}")
    print("\n🎉 Real data testing completed successfully!")
    print("📈 All tests used actual XOFlowers product data from CSV")
    print("💰 Performance optimizations through intelligent caching")

if __name__ == "__main__":
    asyncio.run(main())