"""
Verdant Heritage Organic Farm - Structured Data Module
Contains products, CSA subscription tiers, farm tours, blog posts, testimonials, and FAQs.
"""

PRODUCTS = [
    {
        "id": 1,
        "name": "Heirloom Cherokee Purple Tomatoes",
        "category": "Vegetables",
        "price": 5.75,
        "unit": "per lb",
        "badge": "Heirloom",
        "rating": 4.9,
        "reviews_count": 48,
        "in_stock": True,
        "seasonal": False,
        "origin": "Sunny Ridge Greenhouse, Block 2",
        "harvest_date": "Harvested Daily at Dawn",
        "storage_tips": "Store at room temperature out of direct sunlight. Never refrigerate to preserve rich sugars and complex acidity.",
        "nutrition": "High in Lycopene, Vitamin C, Potassium, and Vitamin K.",
        "description": "Prized heirloom tomato dating back over 100 years. Deep dusky-rose skin with greenish shoulders, rich wine-sweet flavor, and luscious meaty texture.",
        "image": "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1592924357228-91a4daadcfea?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1546470427-227c7369a4d8?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 2,
        "name": "Crisp Mountain Honeycrisp Apples",
        "category": "Fruits",
        "price": 4.50,
        "unit": "per 2 lb bag",
        "badge": "Bestseller",
        "rating": 5.0,
        "reviews_count": 86,
        "in_stock": True,
        "seasonal": True,
        "origin": "North Slope Orchard, Row 14",
        "harvest_date": "Yesterday Morning",
        "storage_tips": "Keep in the refrigerator crisper drawer. Will stay remarkably crisp and juicy for up to 4 weeks.",
        "nutrition": "Rich in Dietary Fiber, Vitamin C, and Antioxidants.",
        "description": "Hand-picked from our cool-climate mountain orchard. Explosively crisp with an exquisite balance of floral sweetness and lively tartness.",
        "image": "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1560806887-1e4cd0b6cbd6?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 3,
        "name": "Artisanal Field Harvest Greens Box",
        "category": "Farm Boxes",
        "price": 18.00,
        "unit": "per harvest tote",
        "badge": "Farm Favorite",
        "rating": 4.9,
        "reviews_count": 64,
        "in_stock": True,
        "seasonal": False,
        "origin": "Market Garden Valley, Plot 7",
        "harvest_date": "Harvested to order",
        "storage_tips": "Wrap gently in damp organic cotton cloth and refrigerate. Enjoy within 7-10 days.",
        "nutrition": "Powerhouse of Folate, Iron, Vitamin A, and Chlorophyll.",
        "description": "A vibrant assortment of tender baby kale, red butterhead lettuce, spicy wild arugula, mizuna, and edible calendula petals washed in clean well water.",
        "image": "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1540420773420-3366772f4999?auto=format&fit=crop&w=800&q=80",
            "https://images.unsplash.com/photo-1518977676601-b53f82aba655?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 4,
        "name": "Rainbow Heritage Baby Carrots",
        "category": "Vegetables",
        "price": 3.95,
        "unit": "per bunch with tops",
        "badge": "Organic",
        "rating": 4.8,
        "reviews_count": 39,
        "in_stock": True,
        "seasonal": False,
        "origin": "East Bottomland Terraces",
        "harvest_date": "Daily harvest",
        "storage_tips": "Remove carrot tops before storing in the fridge to maintain root moisture. Use green tops for zesty pesto!",
        "nutrition": "High in Beta-Carotene, Anthocyanins, Lutein, and Fiber.",
        "description": "Gorgeous heritage bunch of deep purple, solar yellow, and radiant orange carrots. Tender enough to enjoy raw with remarkable natural sweetness.",
        "image": "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1598170845058-32b9d6a5da37?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 5,
        "name": "Raw Wildflower Honeycomb & Honey Jar",
        "category": "Seasonal Produce",
        "price": 14.50,
        "unit": "16 oz jar + comb",
        "badge": "Pure & Raw",
        "rating": 5.0,
        "reviews_count": 112,
        "in_stock": True,
        "seasonal": False,
        "origin": "Verdant Apiaries & Clover Meadows",
        "harvest_date": "Late Summer Extraction",
        "storage_tips": "Store at ambient room temperature in a dry pantry. Pure raw honey never expires or spoils.",
        "nutrition": "Rich in Living Probiotics, Active Enzymes, and Wild Pollen.",
        "description": "100% unpasteurized, single-origin honey harvested from bee colonies foraging on wildflower meadows, clover, and lavender. Includes a fresh cut of edible wax honeycomb.",
        "image": "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1587049352846-4a222e784d38?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 6,
        "name": "Pasture-Raised Heritage Farm Eggs",
        "category": "Farm Boxes",
        "price": 7.25,
        "unit": "dozen (12 eggs)",
        "badge": "Pasture-Raised",
        "rating": 4.9,
        "reviews_count": 94,
        "in_stock": True,
        "seasonal": False,
        "origin": "Heritage Hen Pastures (50 sq ft/bird)",
        "harvest_date": "Collected Daily at 7 AM & 3 PM",
        "storage_tips": "Refrigerate in carton with the pointed end down to keep the yolk centered and fresh.",
        "nutrition": "6g Protein per egg, abundant Omega-3 fatty acids, and Vitamin D3.",
        "description": "Laid by heritage Rhode Island Red and Ameraucana hens free-roaming on fresh organic clover pastures. Deep amber yolks with unbeatable rich flavor.",
        "image": "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1582722872445-44dc5f7e3c8f?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 7,
        "name": "Stone-Ground Ancient Emmer Farro Flour",
        "category": "Organic Grains",
        "price": 8.90,
        "unit": "3 lb cotton sack",
        "badge": "Heritage Grain",
        "rating": 4.8,
        "reviews_count": 31,
        "in_stock": True,
        "seasonal": False,
        "origin": "Millhouse Grain Terraces",
        "harvest_date": "Milled on Granite Stone This Week",
        "storage_tips": "Keep in an airtight container in a cool pantry or freezer to protect the delicate wheat germ oils.",
        "nutrition": "Nutrient-dense with easily digestible protein, magnesium, and B vitamins.",
        "description": "Slow stone-ground whole wheat grain from our heirloom non-GMO emmer crops. Imparts a deeply nutty, earthy flavor to rustic breads, pasta, and pastries.",
        "image": "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1509440159596-0249088772ff?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 8,
        "name": "Fresh Sweet Genovese Basil & Herb Bouquet",
        "category": "Herbs",
        "price": 3.50,
        "unit": "per fresh bunch",
        "badge": "Aromatic",
        "rating": 4.9,
        "reviews_count": 42,
        "in_stock": True,
        "seasonal": False,
        "origin": "Herb Sanctuary Greenhouse",
        "harvest_date": "Cut fresh on day of packing",
        "storage_tips": "Place stems in a glass of fresh water at room temperature like freshly cut flowers.",
        "nutrition": "Contains Eugenol, Rosmarinic acid, and Vitamin A.",
        "description": "Intensely fragrant large-leaf Genovese basil grown alongside sweet Italian oregano and thyme. Ideal for pesto, Caprese salads, and slow marinara.",
        "image": "https://images.unsplash.com/photo-1618164436241-4473940d1f5c?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1618164436241-4473940d1f5c?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 9,
        "name": "Sweet Sun-Ripened Field Strawberries",
        "category": "Fruits",
        "price": 6.50,
        "unit": "1 lb biodegradable clamshell",
        "badge": "Limited Seasonal",
        "rating": 5.0,
        "reviews_count": 138,
        "in_stock": True,
        "seasonal": True,
        "origin": "Berry Patch Rows 1-8",
        "harvest_date": "Hand-picked this morning",
        "storage_tips": "Do not wash until immediately before eating. Store dry in refrigerator.",
        "nutrition": "High in Vitamin C, Manganese, and Polyphenols.",
        "description": "Sweet, fragrant, ruby-red strawberries allowed to fully ripen under natural sunshine on straw-mulched beds without synthetic sprays.",
        "image": "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1464965911861-746a04b4bca6?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 10,
        "name": "Artisan Wood-Fired Sourdough Boule",
        "category": "Organic Grains",
        "price": 8.50,
        "unit": "800g loaf",
        "badge": "Bakery",
        "rating": 4.9,
        "reviews_count": 77,
        "in_stock": True,
        "seasonal": False,
        "origin": "Farmstead Stone Hearth Bakery",
        "harvest_date": "Baked at 4:30 AM Daily",
        "storage_tips": "Store cut-side down on a wooden bread board or in a linen bread bag.",
        "nutrition": "Fermented for 36 hours for easy digestion and low glycemic impact.",
        "description": "Crusty golden exterior, open airy crumb, and a gentle sourdough tang crafted exclusively with our organic stone-ground flours and well water.",
        "image": "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1589367920969-ab8e050bbb04?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 11,
        "name": "Cold-Pressed Extra Virgin Olive Oil",
        "category": "Seasonal Produce",
        "price": 22.00,
        "unit": "500 ml dark bottle",
        "badge": "Estate Reserve",
        "rating": 5.0,
        "reviews_count": 52,
        "in_stock": True,
        "seasonal": False,
        "origin": "South Grove Terraced Hillside",
        "harvest_date": "First Cold Pressing < 24°C",
        "storage_tips": "Store away from heat and light in a cool pantry cabinet.",
        "nutrition": "Loaded with Oleic acid polyphenols, Vitamin E, and heart-healthy fats.",
        "description": "Single-estate early harvest olive oil featuring vibrant peppery finish, fresh-cut grass aroma, and ultra-low acidity (<0.2%).",
        "image": "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1474979266404-7eaacbcd87c5?auto=format&fit=crop&w=800&q=80"
        ]
    },
    {
        "id": 12,
        "name": "Family Farm Bounty Harvest Box",
        "category": "Farm Boxes",
        "price": 38.00,
        "unit": "large wooden crate",
        "badge": "Top Value",
        "rating": 5.0,
        "reviews_count": 105,
        "in_stock": True,
        "seasonal": False,
        "origin": "Curated from All 8 Field Blocks",
        "harvest_date": "Harvested morning of dispatch",
        "storage_tips": "Includes detailed weekly produce care and storage guide inside.",
        "nutrition": "Feeds 3-5 people a complete rainbow spectrum of farm nutrients.",
        "description": "Our premier weekly family box: 10-12 seasonal organic vegetables, 2 fruits, a bouquet of fresh culinary herbs, plus farm kitchen recipe cards.",
        "image": "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=800&q=80",
        "gallery": [
            "https://images.unsplash.com/photo-1610832958506-aa56368176cf?auto=format&fit=crop&w=800&q=80"
        ]
    }
]

CATEGORIES = [
    "All",
    "Vegetables",
    "Fruits",
    "Greens",
    "Organic Grains",
    "Herbs",
    "Farm Boxes",
    "Seasonal Produce"
]

CSA_PLANS = [
    {
        "id": "weekly-box",
        "name": "Weekly Harvest Box",
        "price": 34.00,
        "frequency": "Billed weekly",
        "badge": "Most Popular",
        "servings": "Ideal for 1-2 people",
        "items_count": "7-9 seasonal items",
        "description": "Our most popular share. A curated mix of vibrant greens, cooking essentials, fresh roots, seasonal fruits, and herbs harvested at sunrise.",
        "included": [
            "7-9 varieties of freshly harvested organic produce",
            "Weekly rotating seasonal variety from our 8 field blocks",
            "Printed farm newsletter & chef-crafted seasonal recipes",
            "10% discount on all farm visits & store purchases",
            "Free farm gate pickup or low-carbon home delivery"
        ],
        "delivery_days": "Tuesdays & Fridays",
        "icon": "leaf"
    },
    {
        "id": "biweekly-box",
        "name": "Bi-Weekly Seasonal Box",
        "price": 48.00,
        "frequency": "Billed every 2 weeks",
        "badge": "Flexible",
        "servings": "Ideal for couples & casual cooks",
        "items_count": "9-11 seasonal items",
        "description": "Perfect for smaller households or frequent travelers who want peak seasonal organic nutrition without produce overwhelm.",
        "included": [
            "9-11 hearty varieties with longer shelf life",
            "Artisanal farm staple included in each box (Honey or Flour)",
            "Online portal to swap up to 2 items per delivery",
            "Pause or skip deliveries anytime with 48h notice",
            "Invitation to our Members-Only Harvest Festival"
        ],
        "delivery_days": "Alternate Wednesdays",
        "icon": "calendar"
    },
    {
        "id": "family-box",
        "name": "Family Bounty Box",
        "price": 62.00,
        "frequency": "Billed weekly",
        "badge": "Best Value",
        "servings": "Ideal for families of 3-5",
        "items_count": "13-16 seasonal items + dozen eggs",
        "description": "The ultimate farm feast. Packed with abundant vegetables, dual fruits, pasture-raised farm eggs, fresh culinary herbs, and baker's sourdough loaf.",
        "included": [
            "13-16 generous organic vegetables and fruits",
            "1 dozen pasture-raised heritage eggs included weekly",
            "1 wood-fired artisan sourdough boule included",
            "Priority selection of limited berries and heirloom varieties",
            "Free guided annual farm tour for the entire family"
        ],
        "delivery_days": "Tuesdays, Thursdays & Saturdays",
        "icon": "sun"
    }
]

FARM_TOURS = [
    {
        "id": "guided-walk",
        "title": "Guided Regenerative Farm Walk",
        "duration": "90 Minutes",
        "price": 15.00,
        "price_note": "per adult (kids under 12 free)",
        "badge": "Classic Tour",
        "image": "https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80",
        "description": "Walk our fertile fields with 4th generation grower Thomas Ward. Discover heirloom seed preservation, compost biology, and solar irrigation systems.",
        "highlights": [
            "Guided walking exploration of all 8 cultivation blocks",
            "Tasting straight from the vine in the greenhouse",
            "Visit the composting facility and pollinator wildflower meadows",
            "Complimentary chilled herbal tea and fresh fruit slice"
        ],
        "days": "Wednesday & Saturday mornings at 10:00 AM"
    },
    {
        "id": "family-harvester",
        "title": "Family Harvester & Animal Experience",
        "duration": "120 Minutes",
        "price": 25.00,
        "price_note": "per person (kids under 3 free)",
        "badge": "Family Favorite",
        "image": "https://images.unsplash.com/photo-1595974482597-4b8da8879bc5?auto=format&fit=crop&w=800&q=80",
        "description": "An unforgettable hands-on experience for children and families. Meet our pasture hens, learn to gently harvest baby carrots, and ride the tractor wagon.",
        "highlights": [
            "Interactive tractor wagon tour of the heritage orchard",
            "Feed and visit our heritage pastured hens",
            "Pick-your-own 2 lb produce basket to take home",
            "Kid-friendly soil bug discovery hunt"
        ],
        "days": "Saturdays & Sundays at 11:00 AM & 2:00 PM"
    },
    {
        "id": "sunset-tasting",
        "title": "Sunset Orchard Tasting & Farmstead Table",
        "duration": "150 Minutes",
        "price": 45.00,
        "price_note": "per person (includes tastings)",
        "badge": "Gourmet Evening",
        "image": "https://images.unsplash.com/photo-1511525287987-1979860b6674?auto=format&fit=crop&w=800&q=80",
        "description": "Celebrate the golden hour in our heirloom apple orchard. Enjoy artisanal cheeses, warm sourdough, freshly pressed cider, and wood-fired flatbreads under the string lights.",
        "highlights": [
            "Scenic golden-hour stroll through the orchards and vineyard",
            "5-course artisanal tasting menu prepared by farmstead culinary team",
            "Live acoustic folk music under our vintage timber pergola",
            "Take-home jar of limited edition wildflower comb honey"
        ],
        "days": "Friday & Saturday Evenings at 5:30 PM"
    }
]

BLOG_POSTS = [
    {
        "id": 1,
        "title": "The Secret Life of Soil: How Regenerative Practices Restore Nutrient Density",
        "category": "Farming",
        "date": "September 12, 2026",
        "read_time": "5 min read",
        "author": "Dr. Sarah Lindqvist (Soil Microbiologist)",
        "image": "https://images.unsplash.com/photo-1500651230702-0e2d8a49d4ad?auto=format&fit=crop&w=800&q=80",
        "summary": "True organic food begins with living biology under our boots. Here is how zero-tillage, biochar, and cover crop cocktails turn ordinary dirt into carbon-rich, living humus.",
        "content": """
Healthy soil is not merely an inert medium for roots—it is an intricate living metropolis. A single teaspoon of fertile regenerative soil contains more living microorganisms than there are humans on Earth.

At Verdant Heritage Farm, we transitioned entirely to zero-till and deep cover-cropping seven years ago. Instead of churning up the subterranean fungal mycorrhizae with industrial plows, we crimp thick rye and vetch into a living organic mulch. This sponge-like carpet preserves moisture, shields microbial life from harsh summer heat, and sequesters atmospheric carbon deep underground.

When crops grow in nutrient-dense living soil, they synthesize higher levels of antioxidants, flavonoids, and essential phytonutrients. The result isn't just better for the biosphere—you can literally taste the extraordinary depth of flavor in every heirloom tomato and crisp apple.
        """
    },
    {
        "id": 2,
        "title": "Autumn Harvest Galette with Heirloom Tomatoes & Fresh Thyme",
        "category": "Recipes",
        "date": "September 8, 2026",
        "read_time": "4 min read",
        "author": "Chef Elena Rossi (Farmstead Kitchen)",
        "image": "https://images.unsplash.com/photo-1565299624946-b28f40a0ae38?auto=format&fit=crop&w=800&q=80",
        "summary": "Celebrate the end-of-summer harvest with this rustic, golden-crusted galette featuring our Cherokee Purple tomatoes, stone-ground emmer flour, and sheep's milk ricotta.",
        "content": """
Rustic galettes are the ultimate celebration of farm-fresh produce: effortless, beautifully imperfect, and deeply satisfying.

### Ingredients:
* 1 1/2 cups stone-ground ancient emmer flour
* 1/2 cup cold unsalted grass-fed butter, cubed
* 3 tbsp ice-cold well water
* 1 1/2 lbs mixed heirloom tomatoes, sliced 1/4-inch thick
* 1 cup whole-milk ricotta seasoned with lemon zest & sea salt
* 2 tbsp freshly picked thyme leaves
* 1 tbsp cold-pressed extra virgin olive oil

### Instructions:
1. Pulse flour, salt, and cold butter until coarse pea-sized crumbs form. Gradually drizzle ice water until dough just holds together. Chill for 45 minutes.
2. Slice tomatoes and lay on paper towels with a pinch of flaky salt to draw out excess liquid for 20 minutes.
3. Roll dough onto parchment into a 12-inch rustic round. Spread seasoned ricotta in the center, leaving a 2-inch border.
4. Layer the colorful heirloom tomato slices over the cheese, drizzle with olive oil and scatter fresh thyme.
5. Fold the edges of dough over the filling, pleating gently. Brush pastry with egg wash.
6. Bake at 400°F (205°C) for 35-40 minutes until golden brown and bubbling. Cool slightly before slicing!
        """
    },
    {
        "id": 3,
        "title": "Why Community Supported Agriculture (CSA) Is the Future of Food Independence",
        "category": "Sustainability",
        "date": "August 28, 2026",
        "read_time": "6 min read",
        "author": "Thomas Ward (4th Gen Farmer)",
        "image": "https://images.unsplash.com/photo-1488459716781-31db52582fe9?auto=format&fit=crop&w=800&q=80",
        "summary": "When you subscribe to a local farm CSA, you bypass fragile global supply chains, eliminate warehouse refrigeration waste, and forge a personal bond with your growers.",
        "content": """
The modern industrial food system separates consumers from the land by thousands of miles, weeks of cold storage, and endless layers of packaging. CSA turns this model upside-down.

By joining a CSA, you become an active stakeholder in the farm season. In spring, your upfront share enables us to purchase organic non-GMO seeds, prepare bio-intensive beds, and maintain fair living wages for our harvesting team. In return, your family receives the freshest, most vibrant seasonal produce harvested mere hours before reaching your table.

There are no intermediate warehouses, no artificial ripening gases, and no single-use plastic wraps. It is genuine, community-powered food sovereignty.
        """
    },
    {
        "id": 4,
        "title": "The Golden Orchard Season: Guide to 7 Heritage Apple Varieties",
        "category": "Seasonal Produce",
        "date": "August 19, 2026",
        "read_time": "4 min read",
        "author": "Claire Ward (Orchard Caretaker)",
        "image": "https://images.unsplash.com/photo-1568702846914-96b305d2aaeb?auto=format&fit=crop&w=800&q=80",
        "summary": "Step into our historic high-elevation orchard to discover rare antique apple varieties prized for cider pressing, baking, and crisp afternoon snacking.",
        "content": """
Unlike grocery store apples bred primarily for shelf longevity and thick skins, our heritage orchard is home to century-old trees bursting with complex flavors.

From the crisp champagne notes of our Honeycrisp to the buttery, pie-ready spice of Northern Spy and the pink-fleshed tartness of Hidden Rose, autumn is our most sensory season. In this guide, we break down how to pair each variety with cheeses, ciders, and slow autumn roasts.
        """
    }
]

TESTIMONIALS = [
    {
        "name": "Evelyn Montgomery",
        "role": "CSA Member for 4 Years",
        "location": "Oak Valley",
        "rating": 5,
        "comment": "The difference between grocery store greens and Verdant Heritage produce is astonishing. Their heirloom tomatoes taste like sunshine and honest earth. My kids now ask for raw baby carrots as afternoon snacks!",
        "avatar": "https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=200&q=80"
    },
    {
        "name": "Marcus & Daniel Chen",
        "role": "Farm Visit Guests & Chefs",
        "location": "Riverton",
        "rating": 5,
        "comment": "We booked the Sunset Orchard Tasting for our anniversary and it exceeded every expectation. Sitting beneath the lanterns with freshly pressed cider and wood-fired sourdough was pure magic. Thomas and Claire are inspiring stewards of the land.",
        "avatar": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80"
    },
    {
        "name": "Sophia Al-Mansoor",
        "role": "Weekly Family Box Subscriber",
        "location": "Highland Park",
        "rating": 5,
        "comment": "Switching to their weekly farm box transformed the way our household cooks. The produce arrives crisp, clean, and bursting with life. Customer service is warm, genuine, and accommodating when we need to pause for travel.",
        "avatar": "https://images.unsplash.com/photo-1544005313-94ddf0286df2?auto=format&fit=crop&w=200&q=80"
    }
]

FAQS = [
    {
        "question": "How does your produce delivery work and what are the delivery zones?",
        "answer": "We harvest produce in the morning and dispatch directly in temperature-monitored, eco-friendly totes. We deliver within a 45-mile radius of the farm every Tuesday, Thursday, and Saturday. Free delivery is automatically applied to all orders over $35 or active CSA subscribers."
    },
    {
        "question": "Are your crops 100% certified organic and non-GMO?",
        "answer": "Yes! All 350 acres of Verdant Heritage Farm are certified USDA Organic and Biodynamic. We never use synthetic pesticides, chemical herbicides, artificial fertilizers, or genetically modified seeds. Our pest management relies on beneficial insects, companion planting, and healthy soil biodiversity."
    },
    {
        "question": "Can I pause or customize my CSA subscription box?",
        "answer": "Absolutely. You can log into your Account Dashboard at any time to pause deliveries for vacations, skip a specific week, or change your delivery address with 48 hours notice before your scheduled harvest day."
    },
    {
        "question": "How do farm visits work, and are children welcome?",
        "answer": "Families and guests of all ages are warmly welcomed! We have guided walking tours, tractor wagon rides, and hands-on harvester experiences. Sensible closed-toe shoes and hats are recommended. We provide shaded rest areas, water stations, and stroller-friendly primary paths."
    },
    {
        "question": "What if an item in my delivery arrives damaged or is missing?",
        "answer": "We back every harvest with our 100% Farm Fresh Guarantee. If anything doesn't meet your highest standards, simply message us through your Account or Contact page, and we will issue an immediate replacement or full refund with no questions asked."
    }
]

FARM_STATS = [
    {"label": "Certified Organic Acres", "value": "350+"},
    {"label": "Heirloom Crop Varieties", "value": "120+"},
    {"label": "Local Families Nourished", "value": "18,500+"},
    {"label": "Solar Energy Powered", "value": "100%"},
    {"label": "Years of Farming Heritage", "value": "78"}
]
