import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from spellchecker import SpellChecker
from datetime import date


embedder = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
spell = SpellChecker()

# ─── standard categories ───────────────────────────────────────────────────────

STANDARD_CATEGORIES = [
    "Fuel & Petroleum",
    "Groceries",
    "Clothing & Fashion",
    "Dining & Restaurants",
    "Travel & Transport",
    "Health & Fitness",
    "Streaming Services",
    "Entertainment & Leisure",
    "Sports & Recreation",
    "Education & Courses",
    "Utilities & Bills",
    "Rent & Housing",
    "Personal Care",
    "Electronics & Gadgets",
    "Healthcare & Medical",
    "Insurance",
    "Mobile & Internet",
    "Household & Maintenance",
    "Gifts & Donations",
    "Investments & Savings",
    "Kids & Family",
    "Pets",
    "Loans & EMI",
    "Others",
]

# ─── category descriptions ─────────────────────────────────────────────────────
#
# These are the "anchor" texts for each category.
# The embedding model compares expense text against these descriptions.
# Richer vocabulary = stronger signal = fewer falls to Stage 4.
#
# Rules for writing good descriptions:
#   - Include synonyms, brand names, transliterations
#   - Include words users actually TYPE, not formal category names
#   - Do NOT include words that belong to other categories (causes confusion)

CATEGORY_DESCRIPTIONS = {
    "Fuel & Petroleum": (
        "petrol diesel fuel bike car vehicle fill pump gas station bunk "
        "electric vehicle charging ev charge shell hpcl bpcl iocl indian oil "
        "cng lpg auto gas refuel tank full petrol pump fuel bunk"
    ),
    "Groceries": (
        "grocery vegetables supermarket food items market provisions "
        "bigbasket dmart fruits tomatoes potatoes onion rice sabzi "
        "raw ingredients cooking milk bread eggs dal atta maida wheat "
        "flour chana rajma poha chawal mandi aashirvaad chicken mutton "
        "fish meat raw seafood butcher fresh produce kirana store "
        "monthly ration weekly shopping provisions"
    ),
    "Clothing & Fashion": (
        "dress shirt clothes shopping zudio fashion wear apparel shoes "
        "socks jeans kurta saree cloth fabric myntra ajio westside h&m "
        "dry cleaning laundry ironing alteration tailoring raymond "
        "ethnic wear dupatta lehenga salwar suit formal wear"
    ),
    "Dining & Restaurants": (
        "restaurant hotel food zomato swiggy kfc mcdonalds dining eating "
        "lunch dinner cafe breakfast snacks ordered delivery takeout meal "
        "dish cuisine eatery food stall late night food pizza burger "
        "biryani shawarma dosa idli chai coffee tea street food dhaba "
        "canteen mess food court"
    ),
    "Travel & Transport": (
        "travel bus train flight trip ticket journey uber ola cab auto "
        "metro ksrtc rapido railway airways destination visit tour "
        "manali goa shimla ooty trip parking fastag toll highway "
        "car rental driver taxi intercity outstation commute fare "
        "redbus irctc makemytrip booking"
    ),
    "Health & Fitness": (
        "gym fitness yoga workout exercise health sports swimming running "
        "cycling zumba aerobics gym fee membership monthly whey protein "
        "creatine supplement pre-workout multivitamin protein powder "
        "fish oil nutrition fitness tracker smartwatch fitbit "
        "running shoes sports shoes health club"
    ),
    "Streaming Services": (
        "netflix spotify hotstar amazon prime subscription streaming ott "
        "music movie series disney zee5 sonyliv youtube premium "
        "jiocinema mxplayer subscription plan renewal bundle pack "
        "xstream entertainment subscription"
    ),
    "Entertainment & Leisure": (
        "movie theatre cinema concert event show amusement park bowling "
        "game arcade fun outing picnic wonderla art museum resort "
        "photography workshop escape room water park carnival fair "
        "stand-up comedy night out weekend activity hobby"
    ),
    "Sports & Recreation": (
        "cricket football badminton tennis basketball kit bat ball "
        "sports equipment outdoor stadium jersey studs cleats "
        "swimming club cricket academy karate coaching sports club "
        "turf booking sports gear racket court booking"
    ),
    "Education & Courses": (
        "course udemy book study class learning education tuition skill "
        "college certification training program textbook notebook "
        "buying books coursera skillshare unacademy physicswallah "
        "exam fee study material online learning workshop seminar"
    ),
    "Utilities & Bills": (
        "electricity water gas bill utility payment charges maintenance "
        "corporation tax kseb bescom tneb adani electricity msedcl "
        "power bill water charges sewage municipal bill society "
        "maintenance pipeline connection charges"
    ),
    "Rent & Housing": (
        "rent house flat apartment room lease accommodation pg hostel "
        "society maintenance monthly rent security deposit advance "
        "brokerage rental agreement paying guest dormitory"
    ),
    "Personal Care": (
        "salon haircut beauty parlour grooming skincare cosmetics "
        "facewash shampoo spa massage manicure pedicure waxing "
        "threading eyebrow facial bleach makeup products "
        "personal hygiene toiletries body care"
    ),
    "Electronics & Gadgets": (
        "phone laptop computer charger earphone gadget electronic "
        "device headphone tablet keyboard mouse smart bulb alexa "
        "speaker cctv camera smartwatch iphone samsung apple "
        "croma reliance digital imagine store electronic shop "
        "netmeds 1mg gadget purchase tech"
    ),
    "Healthcare & Medical": (
        "medicine doctor hospital clinic pharmacy medical health "
        "consultation lab test scan xray apollo pharmacy netmeds "
        "1mg pharmeasy bandage thermometer oximeter blood pressure "
        "blood test urine test health checkup prescription "
        "specialist consultation surgery dental vision"
    ),
    "Insurance": (
        "insurance policy premium life health vehicle term cover lic "
        "renewal nominee motor insurance star health hdfc ergo "
        "bajaj allianz new india two wheeler insurance bike insurance "
        "car insurance mediclaim policy payment"
    ),
    "Mobile & Internet": (
        "mobile recharge internet data plan sim airtel jio bsnl wifi "
        "broadband net connection topup prepaid postpaid network "
        "4g 5g operator wifi bill broadband bill internet bill "
        "vodafone hathway act fibernet tata sky dth recharge"
    ),
    "Household & Maintenance": (
        "household repair maintenance furniture cleaning utensils home "
        "kitchen appliance plumber electrician mixer grinder fan "
        "iron box cooler washing machine water purifier vacuum cleaner "
        "inverter battery ac repair carpenter painter pest control "
        "maid charges housekeeping home improvement"
    ),
    "Gifts & Donations": (
        "gift donation charity temple church mosque festival present "
        "birthday anniversary offering amazon gift card voucher "
        "wedding gift diwali gift onam gift christmas present "
        "ngo contribution crowdfunding"
    ),
    "Investments & Savings": (
        "mutual fund stocks fd fixed deposit gold investment saving "
        "sip zerodha groww share market upstox nps ppf recurring "
        "deposit rd equity bond demat portfolio"
    ),
    "Kids & Family": (
        "school tuition baby products children kids family diapers "
        "uniform child daycare playschool nursery school fee baby care "
        "toys drawing book stationery crayon colour pencil "
        "kids shoes kids clothes children activity"
    ),
    "Pets": (
        "vet veterinary pet food dog cat grooming collar leash "
        "petshop kennel aquarium bird hamster pet medicine "
        "pet accessories animal clinic"
    ),
    "Loans & EMI": (
        "loan emi equated monthly installment home bike car personal "
        "repayment bank finance bnpl installment borrowed debt "
        "emi payment car loan bike loan vehicle loan two wheeler "
        "four wheeler interest payment processing fee foreclosure "
        "credit card due outstanding"
    ),
    "Others": (
        "miscellaneous random sundry other general unclassified misc "
        "bank charges atm stamp paper court fee fine challan "
        "passport photo xerox photocopy courier postage "
        "government fee rto registration"
    ),
}

# ─── merchant database ─────────────────────────────────────────────────────────
#
# Stage 1 check — fastest and most reliable.
# Add any merchant you find failing in tests here.
# Key = merchant name in lowercase, Value = category string

MERCHANT_MAP = {
    # fuel
    'hpcl':                 'Fuel & Petroleum',
    'indian oil':           'Fuel & Petroleum',
    'iocl':                 'Fuel & Petroleum',
    'bpcl':                 'Fuel & Petroleum',
    'shell':                'Fuel & Petroleum',
    'petrol bunk':          'Fuel & Petroleum',
    'fuel station':         'Fuel & Petroleum',
    'hp petrol':            'Fuel & Petroleum',
    'hp fuel':              'Fuel & Petroleum',
    'hp bunk':              'Fuel & Petroleum',
    # streaming
    'netflix':              'Streaming Services',
    'spotify':              'Streaming Services',
    'hotstar':              'Streaming Services',
    'disney+':              'Streaming Services',
    'disney plus':          'Streaming Services',
    'amazon prime':         'Streaming Services',
    'prime video':          'Streaming Services',
    'zee5':                 'Streaming Services',
    'sonyliv':              'Streaming Services',
    'youtube premium':      'Streaming Services',
    'jiocinema':            'Streaming Services',
    'mxplayer':             'Streaming Services',
    'airtel xstream':       'Streaming Services',
    # telecom
    'jio':                  'Mobile & Internet',
    'airtel':               'Mobile & Internet',
    'bsnl':                 'Mobile & Internet',
    'vodafone':             'Mobile & Internet',
    'hathway':              'Mobile & Internet',
    'act fibernet':         'Mobile & Internet',
    # food delivery
    'zomato':               'Dining & Restaurants',
    'swiggy':               'Dining & Restaurants',
    'ubereats':             'Dining & Restaurants',
    # grocery
    'bigbasket':            'Groceries',
    'blinkit':              'Groceries',
    'dmart':                'Groceries',
    'zepto':                'Groceries',
    'instamart':            'Groceries',
    'swiggy instamart':     'Groceries',
    'aashirvaad':           'Groceries',
    # transport
    'uber':                 'Travel & Transport',
    'rapido':               'Travel & Transport',
    'irctc':                'Travel & Transport',
    'redbus':               'Travel & Transport',
    'makemytrip':           'Travel & Transport',
    'ksrtc':                'Travel & Transport',
    'metro card':           'Travel & Transport',
    'metro recharge':       'Travel & Transport',
    'ola auto':             'Travel & Transport',
    'ola cab':              'Travel & Transport',
    'ola ride':             'Travel & Transport',
    'fastag':               'Travel & Transport',
    # shopping / fashion
    'zudio':                'Clothing & Fashion',
    'myntra':               'Clothing & Fashion',
    'ajio':                 'Clothing & Fashion',
    'h&m':                  'Clothing & Fashion',
    'westside':             'Clothing & Fashion',
    'raymond':              'Clothing & Fashion',
    # education
    'udemy':                'Education & Courses',
    'coursera':             'Education & Courses',
    'unacademy':            'Education & Courses',
    'skillshare':           'Education & Courses',
    'physicswallah':        'Education & Courses',
    # investment
    'zerodha':              'Investments & Savings',
    'groww':                'Investments & Savings',
    'upstox':               'Investments & Savings',
    # electronics stores
    'croma':                'Electronics & Gadgets',
    'reliance digital':     'Electronics & Gadgets',
    'imagine store':        'Electronics & Gadgets',
    'vijay sales':          'Electronics & Gadgets',
    # healthcare
    'apollo pharmacy':      'Healthcare & Medical',
    'netmeds':              'Healthcare & Medical',
    '1mg':                  'Healthcare & Medical',
    'pharmeasy':            'Healthcare & Medical',
    'apollo':               'Healthcare & Medical',
    # entertainment
    'wonderla':             'Entertainment & Leisure',
    'bookmyshow':           'Entertainment & Leisure',
    'pvr':                  'Entertainment & Leisure',
    'inox':                 'Entertainment & Leisure',
    # utilities
    'bescom':               'Utilities & Bills',
    'tneb':                 'Utilities & Bills',
    'kseb':                 'Utilities & Bills',
    'msedcl':               'Utilities & Bills',
    'adani electricity':    'Utilities & Bills',
    # recharge
    'mobile recharge':      'Mobile & Internet',
    'phone recharge':       'Mobile & Internet',
    'wifi bill':            'Mobile & Internet',
    'wifi payment':         'Mobile & Internet',
    'broadband bill':       'Mobile & Internet',
    # ev
    'ev recharge':          'Fuel & Petroleum',
    'electric charge':      'Fuel & Petroleum',
    'ev charging':          'Fuel & Petroleum',
    # emi patterns
    'bike emi':             'Loans & EMI',
    'car emi':              'Loans & EMI',
    'home emi':             'Loans & EMI',
    'loan emi':             'Loans & EMI',
    'emi payment':          'Loans & EMI',
}

# embed category descriptions once at startup
category_texts = [CATEGORY_DESCRIPTIONS[cat] for cat in STANDARD_CATEGORIES]
category_embeddings = embedder.encode(category_texts, show_progress_bar=False)
category_embeddings = normalize(category_embeddings)

# protected words — spell checker leaves these alone
MERCHANT_WORDS = set()
for merchant_key in MERCHANT_MAP.keys():
    for word in merchant_key.lower().split():
        MERCHANT_WORDS.add(word)

PROTECTED_WORDS = MERCHANT_WORDS | {
    # food words
    'shawarma', 'biryani', 'biriyani', 'paneer', 'paratha',
    'dosa', 'idli', 'vada', 'samosa', 'chapati', 'roti',
    'sabzi', 'daal', 'dal', 'sabji', 'chawal', 'atta',
    # place names
    'manali', 'shimla', 'ooty', 'munnar', 'goa', 'kerala',
    'rishikesh', 'darjeeling', 'leh', 'ladakh', 'coorg',
    'mussoorie', 'nainital', 'gangtok', 'kasol', 'spiti',
    'thrissur', 'kozhikode', 'wayanad', 'kodaikanal',
    # brand names spell checker mangles
    'fitbit', 'alexa', 'cctv', 'zerodha', 'groww',
    'netmeds', 'pharmeasy', 'bescom', 'tneb', 'kseb',
    'wonderla', 'bookmyshow',
}


# ─── helper functions ──────────────────────────────────────────────────────────

def build_expense_text(expense):
    """title + note for embedding"""
    parts = [expense.expense_title]
    if expense.note:
        parts.append(expense.note)
    return ' '.join(parts)


def correct_spelling(text):
    """
    Corrects typos before embedding similarity matching.
    Only used in Stage 3 — not for clustering or display.
    """
    words = text.lower().split()
    corrected = []
    for word in words:
        if word in PROTECTED_WORDS:
            corrected.append(word)
        else:
            fixed = spell.correction(word) or word
            corrected.append(fixed)
    return ' '.join(corrected)


def check_merchant(titles_in_cluster, notes=None):
    """Stage 1 — exact word match against merchant database"""
    combined = ' '.join(titles_in_cluster).lower()
    if notes:
        combined += ' ' + ' '.join(n for n in notes if n).lower()

    combined_words = combined.split()

    for merchant, category in MERCHANT_MAP.items():
        merchant_words = merchant.strip().split()
        if len(merchant_words) == 1:
            if merchant.strip() in combined_words:
                return category
        else:
            if merchant in combined:
                return category
    return None


def generate_custom_name(titles_in_cluster):
    """Stage 4 — extract best phrase from titles when no standard category fits"""
    stop = {
        'my', 'some', 'the', 'a', 'an', 'for', 'and', 'or',
        'at', 'to', 'in', 'of', 'from', 'by', 'with', 'on',
        'purchase', 'bought', 'buy', 'paid', 'payment', 'order',
        'shopping', 'expenses', 'spending'
    }

    candidates = set()
    for title in titles_in_cluster:
        words = [w for w in title.lower().split() if w not in stop]
        for w in words:
            candidates.add(w)
        for w1, w2 in zip(words, words[1:]):
            candidates.add(f"{w1} {w2}")
        clean = ' '.join(words)
        if clean:
            candidates.add(clean)

    if not candidates:
        return titles_in_cluster[0].title()

    candidate_list = list(candidates)
    combined = ', '.join(titles_in_cluster)

    candidate_embeddings = embedder.encode(candidate_list, show_progress_bar=False)
    candidate_embeddings = normalize(candidate_embeddings)

    cluster_embedding = embedder.encode([combined], show_progress_bar=False)
    cluster_embedding = normalize(cluster_embedding)

    similarities = np.dot(candidate_embeddings, cluster_embedding.T).flatten()
    best_idx = int(np.argmax(similarities))

    return candidate_list[best_idx].title()


def generate_category_name(titles_in_cluster, expense_contexts=None):
    """
    4-stage fallback chain:
    1. Merchant database  — exact match, fastest and most reliable
    2. Note merchant check — catches brand names buried in notes
    3. Embedding similarity — semantic matching with spell correction
    4. Custom name — for genuinely novel expenses
    """
    notes = []
    if expense_contexts:
        notes = [ctx['note'] for ctx in expense_contexts if ctx['note']]

    # stage 1 — merchant database
    merchant_match = check_merchant(titles_in_cluster, notes)
    if merchant_match:
        return merchant_match

    # stage 3 — embedding similarity with spell correction
    # (stage 2 note merchant check removed — redundant with stage 1)
    corrected_titles = [correct_spelling(t) for t in titles_in_cluster]
    combined = ' '.join(corrected_titles)
    if notes:
        combined += ' ' + ' '.join(notes)

    combined_embedding = embedder.encode([combined], show_progress_bar=False)
    combined_embedding = normalize(combined_embedding)

    similarities = np.dot(category_embeddings, combined_embedding.T).flatten()
    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])

    # threshold calibration:
    # 0.20 for single-word titles  — short text = weak signal, be lenient
    # 0.28 for multi-word titles   — enough context, be stricter
    # raising above 0.30 causes known merchants to fall to Stage 4
    # lowering below 0.20 causes custom expenses to get wrong categories
    is_single_word = len(titles_in_cluster[0].split()) == 1
    threshold = 0.20 if is_single_word else 0.28

    if best_score > threshold:
        return STANDARD_CATEGORIES[best_idx]

    # stage 4 — custom name
    return generate_custom_name(titles_in_cluster)


# ─── main clustering function ──────────────────────────────────────────────────

def cluster_user_expenses(user, period=None):
    from ..models import ExpenseDb, ExpenseSubCategory

    period = period or date.today().replace(day=1)

    expenses = list(
        ExpenseDb.objects.filter(
            user=user,
            date__year=period.year,
            date__month=period.month,
        ).select_related('sub_category')
    )

    if len(expenses) < 2:
        return

    if period < date.today().replace(day=1):
        already_clustered = ExpenseSubCategory.objects.filter(
            user=user, period=period
        ).exists()
        if already_clustered:
            return

    titles = [e.expense_title for e in expenses]
    texts_for_embedding = [build_expense_text(e) for e in expenses]

    embeddings = embedder.encode(texts_for_embedding, show_progress_bar=False)
    embeddings = normalize(embeddings)

    clustering = DBSCAN(eps=0.45, min_samples=1, metric='cosine').fit(embeddings)
    labels = clustering.labels_

    cluster_data = {}
    for i, label in enumerate(labels):
        if label == -1:
            continue
        if label not in cluster_data:
            cluster_data[label] = {'titles': [], 'contexts': []}
        cluster_data[label]['titles'].append(titles[i])
        cluster_data[label]['contexts'].append({
            'note': expenses[i].note or '',
            'category': expenses[i].category,
        })

    cluster_names = {}
    for cluster_id, data in cluster_data.items():
        cluster_names[cluster_id] = generate_category_name(
            data['titles'],
            expense_contexts=data['contexts']
        )

    ExpenseSubCategory.objects.filter(user=user, period=period).delete()

    for i, expense in enumerate(expenses):
        label = labels[i]

        if label == -1:
            cat_display = 'Others'
            cat_name = 'others'
        else:
            cat_display = cluster_names[label]
            cat_name = cat_display.lower().replace(' ', '_').replace('&', 'and')[:100]

        sub_cat, _ = ExpenseSubCategory.objects.get_or_create(
            user=user,
            name=cat_name,
            period=period,
            defaults={'display_name': cat_display}
        )

        expense.sub_category = sub_cat
        expense.save(update_fields=['sub_category'])