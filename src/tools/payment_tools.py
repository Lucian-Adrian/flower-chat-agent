import uuid
from datetime import datetime
from typing import Dict, Any
import json
import os

class PaymentTools:
    def __init__(self, cart_tools):
        self.cart_tools = cart_tools
        self.orders_file = "data/orders.json"
        self.orders = self._load_orders()
    
    def _load_orders(self) -> dict:
        if os.path.exists(self.orders_file):
            with open(self.orders_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _save_orders(self):
        os.makedirs(os.path.dirname(self.orders_file), exist_ok=True)
        with open(self.orders_file, 'w', encoding='utf-8') as f:
            json.dump(self.orders, f, ensure_ascii=False, indent=2)

    def process_payment(self, user_id: str, customer_name: str = "", customer_phone: str = "") -> str:
        if user_id not in self.cart_tools.carts or not self.cart_tools.carts[user_id]:
            return "❌ Nu poți finaliza comanda cu cartul gol. Adaugă produse mai întâi!"
        cart_items = self.cart_tools.carts[user_id]
        total = sum(item['price'] * item['quantity'] for item in cart_items)
        order_id = f"XOF_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6].upper()}"
        transaction_id = f"TXN_{uuid.uuid4().hex[:8].upper()}"
        order = {
            'order_id': order_id,
            'transaction_id': transaction_id,
            'user_id': user_id,
            'items': cart_items.copy(),
            'total_amount': total,
            'currency': 'MDL',
            'customer_name': customer_name,
            'customer_phone': customer_phone,
            'status': 'confirmed',
            'created_at': datetime.now().isoformat(),
            'payment_method': 'dummy_simulation'
        }
        self.orders[order_id] = order
        self._save_orders()
        self.cart_tools.clear_cart(user_id)
        response = f"""✅ **Plata procesată cu succes!**\n\n🛒 **Comanda #{order_id}**\n💰 **Total: {total} MDL**\n🆔 **ID Tranzacție: {transaction_id}**\n\n📦 **Produse comandate:**\n"""
        for item in cart_items:
            response += f"• {item['name']} × {item['quantity']} - {item['price'] * item['quantity']} MDL\n"
        response += f"""\n📞 **Urmează să vă contactăm pentru:**\n• Confirmarea detaliilor de livrare\n• Stabilirea orei de livrare\n• Finalizarea comenzii\n\n🌹 **Mulțumim că alegeți XOFlowers!**\n⏱️ **Timp de procesare: 1-2 ore**"""
        return response

    def get_order_status(self, order_id: str) -> str:
        if order_id not in self.orders:
            return f"❌ Comanda {order_id} nu a fost găsită."
        order = self.orders[order_id]
        return f"""📦 **Status Comandă #{order_id}**\n\n📊 **Status:** {order['status'].title()}\n💰 **Total:** {order['total_amount']} MDL\n📅 **Data:** {order['created_at'][:10]}\n🆔 **Tranzacție:** {order['transaction_id']}\n\n📞 Pentru întrebări: +373 XXX XXX"""
