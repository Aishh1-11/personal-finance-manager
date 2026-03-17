import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'personal_finance_manager.settings')
django.setup()

from pfmApp.services.clustering import generate_category_name, STANDARD_CATEGORIES

TEST_CASES = [
    # fuel
    ("bike petrol",             "Fuel & Petroleum"),
    ("car diesel",              "Fuel & Petroleum"),
    ("petrol fill",             "Fuel & Petroleum"),
    ("hpcl fuel",               "Fuel & Petroleum"),
    ("ev charging",             "Fuel & Petroleum"),

    # groceries
    ("grocery shopping",        "Groceries"),
    ("vegetables from market",  "Groceries"),
    ("rice and daal",           "Groceries"),
    ("bigbasket order",         "Groceries"),
    ("fruits",                  "Groceries"),

    # dining
    ("zomato order",            "Dining & Restaurants"),
    ("swiggy biryani",          "Dining & Restaurants"),
    ("kfc dinner",              "Dining & Restaurants"),
    ("restaurant lunch",        "Dining & Restaurants"),
    ("ordered chicken curry",   "Dining & Restaurants"),
    ("ubereats shawarma",       "Dining & Restaurants"),

    # travel
    ("uber ride",               "Travel & Transport"),
    ("bus ticket",              "Travel & Transport"),
    ("train ticket",            "Travel & Transport"),
    ("rapido cab",              "Travel & Transport"),
    ("ksrtc bus",               "Travel & Transport"),
    ("trip to manali",          "Travel & Transport"),
    ("flight ticket",           "Travel & Transport"),

    # streaming
    ("netflix subscription",    "Streaming Services"),
    ("spotify premium",         "Streaming Services"),
    ("hotstar plan",            "Streaming Services"),
    ("amazon prime renewal",    "Streaming Services"),

    # mobile
    ("mobile recharge",         "Mobile & Internet"),
    ("jio recharge",            "Mobile & Internet"),
    ("airtel plan",             "Mobile & Internet"),
    ("internet bill",           "Mobile & Internet"),

    # education
    ("udemy course",            "Education & Courses"),
    ("course purchase",         "Education & Courses"),
    ("book purchase",           "Education & Courses"),

    # fitness
    ("gym fee",                 "Health & Fitness"),
    ("yoga class",              "Health & Fitness"),
    ("swimming pool",           "Health & Fitness"),

    # clothing
    ("dress shopping",          "Clothing & Fashion"),
    ("shirt from zudio",        "Clothing & Fashion"),
    ("shoes purchase",          "Clothing & Fashion"),

    # loans
    ("bike emi",                "Loans & EMI"),
    ("home loan",               "Loans & EMI"),
    ("car emi",                 "Loans & EMI"),

    # rent
    ("house rent",              "Rent & Housing"),
    ("flat rent",               "Rent & Housing"),

    # utilities
    ("electricity bill",        "Utilities & Bills"),
    ("water bill",              "Utilities & Bills"),

    # typos — embedder should handle
    ("disel fill",              "Fuel & Petroleum"),
    ("cloths shopping",         "Clothing & Fashion"),
    ("resturant food",          "Dining & Restaurants"),

    # custom name expected — not a standard category
    ("wedding catering",        None),
    ("temple donation",         None),
    ("mehendi ceremony",        None),
]


def run_tests():
    correct = 0
    wrong = 0
    custom = 0
    total = len(TEST_CASES)

    print(f"\n{'─'*75}")
    print(f"{'EXPENSE TITLE':<30} {'EXPECTED':<25} {'GOT':<25} RESULT")
    print(f"{'─'*75}")

    for title, expected in TEST_CASES:
        got = generate_category_name([title])

        if expected is None:
            if got not in STANDARD_CATEGORIES:
                result = "✓ custom"
                custom += 1
            else:
                result = f"✗ should be custom, got {got}"
                wrong += 1
        elif got == expected:
            result = "✓"
            correct += 1
        else:
            result = "✗"
            wrong += 1

        print(f"{title:<30} {str(expected):<25} {got:<25} {result}")

    print(f"{'─'*75}")
    print(f"\nResults:")
    print(f"  Correct  : {correct}")
    print(f"  Wrong    : {wrong}")
    print(f"  Custom   : {custom} (expected custom names)")
    print(f"  Total    : {total}")
    print(f"  Accuracy : {round((correct + custom) / total * 100, 1)}%")
    print(f"{'─'*75}\n")

    # print only wrong ones for easy fixing
    if wrong > 0:
        print("Wrong categorizations to fix:")
        for title, expected in TEST_CASES:
            got = generate_category_name([title])
            if expected is not None and got != expected:
                print(f"  '{title}' → expected '{expected}' got '{got}'")
        print()


if __name__ == '__main__':
    run_tests()