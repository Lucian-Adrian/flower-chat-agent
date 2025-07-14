# 🔄 System Flow Documentation

## 📋 **OVERVIEW**

This document describes the complete flow of how the XOFlowers AI Agent processes messages and interactions from users across different platforms (Instagram, Telegram).

## 🌊 **MESSAGE PROCESSING FLOW**

### **1. Message Reception**

```
User Message → Platform API → Our Application
```

#### **Instagram Flow**
```
Instagram DM → Meta Graph API → Webhook → instagram_app.py
```

#### **Telegram Flow**
```
Telegram Message → Telegram Bot API → Polling → telegram_app.py
```

### **2. Security Layer**

```
Raw Message → Security Filters → Validated Message
```

**Security Checks (`src/security/filters.py`):**
- ✅ Content filtering (offensive language, spam)
- ✅ Rate limiting (max messages per minute)
- ✅ Anti-jailbreak protection
- ✅ Message length validation
- ✅ User verification

### **3. Intent Classification**

```
Validated Message → AI Analysis → Intent Classification
```

**Intent Types (`src/intelligence/intent_classifier.py`):**
- 🔍 **find_product** - Product search and recommendations
- ❓ **ask_question** - General business inquiries
- 📧 **subscribe** - Newsletter/updates subscription
- 💳 **pay_for_product** - Payment processing intents

### **4. Action Processing**

```
Classified Intent → Action Handler → Business Logic
```

**Action Handlers (`src/intelligence/action_handler.py`):**

#### **Find Product Flow:**
```
find_product → product_search.py → ChromaDB Vector Search → Product Results
```

#### **Ask Question Flow:**
```
ask_question → FAQ Matching → config/faq_data.json → Contextual Answer
```

#### **Subscribe Flow:**
```
subscribe → Subscription Logic → User Database → Confirmation
```

#### **Payment Flow:**
```
pay_for_product → Payment Validation → Mock Payment → Transaction Status
```

### **5. Response Generation**

```
Action Results → AI Response Generation → Formatted Response
```

**AI Response (`src/intelligence/prompts.py`):**
- 🎯 Context-aware responses
- 🇷🇴 Romanian language support
- 🌸 XOFlowers brand voice
- 📱 Platform-specific formatting

### **6. Response Delivery**

```
Generated Response → Platform API → User Notification
```

## 🏗️ **DETAILED ARCHITECTURE FLOW**

### **Complete Processing Pipeline**

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   User Sends    │    │   Platform      │    │   Application   │
│   Message       │───▶│   API           │───▶│   Receives      │
│   📱💬          │    │   (IG/TG)       │    │   Webhook       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Security      │    │   Message       │    │   Raw Message   │
│   Layer         │◀───│   Validation    │◀───│   Processing    │
│   🔒            │    │   ✅            │    │   📝            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Intent     │    │   Intent        │    │   Message       │
│   Classification│───▶│   Identified    │───▶│   Routing       │
│   🧠            │    │   🎯            │    │   🚦            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                        │
                                                        ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Business      │    │   Action        │    │   Specific      │
│   Logic         │◀───│   Handler       │◀───│   Action        │
│   Execution     │    │   Selection     │    │   Module        │
│   ⚡            │    │   🎛️           │    │   🔧            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │
         ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   AI Response   │    │   Response      │    │   Platform      │
│   Generation    │───▶│   Formatting    │───▶│   Delivery      │
│   ✨            │    │   📝            │    │   📤            │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## 🔍 **INTENT CLASSIFICATION DETAILS**

### **1. Find Product Intent**

**Triggers:**
- "vreau un buchet"
- "arată-mi flori"
- "ce cutii cadou aveți"
- "flori pentru aniversare"

**Process:**
1. Extract search keywords
2. Vector search in ChromaDB
3. Filter by category/price/color
4. Rank by similarity
5. Return top 3-5 results

**Response Format:**
```
🌸 Am găsit aceste produse pentru tine:

1. 🌹 **Buchet Romantic** - 450 MDL
   💬 Buchet elegant cu trandafiri roșii
   📍 Disponibil în magazin

2. 🌷 **Cutie Cadou Deluxe** - 650 MDL
   💬 Cutie frumoasă cu flori mixte
   📍 Livrare disponibilă
```

### **2. Ask Question Intent**

**Triggers:**
- "ce program aveți"
- "unde vă aflați"
- "livrați acasă"
- "ce metode de plată acceptați"

**Process:**
1. Match question with FAQ database
2. Retrieve contextual information
3. Generate personalized answer
4. Include relevant contact info

### **3. Subscribe Intent**

**Triggers:**
- "vreau să mă abonez"
- "actualizări noi"
- "newsletter"
- "oferte speciale"

**Process:**
1. Validate user information
2. Store subscription preferences
3. Send confirmation message
4. Schedule welcome sequence

### **4. Payment Intent**

**Triggers:**
- "vreau să plătesc"
- "cum pot comanda"
- "procesez plata"
- "finalizez comanda"

**Process:**
1. Validate product selection
2. Calculate total cost
3. Mock payment simulation
4. Generate order confirmation

## 🛠️ **ERROR HANDLING FLOW**

### **Common Error Scenarios**

#### **1. API Rate Limits**
```
Rate Limit Exceeded → Queue Message → Retry Logic → Success/Failure
```

#### **2. AI Service Failures**
```
Primary AI Fails → Fallback AI → Fallback Response → User Notification
```

#### **3. Database Errors**
```
ChromaDB Error → Fallback Search → Static Results → Error Logging
```

#### **4. Network Issues**
```
Connection Error → Retry Mechanism → Timeout Handling → User Notification
```

## 📊 **PERFORMANCE MONITORING**

### **Key Metrics**

1. **Response Time**
   - Average processing time per message
   - 95th percentile response time
   - Platform-specific latency

2. **Success Rates**
   - Message processing success rate
   - Intent classification accuracy
   - Action completion rate

3. **User Engagement**
   - Messages per user session
   - Intent distribution
   - User satisfaction scores

### **Monitoring Points**

```
Message Received → Security Check → Intent Classification → Action Processing → Response Generation → Message Sent
      ↓                ↓                    ↓                    ↓                    ↓               ↓
   📊 Count        📊 Filter Rate      📊 Accuracy         📊 Success Rate     📊 Generation Time  📊 Delivery Rate
```

## 🔄 **CONTINUOUS IMPROVEMENT**

### **Learning Loop**

1. **Data Collection**
   - User interactions
   - Success/failure rates
   - Response quality feedback

2. **Analysis**
   - Intent classification accuracy
   - Response relevance
   - User satisfaction

3. **Optimization**
   - Prompt engineering
   - Model fine-tuning
   - Performance optimization

4. **Deployment**
   - A/B testing
   - Gradual rollout
   - Performance monitoring

## 🚀 **SCALING CONSIDERATIONS**

### **Horizontal Scaling**
- Multiple worker processes
- Load balancing
- Database sharding

### **Vertical Scaling**
- Memory optimization
- CPU utilization
- I/O performance

### **Caching Strategy**
- Frequent queries caching
- Session state management
- Response template caching

---

**Last Updated:** January 2025  
**Version:** 1.0.0
