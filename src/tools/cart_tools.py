from dataclasses import dataclass
from typing import List, Optional
import json
import os

@dataclass
class CartItem:
    product_id: str
    name: str
    price: float
    quantity: int = 1
    url: str = ""

class CartTools:
    def __init__(self):
        self.carts_file = "data/user_carts.json"
        self.carts = self._load_carts()
    
    def _load_carts(self) -> dict:
        if os.path.exists(self.carts_file):
            with open(self.carts_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_carts(self):
        os.makedirs(os.path.dirname(self.carts_file), exist_ok=True)
        with open(self.carts_file, 'w', encoding='utf-8') as f:
            json.dump(self.carts, f, ensure_ascii=False, indent=2)

    def add_to_cart(self, user_id: str, product_name: str, price: float, product_url: str = "") -> str:
        if user_id not in self.carts:
            self.carts[user_id] = []
        for item in self.carts[user_id]:
            if item['name'] == product_name:
                item['quantity'] += 1
                self._save_carts()
                return f"🌸 {product_name} (cantitatea actualizată la {item['quantity']}) - {price} MDL"
        new_item = {
            'product_id': f"prod_{len(self.carts[user_id]) + 1}",
            'name': product_name,
            'price': price,
            'quantity': 1,
            'url': product_url
        }
        self.carts[user_id].append(new_item)
        self._save_carts()
        return f"✅ {product_name} adăugat în cart - {price} MDL"

    def view_cart(self, user_id: str) -> str:
        if user_id not in self.carts or not self.carts[user_id]:
            return "🛒 Cartul tău este gol.\n🌹 Caută produse cu: 'Arată-mi buchete' sau 'Vreau flori pentru...'"
        cart_items = self.carts[user_id]
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        cart_text = "🛒 **Cartul tău:**\n\n"
        for item in cart_items:
            cart_text += f"• {item['name']} × {item['quantity']} - {item['price'] * item['quantity']} MDL\n"
        cart_text += f"\n💰 **Total: {total} MDL**\n"
        cart_text += "📝 Pentru finalizare: 'Vreau să plătesc'"
        return cart_text

    def clear_cart(self, user_id: str) -> str:
        if user_id in self.carts:
            self.carts[user_id] = []
            self._save_carts()
        return "🗑️ Cartul a fost golit cu succes!"

    def remove_from_cart(self, user_id: str, product_name: str) -> str:
        if user_id not in self.carts:
            return "🛒 Cartul tău este gol."
        cart_items = self.carts[user_id]
        for i, item in enumerate(cart_items):
            if item['name'].lower() == product_name.lower():
                removed_item = cart_items.pop(i)
                self._save_carts()
                return f"❌ {removed_item['name']} eliminat din cart"
        return f"❌ Produsul '{product_name}' nu a fost găsit în cart"
