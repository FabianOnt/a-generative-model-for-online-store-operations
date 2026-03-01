N_USERS = 1000

N_VENDORS = 200

N_PRODUCTS = 10000

N_ORDERS = 5000

COUNTIRES = [
    "Mexico",
    "United States",
    "Canada",
    "Brazil",
    "Argentina",
    "Spain",
    "France",
    "Germany",
    "Japan",
    "Australia"
]

CATEGORIES = {
    "Electronics & Gadgets": [
        "Smartphones", "Tablets", "Laptops", "Desktops & Monitors", "Smartwatches",
        "Headphones & Earbuds", "Cameras & Photography Equipment", "Gaming Consoles",
        "VR & AR Devices", "Wearable Tech"
    ],
    "Home & Living": [
        "Furniture", "Home Décor", "Bedding & Linens", "Kitchen Appliances",
        "Cookware & Bakeware", "Storage & Organization", "Lighting",
        "Cleaning Supplies", "Home Improvement Tools", "Gardening & Outdoor Equipment"
    ],
    "Fashion & Apparel": [
        "Mens Clothing", "Womens Clothing", "Kids Clothing", "Footwear",
        "Bags & Backpacks", "Accessories", "Jewelry & Watches", "Eyewear & Sunglasses",
        "Activewear & Sportswear", "Outerwear & Jackets"
    ],
    "Beauty & Personal Care": [
        "Skincare", "Haircare", "Makeup & Cosmetics", "Fragrances & Perfumes",
        "Nail Care", "Bath & Body Products", "Grooming & Shaving",
        "Oral Care", "Beauty Tools & Accessories", "Wellness Products"
    ],
    "Food & Beverages": [
        "Fresh Produce", "Snacks", "Beverages", "Packaged Foods", "Health Foods & Supplements",
        "Spices & Condiments", "Frozen Foods", "Organic & Natural Products",
        "Alcoholic Beverages", "Gourmet & Specialty Foods"
    ],
    "Sports & Outdoors": [
        "Fitness Equipment", "Camping Gear", "Hiking & Climbing Equipment",
        "Bicycles & Accessories", "Water Sports Equipment", "Winter Sports Gear",
        "Fishing & Hunting Equipment", "Team Sports Gear", "Yoga & Meditation Gear",
        "Sports Apparel & Footwear"
    ],
    "Baby & Kids": [
        "Baby Clothing", "Baby Gear", "Baby Toys", "Kids Toys", "Educational Toys",
        "School Supplies", "Baby Feeding Products", "Nursery Furniture",
        "Diapers & Wipes", "Baby Health & Safety"
    ],
    "Books & Media & Stationery": [
        "Books", "Magazines", "E-books", "Music & Instruments", "Movies & TV Shows",
        "Board Games & Puzzles", "Office Supplies", "Craft & Art Supplies",
        "Calendars & Planners", "Stationery"
    ],
    "Automotive & Tools": [
        "Car Accessories", "Motorcycle Gear", "Car Care Products", "Auto Parts",
        "Power Tools", "Hand Tools", "Safety Gear", "Workshop Equipment",
        "Outdoor Tools", "Batteries & Chargers"
    ],
    "Pets": [
        "Pet Food", "Pet Toys", "Pet Grooming Products", "Aquarium Supplies",
        "Pet Beds & Furniture", "Pet Training Supplies", "Pet Carriers",
        "Pet Health & Wellness", "Cat Supplies", "Dog Supplies"
    ]
}

MEAN_PRICE_CATEGORY = {
    "Electronics & Gadgets": 350.0,
    "Home & Living": 120.0,
    "Fashion & Apparel": 50.0,
    "Beauty & Personal Care": 30.0,
    "Food & Beverages": 15.0,
    "Sports & Outdoors": 75.0,
    "Baby & Kids": 40.0,
    "Books & Media & Stationery": 20.0,
    "Automotive & Tools": 80.0,
    "Pets": 25.0
}

INITIAL_SEX_PROB = {
    'Electronics & Gadgets': 0.7,
    'Home & Living': 0.4,
    'Fashion & Apparel': 0.3,
    'Beauty & Personal Care': 0.3,
    'Food & Beverages': 0.5,
    'Sports & Outdoors': 0.5,
    'Baby & Kids': 0.5,
    'Books & Media & Stationery': 0.5,
    'Automotive & Tools': 0.7,
    'Pets': 0.5
}