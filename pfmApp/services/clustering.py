import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import normalize
from spellchecker import SpellChecker
from datetime import date
from ..models import ExpenseDb, ExpenseSubCategory

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

CATEGORY_DESCRIPTIONS = {
    "Fuel & Petroleum":          "petrol diesel fuel bike car vehicle fill pump gas station bunk electric vehicle charging ev charge",
    "Groceries":                 "grocery vegetables supermarket food items market provisions bigbasket dmart fruits tomatoes potatoes onion rice sabzi",
    "Clothing & Fashion":        "dress shirt clothes shopping zudio fashion wear apparel shoes socks jeans kurta saree cloth fabric",
    "Dining & Restaurants":      "restaurant hotel food zomato swiggy kfc mcdonalds dining eating lunch dinner cafe breakfast snacks",
    "Travel & Transport":        "travel bus train flight trip ticket journey uber ola cab auto metro ksrtc rapido railway airways",
    "Health & Fitness":          "gym fitness yoga workout exercise health sports swimming running cycling zumba aerobics",
    "Streaming Services":        "netflix spotify hotstar amazon prime subscription streaming ott music movie series disney zee5",
    "Entertainment & Leisure":   "movie theatre cinema concert event show amusement park bowling game arcade fun outing picnic",
    "Sports & Recreation":       "cricket football badminton tennis basketball kit bat ball sports equipment outdoor stadium",
    "Education & Courses":       "course udemy book study class learning education tuition skill college fees certification",
    "Utilities & Bills":         "electricity water gas bill utility payment charges maintenance corporation tax",
    "Rent & Housing":            "rent house flat apartment room lease accommodation pg hostel society maintenance",
    "Personal Care":             "salon haircut beauty parlour grooming skincare cosmetics facewash shampoo spa massage",
    "Electronics & Gadgets":     "phone laptop computer charger earphone gadget electronic device headphone tablet keyboard mouse",
    "Healthcare & Medical":      "medicine doctor hospital clinic pharmacy medical health consultation lab test scan xray",
    "Insurance":                 "insurance policy premium life health vehicle term cover lic",
    "Mobile & Internet":         "mobile recharge internet data plan sim airtel jio bsnl wifi broadband net connection topup prepaid postpaid network 4g 5g operator",
    "Household & Maintenance":   "household repair maintenance furniture cleaning utensils home kitchen appliance plumber electrician",
    "Gifts & Donations":         "gift donation charity temple church mosque festival present birthday anniversary offering pooja",
    "Investments & Savings":     "mutual fund stocks fd fixed deposit gold investment saving sip zerodha groww share market",
    "Kids & Family":             "school fees toys baby products children kids family diapers uniform stationery tuition",
    "Pets":                      "vet veterinary pet food dog cat grooming collar leash petshop kennel",
    "Loans & EMI":               "loan emi equated monthly installment home bike car personal repayment bank finance bnpl",
    "Others":                    "miscellaneous random sundry other general unclassified misc",
}

# ─── merchant database ─────────────────────────────────────────────────────────

MERCHANT_MAP = {
    # fuel
    'hpcl':             'Fuel & Petroleum',
    'indian oil':       'Fuel & Petroleum',
    'iocl':             'Fuel & Petroleum',
    'bpcl':             'Fuel & Petroleum',
    'petrol bunk':      'Fuel & Petroleum',
    'fuel station':     'Fuel & Petroleum',
    # streaming
    'netflix':          'Streaming Services',
    'spotify':          'Streaming Services',
    'hotstar':          'Streaming Services',
    'disney+':          'Streaming Services',
    'disney plus':      'Streaming Services',
    'amazon prime':     'Streaming Services',
    'prime video':      'Streaming Services',
    'zee5':             'Streaming Services',
    'sonyliv':          'Streaming Services',
    'youtube premium':  'Streaming Services',
    # telecom
    'jio':              'Mobile & Internet',
    'airtel':           'Mobile & Internet',
    'bsnl':             'Mobile & Internet',
    'vodafone':         'Mobile & Internet',
    'hathway':          'Mobile & Internet',
    # food delivery
    'zomato':           'Dining & Restaurants',
    'swiggy':           'Dining & Restaurants',
    # grocery
    'bigbasket':        'Groceries',
    'blinkit':          'Groceries',
    'dmart':            'Groceries',
    'zepto':            'Groceries',
    'instamart':        'Groceries',
    'swiggy instamart': 'Groceries',
    # transport
    'uber':             'Travel & Transport',
    'rapido':           'Travel & Transport',
    'irctc':            'Travel & Transport',
    'redbus':           'Travel & Transport',
    'makemytrip':       'Travel & Transport',
    'ksrtc':            'Travel & Transport',
    # shopping
    'zudio':            'Clothing & Fashion',
    'myntra':           'Clothing & Fashion',
    'ajio':             'Clothing & Fashion',
    'h&m':              'Clothing & Fashion',
    'westside':         'Clothing & Fashion',
    # education
    'udemy':            'Education & Courses',
    'coursera':         'Education & Courses',
    'unacademy':        'Education & Courses',
    'skillshare':       'Education & Courses',
    'physicswallah':    'Education & Courses',
    # investment
    'zerodha':          'Investments & Savings',
    'groww':            'Investments & Savings',
    'upstox':           'Investments & Savings',
    # recharge
    'mobile recharge':  'Mobile & Internet',
    'phone recharge':   'Mobile & Internet',
    # ev
    'ev recharge':      'Fuel & Petroleum',
    'electric charge':  'Fuel & Petroleum',
    'ev charging':      'Fuel & Petroleum',
}

# embed category descriptions once at startup
category_texts = [CATEGORY_DESCRIPTIONS[cat] for cat in STANDARD_CATEGORIES]
category_embeddings = embedder.encode(category_texts, show_progress_bar=False)
category_embeddings = normalize(category_embeddings)

# protected words — built from merchant map only
# no place names needed since spell correction only runs during naming
MERCHANT_WORDS = set()
for merchant_key in MERCHANT_MAP.keys():
    for word in merchant_key.lower().split():
        MERCHANT_WORDS.add(word)

PROTECTED_WORDS = MERCHANT_WORDS


# ─── helper functions ──────────────────────────────────────────────────────────

def build_expense_text(expense):
    """title + note for embedding — no spell correction needed here"""
    parts = [expense.expense_title]
    if expense.note:
        parts.append(expense.note)
    return ' '.join(parts)


def correct_spelling(text):
    """
    Only used for category matching — not for clustering.
    Protects merchant names from being corrected.
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
    1. Merchant database
    2. Note merchant check
    3. Embedding similarity (with spell correction for better matching)
    4. Custom name from titles
    """
    notes = []
    if expense_contexts:
        notes = [ctx['note'] for ctx in expense_contexts if ctx['note']]

    # stage 1 — merchant database
    merchant_match = check_merchant(titles_in_cluster, notes)
    if merchant_match:
        return merchant_match

    # stage 2 — note merchant check
    if notes:
        note_words_list = [note.lower().split() for note in notes]
        for note, note_words in zip(notes, note_words_list):
            for merchant, category in MERCHANT_MAP.items():
                merchant_words = merchant.strip().split()
                if len(merchant_words) == 1:
                    if merchant.strip() in note_words:
                        return category
                else:
                    if merchant in note.lower():
                        return category

    # stage 3 — embedding similarity
    # spell correct here for better matching — not for display
    corrected_titles = [correct_spelling(t) for t in titles_in_cluster]
    combined_parts = corrected_titles[:]
    if notes:
        combined_parts.extend(notes)
    combined = ' '.join(combined_parts)

    combined_embedding = embedder.encode([combined], show_progress_bar=False)
    combined_embedding = normalize(combined_embedding)

    similarities = np.dot(category_embeddings, combined_embedding.T).flatten()
    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])

    if best_score > 0.2:
        return STANDARD_CATEGORIES[best_idx]

    # stage 4 — custom name using original titles for display
    return generate_custom_name(titles_in_cluster)


# ─── main clustering function ──────────────────────────────────────────────────

def cluster_user_expenses(user, period=None):
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

    # past months — cluster once and cache
    # current month — always recluster
    if period < date.today().replace(day=1):
        already_clustered = ExpenseSubCategory.objects.filter(
            user=user, period=period
        ).exists()
        if already_clustered:
            return

    titles = [e.expense_title for e in expenses]

    # no spell correction here — embedder handles typos well enough for grouping
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