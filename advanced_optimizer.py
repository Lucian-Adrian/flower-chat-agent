#!/usr/bin/env python3
"""
Advanced XOFlowers Agent Optimizer
Enhanced version for real dataset with 724 products, 15 categories, 316 flower types
Focuses on Romanian market with multilingual support
"""

import csv
import json
import os
import re
import logging
import unicodedata
from typing import Dict, List, Tuple, Optional, Set
from collections import Counter, defaultdict
import numpy as np
from sentence_transformers import SentenceTransformer
import chromadb
from difflib import SequenceMatcher
import pandas as pd

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedXOFlowersOptimizer:
    """Advanced optimizer specifically for XOFlowers dataset"""
    
    def __init__(self):
        self.csv_path = "chunks_data.csv"
        self.model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        
        # Romanian-specific optimizations based on real data analysis
        self.romanian_color_mappings = {
            "roșu": ["roșu", "roșie", "red", "rouge", "красный", "crimson", "burgundy", "cherry"],
            "alb": ["alb", "albă", "white", "blanc", "белый", "ivory", "cream", "pearl", "snow"],
            "roz": ["roz", "pink", "rose", "розовый", "blush", "salmon", "coral", "fuchsia"],
            "galben": ["galben", "galbenă", "yellow", "jaune", "жёлтый", "golden", "amber", "sunshine", "lemon"],
            "violet": ["violet", "violetă", "purple", "violet", "фиолетовый", "lilac", "lavender", "mauve", "plum"],
            "albastru": ["albastru", "albastră", "blue", "bleu", "синий", "navy", "azure", "cerulean", "sapphire"],
            "verde": ["verde", "green", "vert", "зелёный", "emerald", "sage", "mint", "forest", "lime"],
            "portocaliu": ["portocaliu", "orange", "оранжевый", "peach", "apricot", "tangerine", "amber"],
            "negru": ["negru", "neagră", "black", "noir", "чёрный", "ebony", "charcoal", "midnight"],
            "multicolor": ["multicolor", "mixed", "mixte", "разноцветный", "various", "assorted", "rainbow"],
            "pastel": ["pastel", "soft", "delicate", "subtle", "pale", "light", "tender"]
        }
        
        # Enhanced occasion mappings for Romanian market
        self.romanian_occasion_mappings = {
            "ziua_de_nastere": ["ziua de naștere", "birthday", "aniversare", "naștere", "születésnap", "день рождения"],
            "nunta": ["nuntă", "wedding", "căsătorie", "mireasă", "mire", "esküvő", "свадьба", "marriage"],
            "valentine": ["valentine", "ziua îndrăgostiților", "dragobete", "iubire", "amor", "святой валентин"],
            "8_martie": ["8 martie", "ziua femeii", "women's day", "femei", "международный женский день"],
            "paste": ["paște", "easter", "înviere", "пасха", "húsvét"],
            "craciun": ["crăciun", "christmas", "sărbători", "рождество", "karácsony"],
            "ziua_mamei": ["ziua mamei", "mother's day", "mama", "mère", "день матери"],
            "ziua_indragostistilor": ["ziua îndrăgostiților", "valentine's day", "dragobete"],
            "botez": ["botez", "baptism", "christening", "крещение"],
            "absolvire": ["absolvire", "graduation", "diplomă", "выпускной"],
            "doliu": ["doliu", "mourning", "condoleanțe", "памяти", "funeral"],
            "bucurie": ["bucurie", "celebration", "joy", "felicitare", "радость"],
            "multumire": ["mulțumire", "thank you", "appreciation", "благодарность"],
            "scuze": ["scuze", "apology", "sorry", "извинение"],
            "romantic": ["romantic", "romantico", "романтический", "romantikus"]
        }
        
        # Category standardization for XOFlowers
        self.category_mappings = {
            "mono_duo": ["MONO/DUO bouquets", "mono", "duo", "single", "pair"],
            "author": ["Author's bouquets", "designer", "custom", "авторский", "author"],
            "valentine": ["St. Valentine's Day", "valentine", "dragobete", "romantic"],
            "basket": ["Basket / Boxes with flowers", "basket", "box", "container", "коробка"],
            "premium": ["Premium", "luxury", "expensive", "премиум", "lux"],
            "card": ["Greeting card", "card", "message", "note", "открытка"],
            "french": ["French roses", "french", "france", "français", "французский"],
            "peonies": ["Peonies", "peony", "bujor", "пион"],
            "accessories": ["Additional accessories / Vases", "vase", "accessory", "ваза"],
            "bridal": ["Bride's bouquet", "bride", "bridal", "wedding", "невеста"],
            "toys": ["Soft toys", "toy", "teddy", "игрушка"],
            "chando": ["Chando", "diffuser", "aroma", "difuzor"],
            "mourning": ["Mourning flower arrangement", "mourning", "funeral", "doliu"],
            "sweets": ["Sweets", "chocolate", "candy", "сладости"],
            "classic": ["Classic bouquets", "classic", "traditional", "классический"]
        }
        
        # Flower type normalization (based on 316 types found)
        self.flower_type_mappings = {
            "roses": ["roses", "rose", "trandafir", "trandafiri", "роза", "розы"],
            "peonies": ["peonies", "peony", "bujor", "bujori", "пион", "пионы"],
            "hydrangea": ["hydrangea", "hortensia", "hortensie", "гортензия"],
            "gypsophila": ["gypsophila", "baby's breath", "gypsophila paniculata"],
            "eucalyptus": ["eucalyptus", "eucalipt", "эвкалипт"],
            "chrysanthemum": ["chrysanthemum", "crizanteme", "хризантема"],
            "tulips": ["tulips", "tulip", "lalele", "lalea", "тюльпан"],
            "carnations": ["carnations", "carnation", "garoafe", "garoafă", "гвоздика"],
            "orchids": ["orchids", "orchid", "orhidee", "орхидея"],
            "lilies": ["lilies", "lily", "crin", "crini", "лилия"],
            "sunflowers": ["sunflowers", "sunflower", "floarea soarelui", "подсолнух"],
            "gerbera": ["gerbera", "gerbere", "гербера"],
            "alstroemeria": ["alstroemeria", "альстромерия"],
            "diffuser": ["difuzor aromă", "aroma diffuser", "диффузор"]
        }
        
        # Price range categories for better filtering
        self.price_ranges = {
            "budget": (0, 500),
            "mid_range": (500, 1500),
            "premium": (1500, 3000),
            "luxury": (3000, 6000),
            "exclusive": (6000, float('inf'))
        }
        
        # Sentiment and emotion mappings
        self.emotion_mappings = {
            "love": ["love", "iubire", "amor", "любовь", "romantic", "passion"],
            "gratitude": ["thank you", "mulțumesc", "gratitude", "спасибо", "appreciation"],
            "celebration": ["celebration", "sărbătoare", "party", "праздник", "joy"],
            "sympathy": ["sympathy", "condoleanțe", "sorry", "сочувствие", "comfort"],
            "congratulations": ["congratulations", "felicitări", "bravo", "поздравления"],
            "apology": ["apology", "scuze", "sorry", "извинение", "forgiveness"],
            "friendship": ["friendship", "prietenie", "friend", "дружба", "buddy"],
            "admiration": ["admiration", "admirație", "respect", "восхищение"]
        }

    def analyze_dataset_deep(self) -> Dict:
        """Deep analysis of the XOFlowers dataset"""
        logger.info("🔍 Starting deep dataset analysis...")
        
        df = pd.read_csv(self.csv_path)
        
        analysis = {
            "total_products": len(df),
            "categories": {},
            "flower_types": {},
            "price_analysis": {},
            "text_analysis": {},
            "optimization_opportunities": []
        }
        
        # Category analysis
        for category, count in df['category'].value_counts().items():
            analysis["categories"][category] = {
                "count": count,
                "percentage": (count / len(df)) * 100,
                "avg_price": df[df['category'] == category]['price'].astype(float).mean()
            }
        
        # Flower type analysis
        flower_counts = df['flower_type'].value_counts()
        for flower, count in flower_counts.head(20).items():
            analysis["flower_types"][flower] = {
                "count": count,
                "percentage": (count / len(df)) * 100
            }
        
        # Price analysis
        prices = pd.to_numeric(df['price'], errors='coerce')
        analysis["price_analysis"] = {
            "min": float(prices.min()),
            "max": float(prices.max()),
            "mean": float(prices.mean()),
            "median": float(prices.median()),
            "std": float(prices.std()),
            "quartiles": {
                "q1": float(prices.quantile(0.25)),
                "q3": float(prices.quantile(0.75))
            }
        }
        
        # Text analysis for optimization
        all_text = ' '.join(df['primary_text'].astype(str)).lower()
        
        # Romanian flower terms frequency
        romanian_terms = {
            "trandafir": all_text.count("trandafir"),
            "buchet": all_text.count("buchet"),
            "floare": all_text.count("floare"),
            "flori": all_text.count("flori"),
            "romantic": all_text.count("romantic"),
            "elegant": all_text.count("elegant"),
            "frumos": all_text.count("frumos"),
            "cadou": all_text.count("cadou")
        }
        
        analysis["text_analysis"]["romanian_terms"] = romanian_terms
        
        # Color term frequency
        color_freq = {}
        for color, variants in self.romanian_color_mappings.items():
            count = sum(all_text.count(variant.lower()) for variant in variants)
            if count > 0:
                color_freq[color] = count
        
        analysis["text_analysis"]["color_frequency"] = color_freq
        
        # Identify optimization opportunities
        opportunities = []
        
        # Check for inconsistent naming
        if flower_counts.nunique() > 100:
            opportunities.append("Standardize flower type names - too many variants")
        
        # Check for missing color information
        if sum(color_freq.values()) < len(df) * 0.3:
            opportunities.append("Add more color information to product descriptions")
        
        # Check price distribution
        if prices.std() > prices.mean():
            opportunities.append("High price variance - implement better price categorization")
        
        analysis["optimization_opportunities"] = opportunities
        
        return analysis

    def generate_enhanced_synonyms(self) -> Dict:
        """Generate enhanced synonyms based on real dataset analysis"""
        logger.info("📝 Generating enhanced synonyms...")
        
        # Load real data to extract patterns
        df = pd.read_csv(self.csv_path)
        
        synonyms = {
            "categories": {},
            "flowers": {},
            "colors": self.romanian_color_mappings,
            "occasions": self.romanian_occasion_mappings,
            "emotions": self.emotion_mappings,
            "price_ranges": {},
            "descriptors": {}
        }
        
        # Generate category synonyms from real data
        for standard, variants in self.category_mappings.items():
            synonyms["categories"][standard] = variants
        
        # Generate flower synonyms
        for standard, variants in self.flower_type_mappings.items():
            synonyms["flowers"][standard] = variants
        
        # Price range synonyms
        for range_name, (min_price, max_price) in self.price_ranges.items():
            synonyms["price_ranges"][range_name] = {
                "range": [min_price, max_price],
                "terms": self._get_price_range_terms(range_name)
            }
        
        # Common descriptors from product text
        descriptors = {
            "elegant": ["elegant", "elegantă", "refined", "sophisticated", "элегантный"],
            "beautiful": ["frumos", "beautiful", "gorgeous", "stunning", "красивый"],
            "romantic": ["romantic", "romantică", "loving", "tender", "романтический"],
            "luxury": ["luxury", "luxos", "premium", "expensive", "роскошный"],
            "fresh": ["fresh", "proaspăt", "new", "crisp", "свежий"],
            "delicate": ["delicate", "delicat", "gentle", "soft", "нежный"],
            "vibrant": ["vibrant", "viu", "bright", "colorful", "яркий"],
            "classic": ["classic", "clasic", "traditional", "timeless", "классический"]
        }
        
        synonyms["descriptors"] = descriptors
        
        return synonyms

    def _get_price_range_terms(self, range_name: str) -> List[str]:
        """Get terms associated with price ranges"""
        terms_map = {
            "budget": ["ieftin", "budget", "affordable", "cheap", "economic", "дешевый"],
            "mid_range": ["mediu", "moderate", "reasonable", "средний", "normal"],
            "premium": ["premium", "scump", "expensive", "costly", "дорогой"],
            "luxury": ["luxury", "luxos", "exclusive", "роскошный", "elit"],
            "exclusive": ["exclusive", "exclusiv", "unique", "special", "эксклюзивный"]
        }
        return terms_map.get(range_name, [])

    def create_smart_filters(self) -> Dict:
        """Create intelligent filters based on dataset analysis"""
        logger.info("🎯 Creating smart filters...")
        
        df = pd.read_csv(self.csv_path)
        
        filters = {
            "price_based": {},
            "occasion_based": {},
            "flower_based": {},
            "color_based": {},
            "sentiment_based": {}
        }
        
        # Price-based filters
        prices = pd.to_numeric(df['price'], errors='coerce')
        percentiles = [0, 25, 50, 75, 90, 100]
        price_cuts = [prices.quantile(p/100) for p in percentiles]
        
        filters["price_based"] = {
            "very_budget": {"min": 0, "max": price_cuts[1], "label": "Foarte ieftin"},
            "budget": {"min": price_cuts[1], "max": price_cuts[2], "label": "Ieftin"},
            "moderate": {"min": price_cuts[2], "max": price_cuts[3], "label": "Preț moderat"},
            "expensive": {"min": price_cuts[3], "max": price_cuts[4], "label": "Scump"},
            "luxury": {"min": price_cuts[4], "max": float('inf'), "label": "Luxury"}
        }
        
        # Occasion-based filters with real categories
        real_categories = df['category'].unique()
        for category in real_categories:
            clean_name = self._clean_category_name(category)
            filters["occasion_based"][clean_name] = {
                "original": category,
                "products": len(df[df['category'] == category]),
                "avg_price": float(df[df['category'] == category]['price'].astype(float).mean())
            }
        
        # Flower-based filters
        flower_types = df['flower_type'].value_counts()
        for flower, count in flower_types.head(15).items():
            clean_flower = self._clean_flower_name(flower)
            filters["flower_based"][clean_flower] = {
                "original": flower,
                "count": count,
                "percentage": (count / len(df)) * 100
            }
        
        return filters

    def _clean_category_name(self, category: str) -> str:
        """Clean category name for use as filter key"""
        # Remove special characters and convert to lowercase
        clean = re.sub(r'[^\w\s]', '', category.lower())
        clean = re.sub(r'\s+', '_', clean.strip())
        return clean

    def _clean_flower_name(self, flower: str) -> str:
        """Clean flower name for use as filter key"""
        clean = re.sub(r'[^\w\s]', '', flower.lower())
        clean = re.sub(r'\s+', '_', clean.strip())
        return clean

    def optimize_search_embeddings(self) -> Dict:
        """Optimize search embeddings for better multilingual matching"""
        logger.info("🚀 Optimizing search embeddings...")
        
        df = pd.read_csv(self.csv_path)
        
        # Create enhanced text for embeddings
        enhanced_texts = []
        for _, row in df.iterrows():
            enhanced = self._enhance_product_text(row)
            enhanced_texts.append(enhanced)
        
        # Generate embeddings
        embeddings = self.model.encode(enhanced_texts)
        
        optimization_results = {
            "embedding_dimension": embeddings.shape[1],
            "total_products": len(enhanced_texts),
            "enhancement_stats": {
                "avg_text_length": np.mean([len(text) for text in enhanced_texts]),
                "enhanced_terms_added": self._count_enhanced_terms(enhanced_texts)
            }
        }
        
        return optimization_results

    def _enhance_product_text(self, row: pd.Series) -> str:
        """Enhance product text with synonyms and translations"""
        original_text = str(row['primary_text'])
        enhanced = original_text
        
        # Add category synonyms
        category = str(row['category'])
        for standard, variants in self.category_mappings.items():
            if category in variants:
                enhanced += f" {' '.join(variants[:3])}"
                break
        
        # Add flower type synonyms
        flower_type = str(row['flower_type'])
        for standard, variants in self.flower_type_mappings.items():
            if any(variant.lower() in flower_type.lower() for variant in variants):
                enhanced += f" {' '.join(variants[:3])}"
                break
        
        # Add price range terms
        try:
            price = float(row['price'])
            for range_name, (min_p, max_p) in self.price_ranges.items():
                if min_p <= price < max_p:
                    range_terms = self._get_price_range_terms(range_name)
                    enhanced += f" {' '.join(range_terms[:2])}"
                    break
        except:
            pass
        
        return enhanced

    def _count_enhanced_terms(self, enhanced_texts: List[str]) -> int:
        """Count how many enhancement terms were added"""
        total_enhanced = 0
        for text in enhanced_texts:
            # Count terms that are likely enhancements (simple heuristic)
            words = text.split()
            # Assume enhancement terms are at the end and are shorter/more generic
            if len(words) > 20:  # If text is long, last few words might be enhancements
                total_enhanced += min(5, len(words) - 20)
        return total_enhanced

    def generate_optimization_report(self) -> Dict:
        """Generate comprehensive optimization report"""
        logger.info("📊 Generating optimization report...")
        
        report = {
            "timestamp": pd.Timestamp.now().isoformat(),
            "dataset_analysis": self.analyze_dataset_deep(),
            "synonyms": self.generate_enhanced_synonyms(),
            "smart_filters": self.create_smart_filters(),
            "embedding_optimization": self.optimize_search_embeddings(),
            "recommendations": self._generate_recommendations()
        }
        
        return report

    def _generate_recommendations(self) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = [
            "Implement fuzzy matching for flower type queries (316 types need standardization)",
            "Add Romanian-specific color detection with expanded synonym mapping",
            "Create price-based smart filters for better user experience (price range: 10-11,500 MDL)",
            "Enhance multilingual support with automatic language detection",
            "Implement category-specific search boosting for popular categories",
            "Add sentiment analysis for occasion-based recommendations",
            "Create unified flower type taxonomy to reduce 316 variants",
            "Implement seasonal and trending product highlighting",
            "Add smart suggestions based on price range and category correlations",
            "Enhance search with Romanian grammatical form matching (roșu/roșie/roșii)"
        ]
        
        return recommendations

    def export_optimizations(self, output_dir: str = "."):
        """Export all optimization data"""
        logger.info("💾 Exporting optimization data...")
        
        # Generate full report
        report = self.generate_optimization_report()
        
        # Save main report
        with open(os.path.join(output_dir, "xoflowers_optimization_report.json"), 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Save individual components
        components = {
            "synonyms_enhanced.json": report["synonyms"],
            "smart_filters.json": report["smart_filters"],
            "dataset_analysis.json": report["dataset_analysis"]
        }
        
        for filename, data in components.items():
            with open(os.path.join(output_dir, filename), 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        logger.info("✅ Optimization data exported successfully!")
        
        return {
            "files_created": list(components.keys()) + ["xoflowers_optimization_report.json"],
            "output_directory": output_dir
        }

def main():
    """Main optimization function"""
    print("🚀 XOFlowers Advanced Optimizer")
    print("="*50)
    
    optimizer = AdvancedXOFlowersOptimizer()
    
    try:
        # Export all optimizations
        result = optimizer.export_optimizations()
        
        print("\n✅ Optimization Complete!")
        print(f"📁 Files created: {len(result['files_created'])}")
        for file in result['files_created']:
            print(f"   📄 {file}")
        
        print(f"\n📍 Location: {result['output_directory']}")
        
        # Display key insights
        analysis = optimizer.analyze_dataset_deep()
        print(f"\n📊 Key Insights:")
        print(f"   🌸 Total products: {analysis['total_products']}")
        print(f"   📂 Categories: {len(analysis['categories'])}")
        print(f"   🌺 Flower types: {len(analysis['flower_types'])}")
        print(f"   💰 Price range: {analysis['price_analysis']['min']:.0f} - {analysis['price_analysis']['max']:.0f} MDL")
        
        print(f"\n🎯 Top recommendations:")
        recommendations = optimizer._generate_recommendations()
        for i, rec in enumerate(recommendations[:5], 1):
            print(f"   {i}. {rec}")
        
    except Exception as e:
        logger.error(f"❌ Optimization failed: {e}")
        raise

if __name__ == "__main__":
    main()
