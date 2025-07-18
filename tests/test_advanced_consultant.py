#!/usr/bin/env python3
"""
Продвинутый тест AI консультанта XOFlowers
Проверяет способность адаптироваться к разным типам клиентов и запросов
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Импортируем напрямую без проблемных модулей
import importlib.util
spec = importlib.util.spec_from_file_location("conversation_manager", 
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
    "src", "intelligence", "conversation_manager.py"))
conversation_manager = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conversation_manager)

import time

def test_advanced_consultant():
    """
    Комплексный тест консультанта с 100 разнообразными сценариями
    Покрывает все типы клиентов, языки, ситуации и стили общения
    """
    print("🧪 XOFlowers Advanced AI Consultant Test")
    print("=" * 80)
    print("Тестируем способность ИИ консультировать клиентов разных типов")
    print("100 сценариев на румынском, русском и английском языках")
    print("=" * 80)
    
    cm = conversation_manager.get_conversation_manager()
    
    # БЛОК 1: ПРОСТЫЕ ЗАПРОСЫ (1-20)
    simple_queries = [
        # Румынский - простые запросы
        ("Bună ziua, caut flori pentru soția mea", "ro", "simple_romantic", 
         "Должен спросить детали: повод, цвета, бюджет"),
        
        ("Vreau trandafiri roșii", "ro", "simple_product",
         "Должен показать красные розы и варианты"),
        
        ("Ce flori aveți pentru Valentine's Day?", "ro", "occasion_specific",
         "Должен предложить романтические букеты"),
        
        ("Cât costă un buchet simplu?", "ro", "price_inquiry", 
         "Должен назвать диапазон цен 565-8700 MDL"),
        
        ("Puteți livra astăzi?", "ro", "delivery_inquiry",
         "Должен объяснить условия доставки"),
        
        # Русский - простые запросы  
        ("Привет, нужны цветы для девушки", "ru", "simple_romantic",
         "Должен узнать повод, предпочтения, бюджет"),
        
        ("Хочу букет красных роз", "ru", "simple_product", 
         "Должен показать варианты красных роз"),
        
        ("Что у вас есть на 8 марта?", "ru", "women_day",
         "Должен предложить праздничные букеты"),
        
        ("Сколько стоят ваши букеты?", "ru", "price_inquiry",
         "Должен указать диапазон 565-8700 MDL"),
        
        ("Можете доставить сегодня?", "ru", "delivery_inquiry", 
         "Должен объяснить возможности доставки"),
        
        # Английский - простые запросы
        ("Hello, I need flowers for my wife", "en", "simple_romantic",
         "Должен спросить детали о поводе и предпочтениях"),
        
        ("I want red roses", "en", "simple_product",
         "Должен показать варианты красных роз"),
        
        ("What do you have for anniversaries?", "en", "anniversary", 
         "Должен предложить юбилейные букеты"),
        
        ("How much do your bouquets cost?", "en", "price_inquiry",
         "Должен назвать ценовой диапазон"),
        
        ("Can you deliver today?", "en", "delivery_inquiry",
         "Должен объяснить условия доставки"),
        
        # Смешанные языки - 5 запросов
        ("Salut, vreau roses для мамы", "mixed", "mother_gift",
         "Должен адаптироваться к смешанному языку"),
        
        ("Hello, caut flori pentru nuntă", "mixed", "wedding", 
         "Должен переключиться на свадебную тематику"),
        
        ("Привет, want trandafiri albi", "mixed", "white_roses",
         "Должен понять запрос белых роз"),
        
        ("Bună, нужны flowers for birthday", "mixed", "birthday",
         "Должен предложить праздничные варианты"),
        
        ("Hello, vreau букет красивый", "mixed", "beautiful_bouquet",
         "Должен предложить эстетичные варианты")
    ]
    
    # БЛОК 2: ЗАПРОСЫ С БЮДЖЕТОМ (21-35)
    budget_queries = [
        # Разные бюджеты и языки
        ("Am un buget de 600 lei, ce îmi recomandați?", "ro", "budget_600",
         "Должен найти варианты до 600 MDL"),
        
        ("Caut ceva elegant până în 1000 lei", "ro", "budget_1000_elegant", 
         "Должен предложить элегантные варианты до 1000 MDL"),
        
        ("Vreau ceva special, buget 2000 lei", "ro", "budget_2000_special",
         "Должен показать премиум варианты"),
        
        ("Что можно купить за 500 леев?", "ru", "budget_500",
         "Должен найти варианты в бюджете 500 MDL"),
        
        ("У меня бюджет до 1500, хочу что-то красивое", "ru", "budget_1500",
         "Должен предложить красивые варианты до 1500 MDL"),
        
        ("Нужен роскошный букет, бюджет до 3000", "ru", "budget_3000_luxury",
         "Должен показать люксовые варианты"),
        
        ("I have a budget of 700 MDL", "en", "budget_700", 
         "Должен найти варианты до 700 MDL"),
        
        ("Looking for something nice under 1200 MDL", "en", "budget_1200",
         "Должен предложить хорошие варианты до 1200 MDL"),
        
        ("I want luxury flowers, budget up to 5000 MDL", "en", "budget_5000_luxury",
         "Должен показать роскошные варианты"),
        
        ("Ceva frumos și ieftin, sub 800 lei", "ro", "budget_800_cheap",
         "Должен найти красивые и доступные варианты"),
        
        ("Самое дешевое что у вас есть", "ru", "cheapest",
         "Должен показать самые доступные варианты"),
        
        ("What's your most expensive bouquet?", "en", "most_expensive", 
         "Должен показать премиум варианты"),
        
        ("Nu am mulți bani, ceva sub 600", "ro", "budget_under_600",
         "Должен быть тактичным и найти варианты"),
        
        ("Денег мало, но хочется красиво", "ru", "low_budget_beautiful",
         "Должен предложить красивые бюджетные варианты"),
        
        ("Cheap but beautiful flowers please", "en", "cheap_beautiful",
         "Должен найти компромисс цена-качество")
    ]
    
    # БЛОК 3: СПЕЦИАЛЬНЫЕ ПОВОДЫ (36-55)
    occasion_queries = [
        # Романтические поводы
        ("E ziua de naștere a soției mele mâine", "ro", "wife_birthday",
         "Должен предложить праздничные букеты для жены"),
        
        ("Первое свидание сегодня вечером", "ru", "first_date",
         "Должен предложить нежные, не слишком серьезные цветы"),
        
        ("It's our 10th wedding anniversary", "en", "10th_anniversary", 
         "Должен предложить значимые юбилейные букеты"),
        
        ("Vreau să îmi cer iubita în căsătorie", "ro", "proposal",
         "Должен предложить особенные розы для предложения"),
        
        ("Помирились с девушкой после ссоры", "ru", "reconciliation",
         "Должен предложить извинительные букеты"),
        
        # Семейные поводы
        ("E ziua mamei peste două zile", "ro", "mother_day_advance",
         "Должен предложить материнские букеты"),
        
        ("День рождения у бабушки 85 лет", "ru", "grandmother_85_birthday", 
         "Должен предложить нежные цветы для пожилых"),
        
        ("My daughter is graduating tomorrow", "en", "daughter_graduation",
         "Должен предложить праздничные букеты"),
        
        ("Sora mea pleacă în străinătate", "ro", "sister_departure",
         "Должен предложить цветы для прощания"),
        
        ("Новорожденный в семье друзей", "ru", "newborn_friends",
         "Должен предложить нежные цветы для роддома"),
        
        # Деловые поводы
        ("Deschiderea unei firme noi", "ro", "business_opening",
         "Должен предложить деловые композиции"),
        
        ("Корпоративное мероприятие завтра", "ru", "corporate_event",
         "Должен предложить официальные букеты"),
        
        ("Retirement party for my boss", "en", "retirement_party",
         "Должен предложить торжественные композиции"),
        
        # Печальные поводы
        ("Pentru o înmormântare", "ro", "funeral",
         "Должен быть тактичным, предложить траурные композиции"),
        
        ("На похороны коллеги", "ru", "colleague_funeral", 
         "Должен предложить скорбные букеты"),
        
        ("For a memorial service", "en", "memorial_service",
         "Должен предложить памятные композиции"),
        
        # Извинения и благодарности
        ("Am greșit și vreau să îmi cer scuze", "ro", "apology",
         "Должен предложить извинительные букеты"),
        
        ("Хочу поблагодарить учительницу", "ru", "teacher_thanks",
         "Должен предложить благодарственные цветы"),
        
        ("Thank you flowers for my doctor", "en", "doctor_thanks",
         "Должен предложить профессиональные букеты"),
        
        ("Mulțumesc pentru ajutor", "ro", "help_thanks",
         "Должен предложить благодарственные варианты")
    ]
    
    # БЛОК 4: СЛОЖНЫЕ КОНСУЛЬТАЦИИ (56-75)
    complex_queries = [
        # Несколько получателей
        ("Vreau flori pentru 5 colege de la birou", "ro", "5_colleagues",
         "Должен предложить одинаковые или разные букеты"),
        
        ("Нужны букеты для 3 подружек невесты", "ru", "3_bridesmaids",
         "Должен предложить свадебную серию"),
        
        ("Flowers for 8 teachers at school", "en", "8_teachers", 
         "Должен предложить групповой заказ"),
        
        # Сложные предпочтения
        ("Soția mea nu îi plac trandafirii, dar vrea ceva romantic", "ro", "no_roses_romantic",
         "Должен предложить альтернативные романтичные цветы"),
        
        ("Девушка аллергик, нужны цветы без запаха", "ru", "allergy_no_scent",
         "Должен предложить гипоаллергенные варианты"),
        
        ("She loves purple but hates carnations", "en", "purple_no_carnations",
         "Должен найти фиолетовые цветы без гвоздик"),
        
        # Экстренные ситуации
        ("Am uitat, azi e aniversarea! Pot primi ceva în 2 ore?", "ro", "urgent_anniversary",
         "Должен предложить экстренную доставку"),
        
        ("Забыл про день рождения жены, нужно СРОЧНО!", "ru", "urgent_wife_birthday",
         "Должен решить экстренную ситуацию"),
        
        ("Emergency! Need flowers delivered in 1 hour!", "en", "emergency_1_hour",
         "Должен предложить экстренные варианты"),
        
        # Нестандартные запросы
        ("Vreau să decorez o cameră cu flori", "ro", "room_decoration",
         "Должен предложить декоративные решения"),
        
        ("Можно ли сделать букет в форме сердца?", "ru", "heart_shaped",
         "Должен объяснить возможности кастомизации"),
        
        ("I want flowers that last a month", "en", "long_lasting",
         "Должен предложить долговечные варианты"),
        
        # Корпоративные заказы
        ("Comandă pentru hotel, 20 de buchete pe săptămână", "ro", "hotel_weekly",
         "Должен предложить корпоративное сотрудничество"),
        
        ("Ресторан хочет украсить столики цветами", "ru", "restaurant_tables",
         "Должен предложить ресторанные решения"),
        
        ("Office building needs lobby arrangements", "en", "office_lobby",
         "Должен предложить офисные композиции"),
        
        # Обучающие вопросы
        ("Cum să îngrijesc un buchet să țină mai mult?", "ro", "care_instructions",
         "Должен дать советы по уходу"),
        
        ("Какие цветы символизируют дружбу?", "ru", "friendship_symbolism",
         "Должен объяснить символику цветов"),
        
        ("What flowers mean 'new beginnings'?", "en", "new_beginnings_meaning",
         "Должен рассказать о символике"),
        
        # Сравнения и выбор
        ("Ce diferență e între trandafirii francezi și cei obișnuiți?", "ro", "french_vs_regular_roses",
         "Должен объяснить различия"),
        
        ("Что лучше - букет или композиция в коробке?", "ru", "bouquet_vs_box",
         "Должен помочь с выбором формата"),
        
        ("Roses vs peonies for a wedding?", "en", "roses_vs_peonies_wedding",
         "Должен сравнить варианты для свадьбы")
    ]
    
    # БЛОК 5: ЭМОЦИОНАЛЬНЫЕ И ЛИЧНОСТНЫЕ ЗАПРОСЫ (76-100)
    emotional_queries = [
        # Эмоциональные состояния
        ("Sunt foarte trist, vreau flori care să mă înveselească", "ro", "sad_need_cheering",
         "Должен предложить яркие жизнерадостные цветы"),
        
        ("Сегодня плохое настроение, хочется красоты", "ru", "bad_mood_beauty",
         "Должен предложить поднимающие настроение букеты"),
        
        ("I'm feeling lonely, need some beautiful flowers", "en", "lonely_beauty",
         "Должен предложить утешающие композиции"),
        
        ("Am câștigat la loterie! Vreau ceva spectacular!", "ro", "lottery_win_spectacular",
         "Должен предложить роскошные праздничные букеты"),
        
        ("Повышение на работе! Хочу отпраздновать!", "ru", "promotion_celebration",
         "Должен предложить праздничные варианты"),
        
        ("Got engaged today! Need celebration flowers!", "en", "engagement_celebration",
         "Должен предложить праздничные букеты"),
        
        # Личностные типы
        ("Sunt o persoană foarte exigentă", "ro", "perfectionist_client",
         "Должен быть особенно внимательным к деталям"),
        
        ("Я перфекционист, мне нужно идеально", "ru", "perfectionist_russian", 
         "Должен предложить безупречные варианты"),
        
        ("I'm very picky about flowers", "en", "picky_client",
         "Должен проявить терпение и профессионализм"),
        
        ("Nu mă pricep deloc la flori", "ro", "flower_novice",
         "Должен объяснить все простыми словами"),
        
        ("Ничего не понимаю в цветах, помогите", "ru", "flower_beginner",
         "Должен стать наставником"),
        
        ("I know nothing about flowers, help!", "en", "flower_ignorant",
         "Должен обучать и направлять"),
        
        # Возрастные особенности
        ("Sunt o doamnă în vârstă, vreau ceva clasic", "ro", "elderly_lady_classic",
         "Должен предложить классические варианты"),
        
        ("Молодая девушка, люблю все яркое и необычное", "ru", "young_girl_bright",
         "Должен предложить модные молодежные букеты"),
        
        ("Teenager looking for prom flowers", "en", "teenager_prom",
         "Должен предложить молодежные варианты"),
        
        # Культурные особенности
        ("Suntem o familie tradițională", "ro", "traditional_family",
         "Должен учесть традиционные предпочтения"),
        
        ("Мы мусульмане, есть ли ограничения?", "ru", "muslim_family",
         "Должен учесть культурные особенности"),
        
        ("We're from a different culture", "en", "different_culture",
         "Должен быть культурно чувствительным"),
        
        # Профессиональные особенности
        ("Sunt doctor, vreau ceva pentru spital", "ro", "doctor_hospital", 
         "Должен предложить медицински подходящие варианты"),
        
        ("Работаю в банке, нужно что-то деловое", "ru", "banker_business",
         "Должен предложить деловые композиции"),
        
        ("I'm a teacher, need classroom-appropriate flowers", "en", "teacher_classroom",
         "Должен учесть образовательную среду"),
        
        # Особые запросы
        ("Vreau să surprind pe cineva cu ceva neobișnuit", "ro", "unusual_surprise",
         "Должен предложить креативные решения"),
        
        ("Хочется чего-то такого, чего ни у кого нет", "ru", "unique_request",
         "Должен предложить эксклюзивные варианты"),
        
        ("Something nobody else would think of", "en", "original_idea", 
         "Должен проявить креативность"),
        
        ("Am o poveste specială cu aceste flori", "ro", "special_story",
         "Должен выслушать и учесть историю"),
        
        ("У этих цветов особое значение для нас", "ru", "special_meaning",
         "Должен проявить эмпатию"),
        
        ("These flowers have sentimental value", "en", "sentimental_value",
         "Должен быть чувствительным к эмоциям"),
        
        # Финальные сложные сценарии
        ("Nu știu ce vreau, ajută-mă să descopăr", "ro", "dont_know_help_discover",
         "Должен стать консультантом-психологом"),
        
        ("Запуталась совсем, не знаю что выбрать", "ru", "confused_need_guidance",
         "Должен терпеливо направлять")
    ]
    
    # Объединяем все тесты
    all_tests = simple_queries + budget_queries + occasion_queries + complex_queries + emotional_queries
    
    passed = 0
    failed = 0
    detailed_results = []
    
    print(f"\nЗапускаем {len(all_tests)} тестов...")
    print("=" * 80)
    
    for i, (query, language, scenario_type, expected_behavior) in enumerate(all_tests, 1):
        print(f"\n🧪 Тест {i}/{len(all_tests)}: {scenario_type}")
        print(f"   Язык: {language}")
        print(f"   Запрос: '{query}'")
        print(f"   Ожидаемое поведение: {expected_behavior}")
        
        try:
            # Получаем ответ от консультанта
            start_time = time.time()
            response = cm.process_message_sync(f"test_advanced_{i}", query)
            response_time = time.time() - start_time
            
            # Анализируем качество ответа
            quality_score = analyze_response_quality(query, response, language, scenario_type)
            
            print(f"   Ответ: '{response[:150]}{'...' if len(response) > 150 else ''}'")
            print(f"   Время ответа: {response_time:.2f}с")
            print(f"   Оценка качества: {quality_score}/10")
            
            # Определяем результат
            if quality_score >= 6:
                print("   ✅ ПРОШЕЛ")
                passed += 1
                result = "PASS"
            else:
                print("   ❌ НЕ ПРОШЕЛ")
                failed += 1
                result = "FAIL"
            
            detailed_results.append({
                'test_num': i,
                'scenario': scenario_type,
                'language': language,
                'query': query,
                'response': response,
                'quality_score': quality_score,
                'response_time': response_time,
                'result': result,
                'expected': expected_behavior
            })
            
        except Exception as e:
            print(f"   ❌ ОШИБКА: {e}")
            failed += 1
            detailed_results.append({
                'test_num': i,
                'scenario': scenario_type,
                'language': language,
                'query': query,
                'response': f"ERROR: {str(e)}",
                'quality_score': 0,
                'response_time': 0,
                'result': "ERROR",
                'expected': expected_behavior
            })
    
    # Итоговые результаты
    print("\n" + "=" * 80)
    print("📊 ИТОГОВЫЕ РЕЗУЛЬТАТЫ ПРОДВИНУТОГО ТЕСТА КОНСУЛЬТАНТА")
    print("=" * 80)
    
    total_tests = len(all_tests)
    success_rate = (passed / total_tests) * 100
    
    print(f"Всего тестов: {total_tests}")
    print(f"✅ Прошло: {passed}")
    print(f"❌ Не прошло: {failed}")
    print(f"📈 Процент успеха: {success_rate:.1f}%")
    
    # Анализ по языкам
    language_stats = {}
    for result in detailed_results:
        lang = result['language']
        if lang not in language_stats:
            language_stats[lang] = {'passed': 0, 'total': 0}
        language_stats[lang]['total'] += 1
        if result['result'] == 'PASS':
            language_stats[lang]['passed'] += 1
    
    print(f"\n📊 Статистика по языкам:")
    for lang, stats in language_stats.items():
        rate = (stats['passed'] / stats['total']) * 100
        print(f"   {lang}: {stats['passed']}/{stats['total']} ({rate:.1f}%)")
    
    # Анализ по типам сценариев
    scenario_stats = {}
    for result in detailed_results:
        scenario = result['scenario'].split('_')[0]  # Берем первую часть типа
        if scenario not in scenario_stats:
            scenario_stats[scenario] = {'passed': 0, 'total': 0, 'avg_score': 0}
        scenario_stats[scenario]['total'] += 1
        if result['result'] == 'PASS':
            scenario_stats[scenario]['passed'] += 1
        scenario_stats[scenario]['avg_score'] += result['quality_score']
    
    print(f"\n📊 Статистика по типам сценариев:")
    for scenario, stats in scenario_stats.items():
        rate = (stats['passed'] / stats['total']) * 100
        avg_score = stats['avg_score'] / stats['total']
        print(f"   {scenario}: {stats['passed']}/{stats['total']} ({rate:.1f}%, ср.оценка: {avg_score:.1f})")
    
    # Средняя оценка качества
    avg_quality = sum(r['quality_score'] for r in detailed_results) / len(detailed_results)
    avg_response_time = sum(r['response_time'] for r in detailed_results) / len(detailed_results)
    
    print(f"\n📊 Общие метрики:")
    print(f"   Средняя оценка качества: {avg_quality:.1f}/10")
    print(f"   Среднее время ответа: {avg_response_time:.2f}с")
    
    # Рекомендации по улучшению
    print(f"\n💡 Рекомендации по улучшению:")
    
    if success_rate < 70:
        print("   ⚠️ Низкий общий результат - нужна работа над базовой логикой")
    
    worst_language = min(language_stats.items(), key=lambda x: x[1]['passed']/x[1]['total'])
    print(f"   🌍 Самый слабый язык: {worst_language[0]} - улучшить многоязычность")
    
    worst_scenarios = sorted(scenario_stats.items(), key=lambda x: x[1]['passed']/x[1]['total'])[:3]
    print(f"   📋 Самые слабые сценарии:")
    for scenario, stats in worst_scenarios:
        rate = (stats['passed'] / stats['total']) * 100
        print(f"      - {scenario}: {rate:.1f}%")
    
    if avg_response_time > 2.0:
        print("   ⏱️ Время ответа можно улучшить (>2с)")
    
    print("\n" + "=" * 80)
    
    if success_rate >= 85:
        print("🎉 ОТЛИЧНЫЙ РЕЗУЛЬТАТ! Консультант работает на высоком уровне!")
    elif success_rate >= 70:
        print("✅ ХОРОШИЙ РЕЗУЛЬТАТ! Есть место для улучшений")
    else:
        print("⚠️ ТРЕБУЕТСЯ ДОРАБОТКА! Консультант нуждается в серьезных улучшениях")
    
    return detailed_results, success_rate


def analyze_response_quality(query: str, response: str, language: str, scenario_type: str) -> float:
    """
    Анализирует качество ответа консультанта
    Возвращает оценку от 0 до 10
    """
    score = 0.0
    
    # Базовые критерии (0-4 балла)
    if response and len(response.strip()) > 10:
        score += 1  # Ответ не пустой
    
    if "🌸" in response or any(greeting in response.lower() for greeting in ["bună", "привет", "hello", "salut"]):
        score += 1  # Есть приветствие или символ
    
    if len(response) > 50:
        score += 1  # Ответ достаточно подробный
    
    if "XOFlowers" in response or "flori" in response.lower() or "цвет" in response.lower() or "flower" in response.lower():
        score += 1  # Релевантность теме цветов
    
    # Языковые критерии (0-2 балла)
    if language == "ro" and any(word in response.lower() for word in ["sunt", "pot", "ajut", "flori", "buchete"]):
        score += 1
    elif language == "ru" and any(word in response.lower() for word in ["могу", "помочь", "цветы", "букет"]):
        score += 1
    elif language == "en" and any(word in response.lower() for word in ["can", "help", "flowers", "bouquet"]):
        score += 1
    elif language == "mixed":
        score += 0.5  # Частичный балл за смешанный язык
    
    if not ("sorry" in response.lower() or "error" in response.lower() or "problemă" in response.lower()):
        score += 1  # Нет технических ошибок
    
    # Специфичные критерии сценария (0-3 балла)
    if "budget" in scenario_type.lower() or "price" in scenario_type.lower():
        if any(price_word in response.lower() for price_word in ["mdl", "lei", "preț", "цена", "price", "buget", "бюджет"]):
            score += 1.5
    
    if "romantic" in scenario_type.lower() or "anniversary" in scenario_type.lower():
        if any(romantic_word in response.lower() for romantic_word in ["romantic", "dragost", "любов", "special", "frumos"]):
            score += 1.5
    
    if "urgent" in scenario_type.lower() or "emergency" in scenario_type.lower():
        if any(urgent_word in response.lower() for urgent_word in ["rapid", "imediat", "срочно", "быстро", "urgent", "today"]):
            score += 1.5
    
    if "funeral" in scenario_type.lower() or "memorial" in scenario_type.lower():
        if any(sad_word in response.lower() for sad_word in ["condoleanțe", "îmi pare rău", "соболезнования", "sorry for"]):
            score += 1.5
    
    # Дополнительные баллы за качество (0-1 балл)
    if "?" in response:  # Задает вопросы для уточнения
        score += 0.5
    
    if len(response.split()) > 30:  # Подробный ответ
        score += 0.5
    
    return min(score, 10.0)  # Максимум 10 баллов


if __name__ == "__main__":
    print("Запуск продвинутого теста AI консультанта...")
    test_advanced_consultant()
