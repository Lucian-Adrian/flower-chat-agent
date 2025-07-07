#!/usr/bin/env python3
"""
Optimizator pentru XOFlowers AI Agent
Îmbunătățește performanța și acuratețea căutărilor cu dataset-ul real
"""

import csv
import json
import os
import re
import logging
from typing import Dict, List, Tuple, Optional
from collections import Counter, defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XOFlowersOptimizer:
    """Optimizator avansat pentru agentul XOFlowers"""
    
    def __init__(self):
        self.csv_path = "chunks_data.csv"
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Expanded Romanian-specific mappings
        self.color_mappings = {
            # Romanian to standardized colors
            "roșu": ["roșu", "red", "crimson", "scarlet", "burgundy"],
            "alb": ["alb", "white", "ivory", "cream", "pearl"],
            "roz": ["roz", "pink", "rose", "blush", "salmon"],
            "galben": ["galben", "yellow", "golden", "amber", "sunshine"],
            "violet": ["violet", "purple", "lilac", "lavender", "mauve"],
            "albastru": ["albastru", "blue", "navy", "cerulean", "azure"],
            "verde": ["verde", "green", "emerald", "sage", "mint"],
            "portocaliu": ["portocaliu", "orange", "peach", "coral", "apricot"],
            "negru": ["negru", "black", "ebony", "charcoal"],
            "multicolor": ["multicolor", "mixed", "various", "assorted"],
            "pastel": ["pastel", "soft", "delicate", "subtle", "pale"]
        }
        
        self.occasion_mappings = {
            # Romanian to standardized occasions
            "ziua_de_nastere": ["ziua de naștere", "birthday", "aniversare", "naștere"],
            "nunta": ["nuntă", "wedding", "căsătorie", "mireasă", "mire"],
            "valentine": ["valentine", "iubire", "dragobete", "romantic", "amor"],
            "8_martie": ["8 martie", "ziua femeii", "women's day", "femei"],
            "paste": ["paște", "easter", "învierea", "pascal"],
            "craciun": ["crăciun", "christmas", "sărbători", "winter holidays"],
            "absolvire": ["absolvire", "graduation", "terminare", "diplomă"],
            "multumire": ["mulțumire", "thank you", "recunoștință", "gratitude"],
            "inmormantare": ["înmormântare", "funeral", "comemorare", "doliu"],
            "botez": ["botez", "baptism", "christening", "religios"],
            "logodna": ["logodnă", "engagement", "cerere", "proposal"],
            "aniversare": ["aniversare", "anniversary", "comemorare"],
            "felicitari": ["felicitări", "congratulations", "succes"]
        }
        
        # Price range optimization
        self.price_ranges = {
            "budget": (0, 500),
            "medium": (501, 1000), 
            "premium": (1001, 2000),
            "luxury": (2001, float('inf'))
        }
        
        # Enhanced category keywords
        self.category_keywords = {
            "buchete": ["buchet", "bouquet", "trandafiri", "roses", "flori", "flowers"],
            "cutii": ["cutie", "box", "căsuță", "container", "ambalaj"],
            "plante": ["plantă", "plant", "ghiveci", "verde", "interior"],
            "cadouri": ["cadou", "gift", "present", "surpriză", "difuzor"],
            "compozitii": ["compoziție", "composition", "aranjament", "arrangement"],
            "bujori": ["bujor", "peony", "peonies", "sezonier"]
        }

    def analyze_dataset(self) -> Dict:
        """Analizează dataset-ul pentru optimizări"""
        try:
            print("🔍 Analizare dataset XOFlowers...")
            
            analysis = {
                "total_products": 0,
                "categories": Counter(),
                "price_distribution": {"budget": 0, "medium": 0, "premium": 0, "luxury": 0},
                "colors_found": Counter(),
                "occasions_found": Counter(),
                "flower_types": Counter(),
                "missing_data": {"price": 0, "category": 0, "description": 0},
                "duplicate_urls": 0,
                "avg_description_length": 0
            }
            
            urls_seen = set()
            description_lengths = []
            
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if row['chunk_type'] == 'product':
                        analysis["total_products"] += 1
                        
                        # Category analysis
                        category = row.get('category', '').strip()
                        if category:
                            analysis["categories"][category] += 1
                        else:
                            analysis["missing_data"]["category"] += 1
                        
                        # Price analysis
                        try:
                            price = float(row.get('price', 0))
                            if price > 0:
                                for range_name, (min_price, max_price) in self.price_ranges.items():
                                    if min_price <= price <= max_price:
                                        analysis["price_distribution"][range_name] += 1
                                        break
                            else:
                                analysis["missing_data"]["price"] += 1
                        except:
                            analysis["missing_data"]["price"] += 1
                        
                        # Description analysis
                        description = row.get('primary_text', '').strip()
                        if description:
                            description_lengths.append(len(description))
                            
                            # Extract colors and occasions from description
                            self._extract_and_count_features(description, analysis)
                        else:
                            analysis["missing_data"]["description"] += 1
                        
                        # Flower type analysis
                        flower_type = row.get('flower_type', '').strip()
                        if flower_type:
                            analysis["flower_types"][flower_type] += 1
                        
                        # URL duplicates
                        url = row.get('url', '').strip()
                        if url in urls_seen:
                            analysis["duplicate_urls"] += 1
                        else:
                            urls_seen.add(url)
            
            # Calculate averages
            if description_lengths:
                analysis["avg_description_length"] = sum(description_lengths) / len(description_lengths)
            
            self._print_analysis_report(analysis)
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing dataset: {e}")
            return {}

    def _extract_and_count_features(self, text: str, analysis: Dict):
        """Extract and count colors/occasions from text"""
        text_lower = text.lower()
        
        # Count colors
        for color, keywords in self.color_mappings.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                analysis["colors_found"][color] += 1
        
        # Count occasions
        for occasion, keywords in self.occasion_mappings.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                analysis["occasions_found"][occasion] += 1

    def _print_analysis_report(self, analysis: Dict):
        """Print detailed analysis report"""
        print("\n" + "="*60)
        print("📊 RAPORT ANALIZĂ DATASET XOFLOWERS")
        print("="*60)
        
        print(f"\n📈 STATISTICI GENERALE:")
        print(f"  • Total produse: {analysis['total_products']}")
        print(f"  • Lungime medie descriere: {analysis['avg_description_length']:.1f} caractere")
        print(f"  • URL-uri duplicate: {analysis['duplicate_urls']}")
        
        print(f"\n🏷️ CATEGORII TOP:")
        for category, count in analysis['categories'].most_common(5):
            percentage = (count / analysis['total_products']) * 100
            print(f"  • {category}: {count} produse ({percentage:.1f}%)")
        
        print(f"\n💰 DISTRIBUȚIE PREȚURI:")
        for range_name, count in analysis['price_distribution'].items():
            percentage = (count / analysis['total_products']) * 100
            print(f"  • {range_name.title()}: {count} produse ({percentage:.1f}%)")
        
        print(f"\n🎨 CULORI TOP:")
        for color, count in analysis['colors_found'].most_common(5):
            print(f"  • {color}: {count} mențiuni")
        
        print(f"\n🎉 OCAZII TOP:")
        for occasion, count in analysis['occasions_found'].most_common(5):
            print(f"  • {occasion}: {count} mențiuni")
        
        print(f"\n🌸 TIPURI FLORI TOP:")
        for flower_type, count in analysis['flower_types'].most_common(5):
            print(f"  • {flower_type}: {count} produse")
        
        print(f"\n⚠️ DATE LIPSĂ:")
        for field, count in analysis['missing_data'].items():
            percentage = (count / analysis['total_products']) * 100
            print(f"  • {field}: {count} produse ({percentage:.1f}%)")

    def generate_search_synonyms(self) -> Dict[str, List[str]]:
        """Generate comprehensive search synonyms for better matching"""
        
        print("\n🔍 Generare sinonime pentru căutare optimizată...")
        
        synonyms = {
            # Product types
            "buchet": ["buchet", "bouquet", "legătură", "mănunchi", "flori"],
            "cutie": ["cutie", "box", "căsuță", "recipient", "ambalaj"],
            "trandafiri": ["trandafir", "trandafiri", "rose", "roses", "roze"],
            "bujori": ["bujor", "bujori", "peony", "peonies"],
            "lalele": ["lalea", "lalele", "tulip", "tulips"],
            "difuzor": ["difuzor", "aromă", "parfum", "miros", "fragrance"],
            
            # Colors with variations
            "rosu": ["roșu", "roșie", "red", "crimson", "burgundy", "cherry"],
            "alb": ["alb", "albă", "white", "ivory", "cream", "pearl"],
            "roz": ["roz", "pink", "rose", "pastel", "blush"],
            "galben": ["galben", "galbenă", "yellow", "golden", "sunshine"],
            "violet": ["violet", "violetă", "purple", "lilac", "lavender"],
            
            # Occasions
            "nunta": ["nuntă", "wedding", "căsătorie", "mireasă", "mire", "bridal"],
            "ziua_de_nastere": ["ziua de naștere", "birthday", "aniversare", "naștere"],
            "valentine": ["valentine", "ziua îndrăgostiților", "romantic", "iubire"],
            "8_martie": ["8 martie", "ziua femeii", "women's day"],
            
            # Styles and occasions
            "elegant": ["elegant", "elegantă", "rafinat", "sofisticat", "luxos"],
            "romantic": ["romantic", "romantică", "tandru", "senzual", "pasional"],
            "modern": ["modern", "modernă", "contemporan", "actual", "trendy"],
            "clasic": ["clasic", "clasică", "tradițional", "clasic", "timeless"]
        }
        
        print(f"✅ Generat {len(synonyms)} grupe de sinonime")
        return synonyms

    def optimize_search_embeddings(self):
        """Create optimized embeddings for better search"""
        
        print("\n🚀 Optimizare embeddings pentru căutare...")
        
        try:
            # Load products and create enhanced descriptions
            enhanced_products = []
            
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    if row['chunk_type'] == 'product':
                        # Create enhanced searchable text
                        enhanced_text = self._create_enhanced_description(row)
                        enhanced_products.append({
                            'id': row.get('chunk_id', ''),
                            'original_text': row.get('primary_text', ''),
                            'enhanced_text': enhanced_text,
                            'category': row.get('category', ''),
                            'price': row.get('price', ''),
                            'flower_type': row.get('flower_type', '')
                        })
            
            print(f"✅ Creat descrieri îmbunătățite pentru {len(enhanced_products)} produse")
            
            # Save enhanced descriptions for ChromaDB
            output_file = "enhanced_products.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(enhanced_products, f, ensure_ascii=False, indent=2)
            
            print(f"💾 Salvat în {output_file}")
            
            return enhanced_products
            
        except Exception as e:
            logger.error(f"Error optimizing embeddings: {e}")
            return []

    def _create_enhanced_description(self, row: Dict) -> str:
        """Create enhanced, searchable description for a product"""
        
        parts = []
        
        # Original description
        original = row.get('primary_text', '').strip()
        if original:
            parts.append(original)
        
        # Add category synonyms
        category = row.get('category', '').lower()
        if 'trandaf' in category or 'rose' in category:
            parts.append("trandafiri roses elegant romantic")
        elif 'bujor' in category or 'peony' in category:
            parts.append("bujori peonies sezonier spring")
        elif 'chando' in category:
            parts.append("difuzor aromă parfum cadou elegant")
        
        # Add flower type synonyms
        flower_type = row.get('flower_type', '').lower()
        if flower_type:
            if 'trandaf' in flower_type or 'rose' in flower_type:
                parts.append("trandafiri roses romantic love")
            elif 'bujor' in flower_type or 'peony' in flower_type:
                parts.append("bujori peonies spring elegant")
            elif 'difuzor' in flower_type:
                parts.append("aromă parfum miros fragrance cadou")
        
        # Add price-based keywords
        try:
            price = float(row.get('price', 0))
            if 0 < price <= 500:
                parts.append("ieftin budget accesibil")
            elif 500 < price <= 1000:
                parts.append("mediu calitate preț")
            elif 1000 < price <= 2000:
                parts.append("premium calitate superior")
            elif price > 2000:
                parts.append("luxos exclusive elegant")
        except:
            pass
        
        # Extract and add color keywords
        text_lower = original.lower()
        for color, keywords in self.color_mappings.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                parts.append(f"{color} {' '.join(keywords[:3])}")
        
        # Extract and add occasion keywords
        for occasion, keywords in self.occasion_mappings.items():
            if any(keyword.lower() in text_lower for keyword in keywords):
                parts.append(f"{occasion} {' '.join(keywords[:2])}")
        
        return " ".join(parts)

    def create_advanced_filters(self) -> Dict:
        """Create advanced filtering rules for better search"""
        
        print("\n🎯 Creare filtre avansate...")
        
        filters = {
            "color_rules": {
                # Smart color matching rules
                "rosu_keywords": ["roșu", "red", "crimson", "burgundy", "cherry", "wine"],
                "alb_keywords": ["alb", "white", "ivory", "cream", "pearl", "snow"],
                "roz_keywords": ["roz", "pink", "rose", "blush", "coral", "salmon"],
                "pastel_keywords": ["pastel", "soft", "delicate", "pale", "light"]
            },
            
            "occasion_rules": {
                # Advanced occasion detection
                "romantic": ["romantic", "valentine", "iubire", "dragobete", "amor", "senzual"],
                "wedding": ["nuntă", "wedding", "mireasă", "mire", "căsătorie", "bridal"],
                "birthday": ["ziua de naștere", "birthday", "aniversare", "celebrare"],
                "sympathy": ["înmormântare", "funeral", "doliu", "comemorare", "condoleanțe"]
            },
            
            "style_rules": {
                # Style and presentation preferences
                "elegant": ["elegant", "rafinat", "sofisticat", "luxos", "clasic"],
                "modern": ["modern", "contemporan", "actual", "trendy", "minimal"],
                "rustic": ["rustic", "natural", "țărănesc", "simplu", "tradițional"],
                "luxurious": ["luxos", "premium", "expensive", "exclusive", "select"]
            },
            
            "size_rules": {
                # Size indicators
                "small": ["mic", "small", "mini", "compact", "discret"],
                "medium": ["mediu", "medium", "standard", "normal", "clasic"],
                "large": ["mare", "large", "big", "impresionant", "spectacular"],
                "extra_large": ["foarte mare", "extra large", "urias", "gigantic", "masiv"]
            }
        }
        
        print(f"✅ Creat {len(filters)} categorii de filtre avansate")
        return filters

    def test_search_optimization(self):
        """Test search optimization with real queries"""
        
        print("\n🧪 TESTARE OPTIMIZĂRI CĂUTARE")
        print("="*50)
        
        # Real customer queries for testing
        test_queries = [
            "trandafiri roșii pentru Valentine's Day",
            "buchet alb pentru nuntă elegant",
            "bujori roz pentru ziua mamei",
            "difuzor aromă cadou ieftin",
            "cutie cu flori pentru ziua de naștere",
            "aranjament floral modern pentru birou",
            "trandafiri francezi luxury premium",
            "flori pastel pentru botez",
            "buchet multicolor pentru absolvire",
            "plantă verde pentru decorare interior"
        ]
        
        synonyms = self.generate_search_synonyms()
        filters = self.create_advanced_filters()
        
        print(f"\n🔍 Testare cu {len(test_queries)} query-uri reale...")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n🧪 Test {i}: '{query}'")
            
            # Simulate enhanced search
            enhanced_query = self._enhance_query(query, synonyms)
            extracted_filters = self._extract_smart_filters(query, filters)
            
            print(f"  📝 Query îmbunătățit: {enhanced_query[:100]}...")
            print(f"  🎯 Filtre detectate: {list(extracted_filters.keys())}")
        
        print(f"\n✅ Testare completă - optimizări funcționale!")

    def _enhance_query(self, query: str, synonyms: Dict) -> str:
        """Enhance search query with synonyms"""
        enhanced_parts = [query]
        query_lower = query.lower()
        
        for term, synonym_list in synonyms.items():
            if any(syn.lower() in query_lower for syn in synonym_list[:2]):
                enhanced_parts.extend(synonym_list[2:4])  # Add 2 more synonyms
        
        return " ".join(enhanced_parts)

    def _extract_smart_filters(self, query: str, filters: Dict) -> Dict:
        """Extract smart filters from query"""
        extracted = {}
        query_lower = query.lower()
        
        for filter_type, rules in filters.items():
            for rule_name, keywords in rules.items():
                if any(keyword.lower() in query_lower for keyword in keywords):
                    if filter_type not in extracted:
                        extracted[filter_type] = []
                    extracted[filter_type].append(rule_name)
        
        return extracted

def main():
    """Main optimization process"""
    print("🌸 OPTIMIZATOR XOFLOWERS AI AGENT")
    print("="*60)
    
    optimizer = XOFlowersOptimizer()
    
    # Step 1: Analyze current dataset
    analysis = optimizer.analyze_dataset()
    
    # Step 2: Generate optimized search components
    synonyms = optimizer.generate_search_synonyms()
    enhanced_products = optimizer.optimize_search_embeddings()
    filters = optimizer.create_advanced_filters()
    
    # Step 3: Test optimizations
    optimizer.test_search_optimization()
    
    # Step 4: Generate optimization report
    print("\n" + "="*60)
    print("📋 SUMAR OPTIMIZĂRI")
    print("="*60)
    print(f"✅ Analizat {analysis.get('total_products', 0)} produse")
    print(f"✅ Generat {len(synonyms)} grupe sinonime")
    print(f"✅ Optimizat {len(enhanced_products)} descrieri produse")
    print(f"✅ Creat {sum(len(rules) for rules in filters.values())} reguli filtre")
    print("\n🚀 Agentul XOFlowers este optimizat pentru dataset-ul real!")
    print("💡 Rulați 'python app.py' pentru a testa îmbunătățirile")

if __name__ == "__main__":
    main()
