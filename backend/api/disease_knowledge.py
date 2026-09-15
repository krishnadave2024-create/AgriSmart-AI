"""
Disease Knowledge Base
======================
Authoritative disease information for each supported class.
This file is the single source of truth — used by the backend.
Never attach disease knowledge to uncertain or unsupported predictions.

Source: PlantVillage class taxonomy + FAO/USDA disease guides
"""

# Maps class_label (from model) → knowledge dict
# class_label format: Crop___Disease (matches model/dataset.py CLASS_TAXONOMY)

DISEASE_KNOWLEDGE_BASE = {

    # ── TOMATO ─────────────────────────────────────────────────────────────
    "Tomato___Bacterial_spot": {
        "crop": "Tomato",
        "disease_name": "Bacterial Spot",
        "pathogen": "Xanthomonas campestris pv. vesicatoria",
        "symptoms": [
            "Small, water-soaked, greasy-looking spots on leaves, stems, and fruit",
            "Spots enlarge and turn brown/black with yellow halos",
            "Severe infection causes defoliation and reduced yield",
        ],
        "causes": [
            "Bacterial infection spread by rain splash, wind, and contaminated tools",
            "Favoured by warm (24–30°C), wet weather",
        ],
        "prevention": [
            "Use disease-free certified seeds and transplants",
            "Avoid overhead irrigation — use drip or furrow",
            "Practice 2–3 year crop rotation with non-solanaceous crops",
            "Sanitise tools and equipment between uses",
        ],
        "management": [
            "Apply copper-based bactericides (copper hydroxide) at first sign of infection",
            "Remove and destroy severely infected plant debris",
            "Consult a local agronomist before applying any pesticide",
        ],
        "expert_note": "Copper resistance is increasingly common. Consult your local agricultural extension officer for current recommendations.",
        "sources": ["FAO Plant Production Guide", "USDA Plant Disease Handbook"],
    },

    "Tomato___Early_blight": {
        "crop": "Tomato",
        "disease_name": "Early Blight",
        "pathogen": "Alternaria solani",
        "symptoms": [
            "Dark brown spots with concentric rings (target-board pattern) on older leaves",
            "Yellow halo surrounding dark spots",
            "Lesions on stems appear as dark, slightly sunken areas",
            "Fruit develops dark, leathery, sunken lesions near the stem end",
        ],
        "causes": [
            "Fungal pathogen that overwinters in infected debris",
            "Spreads by air and water; favoured by warm, humid conditions (24–29°C)",
            "Older or stressed plants are most susceptible",
        ],
        "prevention": [
            "Plant in well-drained soil with good air circulation",
            "Avoid wetting foliage when watering",
            "Remove and destroy infected leaves promptly",
            "Rotate crops to prevent pathogen buildup in soil",
        ],
        "management": [
            "Apply fungicides (chlorothalonil, mancozeb, or copper-based) preventively",
            "Start applications when conditions favour disease development",
            "Ensure adequate plant nutrition — nitrogen deficiency increases susceptibility",
        ],
        "expert_note": "Regular fungicide applications on a 7–10 day schedule are typically needed during wet weather.",
        "sources": ["Cornell University Plant Disease Diagnostic Clinic", "ICAR Tomato Disease Guide"],
    },

    "Tomato___Late_blight": {
        "crop": "Tomato",
        "disease_name": "Late Blight",
        "pathogen": "Phytophthora infestans",
        "symptoms": [
            "Large, irregular, water-soaked, pale green to brown lesions on leaves",
            "White mould (sporangia) visible on leaf undersides in humid conditions",
            "Brown or black lesions on stems and petioles",
            "Infected fruit turns brown, firm, and leathery",
        ],
        "causes": [
            "Oomycete pathogen — same pathogen that caused the Irish Potato Famine",
            "Spreads rapidly in cool (10–20°C), wet, foggy conditions",
            "Can destroy a crop within days under ideal disease conditions",
        ],
        "prevention": [
            "Use resistant varieties where available",
            "Avoid overhead irrigation",
            "Ensure good field drainage",
            "Monitor weather forecasts — apply fungicides before forecasted wet periods",
        ],
        "management": [
            "Metalaxyl or mancozeb-based fungicides are effective if applied early",
            "Destroy infected plant material — do not compost",
            "Remove volunteer plants from surrounding areas",
        ],
        "expert_note": "Late blight is extremely destructive. Immediate consultation with an agricultural expert is strongly recommended.",
        "sources": ["American Phytopathological Society", "FAO Emergency Disease Response"],
    },

    "Tomato___Leaf_Mold": {
        "crop": "Tomato",
        "disease_name": "Leaf Mold",
        "pathogen": "Passalora fulva (formerly Fulvia fulva)",
        "symptoms": [
            "Pale greenish-yellow spots on upper leaf surface",
            "Olive-green to brown, velvety mould on lower leaf surface",
            "Affected leaves may curl and wither; severe infection causes defoliation",
        ],
        "causes": [
            "Fungal disease; favoured by high humidity (>85%) and moderate temperatures (20–25°C)",
            "Common in greenhouse tomatoes due to poor ventilation",
        ],
        "prevention": [
            "Ensure good ventilation in greenhouses and tunnels",
            "Avoid excessive moisture on foliage",
            "Use resistant varieties where available",
        ],
        "management": [
            "Apply fungicides (copper-based, chlorothalonil) at first symptom appearance",
            "Improve air circulation around plants",
            "Remove infected leaves carefully to avoid spreading spores",
        ],
        "expert_note": "Most severe in protected cultivation. Outdoor crops rarely suffer serious losses.",
        "sources": ["UC Davis Plant Pathology", "TNAU Agritech Portal"],
    },

    "Tomato___Septoria_leaf_spot": {
        "crop": "Tomato",
        "disease_name": "Septoria Leaf Spot",
        "pathogen": "Septoria lycopersici",
        "symptoms": [
            "Numerous small, circular spots (3–6 mm) with dark borders and grey/tan centres",
            "Tiny black specks (pycnidia) visible in spot centres under magnification",
            "Begins on lower older leaves; moves upward with disease progression",
            "Severe infection causes complete leaf yellowing and drop",
        ],
        "causes": [
            "Fungal disease; spread by water splash from infected soil or plant debris",
            "Favoured by warm (20–25°C), wet, humid weather",
        ],
        "prevention": [
            "Rotate crops — pathogen survives in soil on tomato debris",
            "Use staked plants for better air circulation",
            "Mulch soil to reduce splash dispersal",
            "Avoid working with plants when wet",
        ],
        "management": [
            "Apply protective fungicides (chlorothalonil, mancozeb) preventively",
            "Remove and destroy fallen infected leaves",
        ],
        "expert_note": "One of the most common tomato foliar diseases in warm, humid regions.",
        "sources": ["Penn State Extension", "ICAR"],
    },

    "Tomato___Spider_mites": {
        "crop": "Tomato",
        "disease_name": "Spider Mites (Two-spotted)",
        "pathogen": "Tetranychus urticae (pest — not a fungal disease)",
        "symptoms": [
            "Fine stippling (tiny yellow or white dots) on upper leaf surface",
            "Leaves turn bronze, yellow, or brown; may curl and drop",
            "Fine webbing visible on underside of leaves in heavy infestations",
            "Tiny moving dots (mites) visible with a hand lens",
        ],
        "causes": [
            "Spider mites are arachnids (not insects or fungi)",
            "Thrive in hot (>28°C), dry, dusty conditions",
            "Populations explode rapidly; one generation per 1–2 weeks in summer",
        ],
        "prevention": [
            "Maintain adequate soil moisture — water stress increases mite susceptibility",
            "Avoid excessive nitrogen fertilisation (promotes lush growth that mites favour)",
            "Conserve natural predators (ladybirds, predatory mites) — avoid broad-spectrum insecticides",
        ],
        "management": [
            "Spray plants with water to reduce mite numbers",
            "Use miticides (abamectin, bifenazate) if population is high",
            "Introduce predatory mites (Phytoseiidae) for biological control",
        ],
        "expert_note": "Spider mites are a pest, not a disease. Misidentification is common. Confirm with a hand lens before applying pesticides.",
        "sources": ["UC IPM", "CABI Invasive Species Compendium"],
    },

    "Tomato___Target_Spot": {
        "crop": "Tomato",
        "disease_name": "Target Spot",
        "pathogen": "Corynespora cassiicola",
        "symptoms": [
            "Dark brown lesions with concentric rings (target pattern) on leaves",
            "Yellow halo surrounds lesions",
            "Lesions on fruit are sunken with dark centres",
        ],
        "causes": [
            "Fungal pathogen; favoured by warm, humid conditions",
            "Spread by wind and water splash from infected crop debris",
        ],
        "prevention": [
            "Remove and destroy infected plant material",
            "Practise crop rotation",
            "Improve air circulation and avoid overhead irrigation",
        ],
        "management": [
            "Apply fungicides (azoxystrobin, tebuconazole) at first symptom",
            "Ensure good plant nutrition",
        ],
        "expert_note": "Often confused with early blight — examine lesion pattern carefully or consult an agronomist.",
        "sources": ["CABI", "FAO"],
    },

    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": {
        "crop": "Tomato",
        "disease_name": "Tomato Yellow Leaf Curl Virus (TYLCV)",
        "pathogen": "Tomato yellow leaf curl virus — transmitted by whitefly (Bemisia tabaci)",
        "symptoms": [
            "Young leaves curl upward and inward, becoming cup-shaped",
            "Leaves turn yellow (chlorotic) at margins",
            "Plants become stunted; fruit set is severely reduced",
            "Diseased plants show compact, bushy appearance",
        ],
        "causes": [
            "Caused by a geminivirus transmitted persistently by silverleaf whitefly",
            "No plant-to-plant transmission without the whitefly vector",
            "Virus can spread rapidly when whitefly populations are high",
        ],
        "prevention": [
            "Use TYLCV-resistant or tolerant tomato varieties",
            "Use reflective mulches to deter whiteflies",
            "Install insect-proof netting in nurseries",
            "Apply systemic insecticides to control whitefly populations early",
        ],
        "management": [
            "No cure for infected plants — remove and destroy infected plants promptly",
            "Control whitefly vector with neonicotinoids or insect growth regulators",
            "Maintain good weed management around fields (reservoir hosts)",
        ],
        "expert_note": "One of the most economically important tomato diseases in tropical/subtropical regions including India. Prevention is critical — there is no curative treatment.",
        "sources": ["AVRDC WorldVeg", "ICAR", "FAO"],
    },

    "Tomato___Tomato_mosaic_virus": {
        "crop": "Tomato",
        "disease_name": "Tomato Mosaic Virus (ToMV)",
        "pathogen": "Tomato mosaic virus (genus Tobamovirus)",
        "symptoms": [
            "Mosaic pattern of light and dark green on leaves",
            "Leaves may be distorted, blistered, or show fern-leaf appearance",
            "Fruits show uneven ripening and internal browning",
            "Infected plants may be stunted",
        ],
        "causes": [
            "Mechanically transmitted via infected plant sap (tools, hands)",
            "Also spread by contact between plants",
            "NOT transmitted by insects; extremely stable and long-lived in soil",
        ],
        "prevention": [
            "Use virus-indexed, certified disease-free seed",
            "Disinfect tools with 10% bleach solution or 70% alcohol between uses",
            "Wash hands thoroughly when working with tomato plants",
            "Avoid using tobacco products near tomato plants (related virus)",
        ],
        "management": [
            "No curative treatment — remove and destroy infected plants immediately",
            "Do not compost infected material",
        ],
        "expert_note": "Extremely persistent in soil and on surfaces. Strict hygiene practices are the only effective management strategy.",
        "sources": ["Cornell PlantClinic", "CABI"],
    },

    "Tomato___healthy": {
        "crop": "Tomato",
        "disease_name": None,
        "symptoms": [],
        "causes": [],
        "prevention": [
            "Continue regular monitoring — inspect plants 2–3 times per week",
            "Maintain balanced fertilisation (balanced NPK)",
            "Use drip irrigation to reduce foliar wetness",
            "Keep field free of weeds and crop debris",
            "Scout for early signs of pest or disease activity",
        ],
        "management": [],
        "expert_note": "The plant appears healthy. Maintain current practices and monitor regularly.",
        "sources": [],
    },

    # ── CORN / MAIZE ────────────────────────────────────────────────────────
    "Corn___Gray_leaf_spot": {
        "crop": "Corn/Maize",
        "disease_name": "Gray Leaf Spot (Cercospora Leaf Spot)",
        "pathogen": "Cercospora zeae-maydis",
        "symptoms": [
            "Long, rectangular, tan to grey lesions running parallel to leaf veins",
            "Lesions have distinct parallel edges bounded by leaf veins",
            "Severe infection causes large areas of leaf to turn grey and die",
        ],
        "causes": [
            "Fungal pathogen; survives on infected corn debris",
            "Favoured by warm (25–30°C), humid conditions with extended leaf wetness",
            "Continuous corn production increases disease pressure",
        ],
        "prevention": [
            "Rotate with non-host crops (soybean, wheat)",
            "Bury or remove crop debris after harvest",
            "Plant resistant hybrid varieties",
        ],
        "management": [
            "Apply foliar fungicides (triazoles, strobilurins) at early disease stages",
            "Consult local recommendations for timing and product selection",
        ],
        "expert_note": "One of the most significant maize diseases in India, particularly in high-altitude and humid regions.",
        "sources": ["CIMMYT", "ICAR", "FAO"],
    },

    "Corn___Common_rust": {
        "crop": "Corn/Maize",
        "disease_name": "Common Rust",
        "pathogen": "Puccinia sorghi",
        "symptoms": [
            "Oval to elongate, brick-red to brown powdery pustules on both leaf surfaces",
            "Pustules rupture, releasing rusty-coloured spores",
            "Severely infected leaves turn yellow and die prematurely",
        ],
        "causes": [
            "Airborne fungal spores (urediniospores) from overwintering sources",
            "Favoured by cool (16–23°C), humid, cloudy weather",
            "Wind-dispersed — can travel long distances",
        ],
        "prevention": [
            "Plant rust-resistant varieties — most modern hybrids have moderate resistance",
            "Early planting to avoid peak infection periods",
        ],
        "management": [
            "Fungicide application (triazoles) is rarely needed except on susceptible varieties",
            "Economic threshold: spray when 50%+ of plants show pustules on upper leaves before silking",
        ],
        "expert_note": "Most commercial hybrids in India have adequate rust resistance. Confirm variety susceptibility with your seed supplier.",
        "sources": ["CIMMYT", "Purdue Plant Disease Management"],
    },

    "Corn___Northern_Leaf_Blight": {
        "crop": "Corn/Maize",
        "disease_name": "Northern Leaf Blight (NLB)",
        "pathogen": "Exserohilum turcicum (formerly Helminthosporium turcicum)",
        "symptoms": [
            "Long, elliptical, cigar-shaped grey-green to tan lesions (2.5–15 cm long)",
            "Lesions appear first on lower leaves and move upward",
            "Severely affected plants produce poor, lightweight grain",
        ],
        "causes": [
            "Fungal pathogen; overwinters on infected corn debris",
            "Favoured by moderate temperatures (18–27°C) and high humidity",
        ],
        "prevention": [
            "Plant resistant hybrid varieties — the most effective management",
            "Crop rotation and debris management reduce initial inoculum",
        ],
        "management": [
            "Fungicides (strobilurins + triazole mixtures) applied at silking are most effective on susceptible hybrids",
            "Economic threshold: 50%+ plants show lesions on the ear leaf or above at tasseling",
        ],
        "expert_note": "Timing is critical — fungicide applications must be made before disease reaches the ear leaf.",
        "sources": ["CIMMYT", "University of Wisconsin Extension"],
    },

    "Corn___healthy": {
        "crop": "Corn/Maize",
        "disease_name": None,
        "symptoms": [],
        "causes": [],
        "prevention": [
            "Scout fields regularly, especially during silking and grain fill",
            "Maintain balanced soil fertility",
            "Monitor for common pests (aphids, stem borers, armyworm)",
        ],
        "management": [],
        "expert_note": "The plant appears healthy. Continue regular monitoring and maintain good crop management practices.",
        "sources": [],
    },

    # ── POTATO ──────────────────────────────────────────────────────────────
    "Potato___Early_blight": {
        "crop": "Potato",
        "disease_name": "Early Blight",
        "pathogen": "Alternaria solani",
        "symptoms": [
            "Dark brown spots with concentric rings (bullseye pattern) on leaves",
            "Yellow area surrounds lesions",
            "Begins on older lower leaves; progresses upward",
            "Severe infection causes premature defoliation",
        ],
        "causes": [
            "Fungal pathogen; survives on infected debris and in soil",
            "Favoured by alternating wet and dry weather (22–26°C)",
            "Stressed or nutrient-deficient plants are most susceptible",
        ],
        "prevention": [
            "Use certified disease-free seed tubers",
            "Maintain adequate nitrogen, phosphorus and potassium levels",
            "Practice crop rotation (3–4 years)",
            "Avoid overhead irrigation",
        ],
        "management": [
            "Apply fungicides (mancozeb, chlorothalonil) preventively",
            "Begin at crop emergence and repeat on 7–10 day schedule",
        ],
        "expert_note": "Early blight is widespread and difficult to eliminate. Fungicide programmes combined with good cultural practices give best results.",
        "sources": ["CPRI Shimla", "FAO", "ICAR"],
    },

    "Potato___Late_blight": {
        "crop": "Potato",
        "disease_name": "Late Blight",
        "pathogen": "Phytophthora infestans",
        "symptoms": [
            "Large, irregular, water-soaked lesions turning brown/black on leaves",
            "White sporangiophores (mould) on underside of lesions in humid conditions",
            "Infected tubers show brown-grey rot beneath the skin",
            "Entire field can be destroyed within 7–10 days in severe outbreaks",
        ],
        "causes": [
            "Oomycete (water mould) pathogen — extremely destructive",
            "Favoured by cool (10–20°C), wet, foggy conditions",
        ],
        "prevention": [
            "Plant certified disease-free or resistant varieties",
            "Ensure good field drainage",
            "Monitor forecasting systems (BLITECAST, field forecasts)",
            "Apply preventive fungicides before wet periods",
        ],
        "management": [
            "Metalaxyl, cymoxanil, or mancozeb-based fungicides — apply before infection",
            "Destroy infected haulms (stems) before harvest to protect tubers",
            "Do not harvest during wet conditions",
        ],
        "expert_note": "Late blight is the most feared potato disease. Immediate expert consultation is strongly advised if late blight is suspected. Do not delay treatment.",
        "sources": ["CPRI Shimla", "CIP International Potato Center", "FAO"],
    },

    "Potato___healthy": {
        "crop": "Potato",
        "disease_name": None,
        "symptoms": [],
        "causes": [],
        "prevention": [
            "Scout weekly, checking both upper and lower leaf surfaces",
            "Maintain balanced fertilisation and optimal soil moisture",
            "Monitor weather and apply preventive fungicides before high-risk periods",
        ],
        "management": [],
        "expert_note": "The plant appears healthy. Continue monitoring and maintain current crop management practices.",
        "sources": [],
    },

    # ── PEPPER ──────────────────────────────────────────────────────────────
    "Pepper___Bacterial_spot": {
        "crop": "Pepper (Bell)",
        "disease_name": "Bacterial Spot",
        "pathogen": "Xanthomonas campestris pv. vesicatoria",
        "symptoms": [
            "Small, water-soaked, greasy spots on leaves and fruit",
            "Spots turn dark brown to black with yellow halos on leaves",
            "Fruit spots are slightly raised; later become sunken and scabby",
            "Defoliation in severe cases reduces fruit set and quality",
        ],
        "causes": [
            "Bacterial infection; spread by rain splash, contaminated tools, infected seed",
            "Favoured by warm (24–30°C), wet conditions",
        ],
        "prevention": [
            "Use certified disease-free seed",
            "Avoid overhead irrigation",
            "Practice crop rotation",
            "Sanitise tools between plants",
        ],
        "management": [
            "Apply copper-based bactericides (copper hydroxide, copper sulphate) preventively",
            "Combine with mancozeb to improve copper adhesion",
            "Remove severely infected plants from the field",
        ],
        "expert_note": "Copper resistance has been documented in bacterial spot pathogens. Monitor effectiveness and consult local extension services.",
        "sources": ["University of Florida IFAS", "ICAR"],
    },

    "Pepper___healthy": {
        "crop": "Pepper (Bell)",
        "disease_name": None,
        "symptoms": [],
        "causes": [],
        "prevention": [
            "Scout regularly for early signs of pests and diseases",
            "Maintain optimal soil moisture and avoid waterlogging",
            "Ensure adequate calcium nutrition to prevent blossom-end rot",
        ],
        "management": [],
        "expert_note": "The plant appears healthy. Continue regular monitoring.",
        "sources": [],
    },
}

# ── Supported Crop Registry ────────────────────────────────────────────────
SUPPORTED_CROPS_INFO = {
    "Tomato": {
        "diseases": [
            "Bacterial Spot", "Early Blight", "Late Blight", "Leaf Mold",
            "Septoria Leaf Spot", "Spider Mites", "Target Spot",
            "Yellow Leaf Curl Virus", "Mosaic Virus"
        ],
        "model_support": "full",
        "dataset": "PlantVillage (CC-BY-SA 3.0)",
    },
    "Corn/Maize": {
        "diseases": ["Gray Leaf Spot", "Common Rust", "Northern Leaf Blight"],
        "model_support": "full",
        "dataset": "PlantVillage (CC-BY-SA 3.0)",
    },
    "Potato": {
        "diseases": ["Early Blight", "Late Blight"],
        "model_support": "full",
        "dataset": "PlantVillage (CC-BY-SA 3.0)",
    },
    "Pepper (Bell)": {
        "diseases": ["Bacterial Spot"],
        "model_support": "full",
        "dataset": "PlantVillage (CC-BY-SA 3.0)",
    },
}

UNSUPPORTED_CROPS = [
    "Cotton", "Rice", "Wheat", "Millet", "Soybean",
    "Sugarcane", "Groundnut", "Sunflower", "Barley"
]
