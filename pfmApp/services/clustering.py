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
    "Mobile & Internet":         "mobile recharge internet data plan sim airtel jio bsnl vi wifi broadband net connection topup prepaid postpaid network 4g 5g operator",
    "Household & Maintenance":   "household repair maintenance furniture cleaning utensils home kitchen appliance plumber electrician",
    "Gifts & Donations":         "gift donation charity temple church mosque festival present birthday anniversary offering pooja",
    "Investments & Savings":     "mutual fund stocks fd fixed deposit gold investment saving sip zerodha groww share market",
    "Kids & Family":             "school fees toys baby products children kids family diapers uniform stationery tuition",
    "Pets":                      "vet veterinary pet food dog cat grooming collar leash petshop kennel",
    "Loans & EMI":               "loan emi equated monthly installment home bike car personal repayment bank finance bnpl",
}




# ─── merchant database — known brands mapped directly ──────────────────────────

MERCHANT_MAP = {
    # fuel
    'hp':               'Fuel & Petroleum',
    'hpcl':             'Fuel & Petroleum',
    'indian oil':       'Fuel & Petroleum',
    'iocl':             'Fuel & Petroleum',
    'bpcl':             'Fuel & Petroleum',
    'shell':            'Fuel & Petroleum',
    'essar':            'Fuel & Petroleum',
    'petrol bunk':      'Fuel & Petroleum',
    'fuel station':     'Fuel & Petroleum',
    # streaming
    'netflix':          'Streaming Services',
    'spotify':          'Streaming Services',
    'hotstar':          'Streaming Services',
    'disney':           'Streaming Services',
    'amazon prime':     'Streaming Services',
    'prime video':      'Streaming Services',
    'zee5':             'Streaming Services',
    'sonyliv':          'Streaming Services',
    'youtube premium':  'Streaming Services',
    # telecom
    'jio':              'Mobile & Internet',
    'airtel':           'Mobile & Internet',
    'bsnl':             'Mobile & Internet',
    'vi ':              'Mobile & Internet',
    'vodafone':         'Mobile & Internet',
    'act ':             'Mobile & Internet',
    'hathway':          'Mobile & Internet',
    # food delivery
'zomato':       'Dining & Restaurants',
'swiggy':       'Dining & Restaurants',
    # grocery
'bigbasket':    'Groceries',
'blinkit':      'Groceries',
'dmart':        'Groceries',
'zepto':        'Groceries',
'instamart':    'Groceries',
'swiggy instamart': 'Groceries',
    # transport
    'uber':             'Travel & Transport',
    'ola':              'Travel & Transport',
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
'physicswallah': 'Education & Courses',
    # investment
    'zerodha':          'Investments & Savings',
    'groww':            'Investments & Savings',
    'upstox':           'Investments & Savings',
    'coin':             'Investments & Savings',

'recharge':         'Mobile & Internet',
'mobile recharge':  'Mobile & Internet',
'phone recharge':   'Mobile & Internet',

'ev recharge':      'Fuel & Petroleum',
'electric charge':  'Fuel & Petroleum',
'ev charging':      'Fuel & Petroleum',
}

# embed category descriptions once at startup
category_texts = [CATEGORY_DESCRIPTIONS[cat] for cat in STANDARD_CATEGORIES]
category_embeddings = embedder.encode(category_texts, show_progress_bar=False)
category_embeddings = normalize(category_embeddings)


# ─── helper functions ──────────────────────────────────────────────────────────

def correct_spelling(title):
    words = title.lower().split()
    corrected = [spell.correction(w) or w for w in words]
    return ' '.join(corrected)


def build_expense_text(expense):
    """
    Combines title + note + category hint for richer embedding.
    More context = better clustering separation.
    """
    parts = [expense.expense_title]
    if expense.note:
        parts.append(expense.note)
    return ' '.join(parts)

def check_merchant(titles_in_cluster, notes=None):
    """
    Stage 1 — checks titles and notes against known merchant database.
    Most reliable, zero ambiguity for known brands.
    """
    combined = ' '.join(titles_in_cluster).lower()

    # also check notes if available
    if notes:
        combined += ' ' + ' '.join(n for n in notes if n).lower()

    for merchant, category in MERCHANT_MAP.items():
        if merchant in combined:

            return category
    return None


def generate_custom_name(titles_in_cluster):
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
    combined = ', '.join(titles_in_cluster)  # ← defined here

    candidate_embeddings = embedder.encode(candidate_list, show_progress_bar=False)
    candidate_embeddings = normalize(candidate_embeddings)

    cluster_embedding = embedder.encode([combined], show_progress_bar=False)
    cluster_embedding = normalize(cluster_embedding)

    similarities = np.dot(candidate_embeddings, cluster_embedding.T).flatten()
    best_idx = int(np.argmax(similarities))

    return candidate_list[best_idx].title()


def generate_category_name(titles_in_cluster, expense_contexts=None):
    notes = []

    if expense_contexts:
        notes = [ctx['note'] for ctx in expense_contexts if ctx['note']]

    # stage 1 — merchant database
    merchant_match = check_merchant(titles_in_cluster, notes)
    if merchant_match:
        return merchant_match

    # stage 2 — note merchant check
    if notes:
        for note in notes:
            for merchant, category in MERCHANT_MAP.items():
                if merchant in note.lower():
                    return category

    # stage 3 — embedding similarity
    combined_parts = titles_in_cluster[:]
    if notes:
        combined_parts.extend(notes)
    combined = ' '.join(combined_parts)  # ← defined here, before use

    combined_embedding = embedder.encode([combined], show_progress_bar=False)
    combined_embedding = normalize(combined_embedding)

    similarities = np.dot(category_embeddings, combined_embedding.T).flatten()
    best_idx = int(np.argmax(similarities))
    best_score = float(similarities[best_idx])

    if best_score > 0.2:
        return STANDARD_CATEGORIES[best_idx]

    # stage 4 — custom name
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

        # past months — only cluster once, never again
        # current month — always recluster (new expenses may have been added)
    if period < date.today():
        already_clustered = ExpenseSubCategory.objects.filter(
            user=user, period=period
        ).exists()
        if already_clustered:
            return

    print("Re-clustering...")

    titles = [e.expense_title for e in expenses]

    # build rich text for embedding — title + note + category hint
    texts_for_embedding = [build_expense_text(e) for e in expenses]
    cleaned_texts = [correct_spelling(t) for t in texts_for_embedding]

    # embed and cluster
    embeddings = embedder.encode(cleaned_texts, show_progress_bar=False)
    embeddings = normalize(embeddings)

    clustering = DBSCAN(eps=0.45, min_samples=1, metric='cosine').fit(embeddings)
    labels = clustering.labels_

    # group titles and contexts by cluster
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

    # generate name for each cluster using fallback chain
    cluster_names = {}
    for cluster_id, data in cluster_data.items():
        cluster_names[cluster_id] = generate_category_name(
            data['titles'],
            expense_contexts=data['contexts']
        )


    # save to db
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