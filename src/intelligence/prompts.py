"""
Prompts and templates for the XOFlowers AI Agent
Contains all prompts used for intent recognition, responses, and fallback handling
"""

# Intent Recognition Prompts
INTENT_RECOGNITION_PROMPT = """
You are an intelligent assistant for XOFlowers, a premium flower shop. 
Analyze the user's message and determine their intent from these categories:

1. find_product - User wants to search for or get product recommendations (bouquets, gift boxes, plants)
2. ask_question - User asks general questions about the business (hours, location, policies)
3. subscribe - User wants to subscribe to flower plans or receive updates/promotions
4. pay_for_product - User expresses intention to pay for a product

User message: "{message}"

Respond with only the intent category (find_product, ask_question, subscribe, pay_for_product) or "fallback" if unclear.
"""

# Product Search Prompts
PRODUCT_SEARCH_PROMPT = """
Based on the user's request: "{query}"
I found these products that might interest you:

{products}

Would you like more information about any of these products, or would you like me to search for something else?
"""

# FAQ Responses
FAQ_RESPONSES = {
    "working_hours": "🕒 Our working hours:\n• Monday-Friday: 9:00 AM - 8:00 PM\n• Saturday: 10:00 AM - 6:00 PM\n• Sunday: 11:00 AM - 5:00 PM",
    "delivery": "🚚 Delivery Information:\n• Free delivery in Chișinău for orders over 500 MDL\n• Standard delivery fee: 100 MDL\n• Express delivery available for urgent orders",
    "location": "📍 XOFlowers Location:\n• Address: [Your Address Here]\n• Phone: [Your Phone Number]\n• We're located in the heart of Chișinău!",
    "return_policy": "↩️ Return Policy:\n• Fresh flowers can be returned within 24 hours if quality issues\n• Full refund for damaged products\n• Contact us immediately for any concerns"
}

# Subscription Prompts
SUBSCRIPTION_PROMPT = """
🌸 Thank you for your interest in our flower subscription service!

Our subscription options:
• Weekly Fresh Bouquets - 800 MDL/month
• Bi-weekly Premium Arrangements - 1200 MDL/month
• Monthly Luxury Collections - 2000 MDL/month

Each subscription includes:
✅ Hand-picked fresh flowers
✅ Professional arrangement
✅ Free delivery
✅ Flexible scheduling

Would you like to proceed with one of these options?
"""

# Payment Simulation
PAYMENT_SUCCESS_PROMPT = """
💳 Payment successful! 🎉

Your order has been confirmed.
We'll reach out shortly to finalize delivery details.

Thank you for choosing XOFlowers! 🌺
"""

# Fallback Responses
FALLBACK_PROMPT = """
I'm sorry, I didn't quite understand your request. 

I'm here to help you with:
🌸 Finding the perfect flowers and gifts
❓ Answering questions about our services
📱 Subscription plans
💳 Processing orders

For immediate assistance, please contact us:
📞 Phone: [Your Phone Number]
📧 Email: [Your Email]

How can I help you today?
"""

# Jailbreak Protection
JAILBREAK_RESPONSE = """
I'm here to help with XOFlowers only! 🌸

How can I assist you with our flowers, gifts, or services today?
"""

# Censorship Keywords (basic list)
CENSORSHIP_KEYWORDS = [
    "offensive_word1",
    "offensive_word2",
    # Add more keywords as needed
]

CENSORSHIP_RESPONSE = """
I'm sorry, but I can't respond to that type of message. 

I'm here to help you with XOFlowers products and services! 🌸

How can I assist you today?
"""
