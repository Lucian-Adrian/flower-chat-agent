"""
XOFlowers AI Agent - Flask Integration Example
Adaugă în app.py pentru integrare completă cu ChromaDB ULTRA
"""

# Add these imports la început în app.py:
from ai_agent_integration import create_ai_agent

# Add această linie după load_dotenv() în app.py:
try:
    ai_agent = create_ai_agent()
    logger.info(f"🤖 AI Agent loaded with {ai_agent.get_performance_stats()['database_size']} products")
except Exception as e:
    logger.error(f"❌ Failed to initialize AI Agent: {e}")
    ai_agent = None

# Add aceste noi endpoint-uri în app.py:

@app.route('/api/ultra-search', methods=['POST'])
def ultra_search():
    """Ultra-fast intelligent search cu AI Agent"""
    try:
        if not ai_agent:
            return jsonify({'error': 'AI Agent not available'}), 500
            
        data = request.get_json()
        user_query = data.get('query', '')
        user_id = data.get('user_id', f'user_{uuid.uuid4()}')
        max_results = data.get('max_results', 5)
        
        if not user_query:
            return jsonify({'error': 'Query is required'}), 400
        
        # Execute intelligent search
        recommendations = ai_agent.intelligent_search(
            user_query=user_query,
            max_results=max_results,
            user_id=user_id
        )
        
        # Format results
        results = []
        for rec in recommendations:
            results.append({
                'id': rec.id,
                'title': rec.title,
                'description': rec.description[:200] + ('...' if len(rec.description) > 200 else ''),
                'price': rec.price,
                'price_tier': rec.price_tier,
                'category': rec.category,
                'flower_type': rec.flower_type,
                'colors': rec.colors,
                'occasions': rec.occasions,
                'confidence': round(rec.confidence, 3),
                'similarity_score': round(rec.similarity_score, 3),
                'search_time': round(rec.search_time, 3)
            })
        
        return jsonify({
            'status': 'success',
            'query': user_query,
            'user_id': user_id,
            'results': results,
            'total_found': len(results),
            'performance': {
                'search_time': f"{results[0]['search_time']:.3f}s" if results else "0s",
                'confidence_range': f"{min(r['confidence'] for r in results):.2f}-{max(r['confidence'] for r in results):.2f}" if results else "N/A"
            }
        })
        
    except Exception as e:
        logger.error(f"Ultra search error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/personalized-recommendations/<user_id>', methods=['GET'])
def get_personalized_recommendations(user_id):
    """Obține recomandări personalizate pentru user"""
    try:
        if not ai_agent:
            return jsonify({'error': 'AI Agent not available'}), 500
            
        max_results = request.args.get('max_results', 3, type=int)
        
        recommendations = ai_agent.get_personalized_recommendations(
            user_id=user_id,
            max_results=max_results
        )
        
        results = []
        for rec in recommendations:
            results.append({
                'id': rec.id,
                'title': rec.title,
                'description': rec.description[:150] + '...',
                'price': rec.price,
                'price_tier': rec.price_tier,
                'confidence': round(rec.confidence, 2),
                'category': rec.category,
                'flower_type': rec.flower_type
            })
        
        return jsonify({
            'status': 'success',
            'user_id': user_id,
            'personalized_recommendations': results,
            'recommendation_basis': 'user_preferences' if user_id in ai_agent.user_preferences else 'popular_items'
        })
        
    except Exception as e:
        logger.error(f"Personalized recommendations error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/performance-stats', methods=['GET'])
def get_performance_stats():
    """Statistici de performanță pentru AI Agent"""
    try:
        if not ai_agent:
            return jsonify({'error': 'AI Agent not available'}), 500
            
        stats = ai_agent.get_performance_stats()
        
        return jsonify({
            'status': 'success',
            'database_stats': {
                'total_products': stats['database_size'],
                'total_queries': stats['total_queries'],
                'avg_query_time': f"{stats['avg_query_time']:.3f}s",
                'cache_hit_rate': f"{stats['cache_hit_rate']:.1f}%",
                'cache_size': stats['cache_size']
            },
            'ai_stats': stats['ai_agent_stats'],
            'system_health': 'excellent' if stats['avg_query_time'] < 0.3 else 'good' if stats['avg_query_time'] < 0.6 else 'needs_optimization',
            'uptime': 'active'
        })
        
    except Exception as e:
        logger.error(f"Performance stats error: {e}")
        return jsonify({'error': str(e)}), 500

# Update existing webhook pentru folosirea AI Agent:
def enhanced_webhook_with_ai(data):
    """Enhanced webhook cu AI Agent integration"""
    try:
        user_id = data.get('sender_id', f'instagram_user_{uuid.uuid4()}')
        message_text = data.get('message', '').strip()
        
        if not message_text:
            return jsonify({'error': 'Empty message'}), 400
        
        # Use AI Agent dacă e disponibil
        if ai_agent:
            recommendations = ai_agent.intelligent_search(
                user_query=message_text,
                max_results=3,
                user_id=user_id
            )
            
            if recommendations:
                response_text = "🌸 **XOFlowers AI** - Am găsit aceste produse pentru tine:\n\n"
                
                for i, rec in enumerate(recommendations, 1):
                    confidence_emoji = "🎯" if rec.confidence > 0.7 else "✨" if rec.confidence > 0.4 else "💫"
                    
                    response_text += f"{confidence_emoji} **{i}. {rec.title}**\n"
                    response_text += f"   💰 {rec.price} MDL ({rec.price_tier})\n"
                    response_text += f"   📊 Match: {rec.confidence:.0%}\n"
                    
                    if rec.colors:
                        response_text += f"   🎨 Culori: {', '.join(rec.colors)}\n"
                    
                    if rec.occasions:
                        response_text += f"   🎉 Ocazii: {', '.join(rec.occasions)}\n"
                    
                    response_text += "\n"
                
                response_text += "💬 *Vrei să vezi mai multe detalii sau ai întrebări?*\n"
                response_text += f"⚡ *Căutare completă în {recommendations[0].search_time:.2f}s*"
                
                return {
                    'status': 'success',
                    'response': response_text,
                    'recommendations_count': len(recommendations),
                    'ai_powered': True
                }
            else:
                return {
                    'status': 'no_results',
                    'response': "🤔 Nu am găsit produse exacte pentru căutarea ta.\n\n💡 *Încearcă cu:*\n- Nume specific de flori (trandafiri, bujori)\n- Culori (roșu, alb, roz)\n- Ocazii (nuntă, aniversare, iubire)\n- Buget (ieftin, premium, luxury)",
                    'ai_powered': True
                }
        else:
            # Fallback la sistemul existent
            return existing_webhook_logic(data)
            
    except Exception as e:
        logger.error(f"Enhanced webhook error: {e}")
        return {
            'status': 'error', 
            'response': "🔧 Sistemul este temporar indisponibil. Te rog încearcă din nou în câteva momente.",
            'error': str(e)
        }

# Test endpoint pentru verificarea AI Agent:
@app.route('/api/test-ai-agent', methods=['GET'])
def test_ai_agent():
    """Test rapid pentru AI Agent"""
    try:
        if not ai_agent:
            return jsonify({'status': 'error', 'message': 'AI Agent not initialized'}), 500
        
        # Test queries
        test_queries = [
            "trandafiri roșii",
            "buchet pentru nuntă", 
            "ceva ieftin și frumos"
        ]
        
        results = {}
        total_time = 0
        
        for query in test_queries:
            start_time = time.time()
            recommendations = ai_agent.intelligent_search(query, max_results=2)
            query_time = time.time() - start_time
            total_time += query_time
            
            results[query] = {
                'results_count': len(recommendations),
                'query_time': f"{query_time:.3f}s",
                'best_match': recommendations[0].title if recommendations else 'No results',
                'confidence': f"{recommendations[0].confidence:.2f}" if recommendations else 0
            }
        
        stats = ai_agent.get_performance_stats()
        
        return jsonify({
            'status': 'success',
            'ai_agent_status': 'active',
            'test_results': results,
            'avg_test_time': f"{total_time / len(test_queries):.3f}s",
            'database_size': stats['database_size'],
            'system_health': 'excellent'
        })
        
    except Exception as e:
        logger.error(f"AI Agent test error: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

# Pentru a testa sistemul complet:
if __name__ == '__main__':
    print("🚀 Starting XOFlowers Flask App with AI Agent...")
    
    if ai_agent:
        stats = ai_agent.get_performance_stats()
        print(f"✅ AI Agent loaded: {stats['database_size']} products")
        print(f"⚡ Average search time: {stats['avg_query_time']:.3f}s")
        print(f"💾 Cache hit rate: {stats['cache_hit_rate']:.1f}%")
    else:
        print("⚠️ AI Agent not available - using fallback system")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
