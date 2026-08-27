# ==========================================
# PLANT DISEASE TREATMENT DATABASE
# ==========================================

TREATMENT_RECOMMENDATIONS = {

    # --------------------------------------
    # PEPPER
    # --------------------------------------

    "Pepper__bell___Bacterial_spot": {

        "plant": "Bell Pepper",

        "condition": "Bacterial Spot",

        "type": "Bacterial disease",

        "pathogen": "Xanthomonas species",

        "treatment_type": "Bactericide / Disease management",

        "active_ingredients": [
            "Copper hydroxide",
            "Fixed copper compounds"
        ],

        "target": "Bacterial spot",

        "chemical_guidance": (
            "Copper-based products may provide protective suppression "
            "of bacterial spot. Effectiveness can vary because copper "
            "resistance occurs in some bacterial populations."
        ),

        "non_chemical": [
            "Remove severely affected plant material.",
            "Avoid overhead irrigation.",
            "Improve air circulation.",
            "Avoid handling plants when foliage is wet.",
            "Sanitize tools after working with infected plants."
        ],

        "warning": (
            "Use only a product registered/labeled for pepper and "
            "bacterial spot in your region. Follow the product label."
        )
    },


    "Pepper__bell___healthy": {

        "plant": "Bell Pepper",

        "condition": "Healthy",

        "type": "No disease detected",

        "pathogen": "None detected",

        "treatment_type": "No pesticide recommended",

        "active_ingredients": [],

        "target": "None",

        "chemical_guidance": (
            "No chemical treatment is recommended when the plant "
            "is classified as healthy."
        ),

        "non_chemical": [
            "Continue regular plant monitoring.",
            "Maintain appropriate watering.",
            "Maintain adequate nutrition.",
            "Keep the growing area clean."
        ],

        "warning": (
            "A healthy classification does not guarantee that the "
            "plant is completely free of pests or diseases."
        )
    },


    # --------------------------------------
    # POTATO
    # --------------------------------------

    "Potato___Early_blight": {

        "plant": "Potato",

        "condition": "Early Blight",

        "type": "Fungal disease",

        "pathogen": "Alternaria solani",

        "treatment_type": "Fungicide",

        "active_ingredients": [
            "Chlorothalonil",
            "Mancozeb",
            "Copper-based fungicides"
        ],

        "target": "Early blight",

        "chemical_guidance": (
            "Fungicide programs can be used for early blight management. "
            "Different fungicide groups should be rotated where appropriate "
            "to reduce resistance development."
        ),

        "non_chemical": [
            "Remove severely infected leaves.",
            "Avoid prolonged leaf wetness.",
            "Water at the soil level.",
            "Improve plant spacing and airflow.",
            "Remove infected plant debris."
        ],

        "warning": (
            "Use only products labeled for potato and early blight "
            "in your region. Follow label rate, protective-equipment, "
            "re-entry and harvest requirements."
        )
    },


    "Potato___Late_blight": {

        "plant": "Potato",

        "condition": "Late Blight",

        "type": "Water mold disease",

        "pathogen": "Phytophthora infestans",

        "treatment_type": "Late-blight fungicide",

        "active_ingredients": [
            "Mefenoxam / metalaxyl-based products",
            "Mandipropamid",
            "Cyazofamid",
            "Cymoxanil"
        ],

        "target": "Phytophthora infestans",

        "chemical_guidance": (
            "Late blight requires fungicides specifically effective "
            "against water molds. Preventive applications are generally "
            "more effective than waiting until severe infection develops."
        ),

        "non_chemical": [
            "Remove severely infected plants where practical.",
            "Use certified disease-free seed potatoes.",
            "Remove volunteer potato plants.",
            "Destroy infected plant material.",
            "Avoid prolonged leaf wetness."
        ],

        "warning": (
            "Active ingredients and permitted uses vary by country and "
            "product. Verify that the product label specifically lists "
            "potato and late blight before use."
        )
    },


    "Potato___healthy": {

        "plant": "Potato",

        "condition": "Healthy",

        "type": "No disease detected",

        "pathogen": "None detected",

        "treatment_type": "No pesticide recommended",

        "active_ingredients": [],

        "target": "None",

        "chemical_guidance": (
            "No chemical treatment is recommended for a plant "
            "classified as healthy."
        ),

        "non_chemical": [
            "Continue regular monitoring.",
            "Maintain proper irrigation.",
            "Use healthy planting material.",
            "Maintain field sanitation."
        ],

        "warning": (
            "The AI classification is not a guarantee that the "
            "plant is completely disease-free."
        )
    },


    # --------------------------------------
    # TOMATO
    # --------------------------------------

    "Tomato_Bacterial_spot": {

        "plant": "Tomato",

        "condition": "Bacterial Spot",

        "type": "Bacterial disease",

        "pathogen": "Xanthomonas species",

        "treatment_type": "Bactericide / Disease management",

        "active_ingredients": [
            "Copper hydroxide",
            "Fixed copper compounds"
        ],

        "target": "Bacterial spot",

        "chemical_guidance": (
            "Copper-based bactericidal products may provide protective "
            "suppression. Copper resistance may reduce effectiveness "
            "in some populations."
        ),

        "non_chemical": [
            "Remove affected leaves when practical.",
            "Avoid overhead irrigation.",
            "Keep foliage dry.",
            "Improve plant spacing.",
            "Sanitize tools."
        ],

        "warning": (
            "Use only products labeled for tomato and bacterial spot "
            "in your region. Follow all label instructions."
        )
    },


    "Tomato_Early_blight": {

        "plant": "Tomato",

        "condition": "Early Blight",

        "type": "Fungal disease",

        "pathogen": "Alternaria tomatophila / Alternaria solani",

        "treatment_type": "Fungicide",

        "active_ingredients": [
            "Chlorothalonil",
            "Mancozeb",
            "Copper-based fungicides"
        ],

        "target": "Early blight",

        "chemical_guidance": (
            "Fungicides can be used when disease pressure warrants "
            "chemical management. Rotate fungicide groups according "
            "to local recommendations to reduce resistance risk."
        ),

        "non_chemical": [
            "Remove infected leaves.",
            "Do not remove more than necessary.",
            "Water at the base of the plant.",
            "Improve airflow.",
            "Use mulch to reduce soil splash.",
            "Remove infected debris."
        ],

        "warning": (
            "Verify that the selected product is labeled for tomato "
            "and early blight in your region."
        )
    },


    "Tomato_Late_blight": {

        "plant": "Tomato",

        "condition": "Late Blight",

        "type": "Water mold disease",

        "pathogen": "Phytophthora infestans",

        "treatment_type": "Late-blight fungicide",

        "active_ingredients": [
            "Mefenoxam / metalaxyl-based products",
            "Mandipropamid",
            "Cyazofamid",
            "Cymoxanil"
        ],

        "target": "Phytophthora infestans",

        "chemical_guidance": (
            "Use fungicides specifically registered for late blight. "
            "Applications are generally most effective when started "
            "before severe infection and repeated according to label."
        ),

        "non_chemical": [
            "Remove severely infected plants.",
            "Avoid overhead irrigation.",
            "Improve airflow.",
            "Remove infected plant material.",
            "Monitor nearby plants frequently."
        ],

        "warning": (
            "Late blight can spread rapidly. Verify the product label "
            "for tomato and late blight before applying any chemical."
        )
    },


    "Tomato_Leaf_Mold": {

        "plant": "Tomato",

        "condition": "Tomato Leaf Mold",

        "type": "Fungal disease",

        "pathogen": "Passalora fulva",

        "treatment_type": "Fungicide",

        "active_ingredients": [
            "Copper hydroxide",
            "Other fungicides registered for tomato leaf mold"
        ],

        "target": "Passalora fulva",

        "chemical_guidance": (
            "Copper-based products may provide some control. "
            "Fungicide programs should follow local recommendations "
            "and alternate chemical families where appropriate."
        ),

        "non_chemical": [
            "Reduce humidity.",
            "Improve greenhouse ventilation.",
            "Increase spacing between plants.",
            "Avoid wetting foliage.",
            "Remove infected leaves.",
            "Sanitize greenhouse equipment."
        ],

        "warning": (
            "Check whether the selected formulation is approved "
            "for tomato and the intended growing environment."
        )
    },


    "Tomato_Septoria_leaf_spot": {

        "plant": "Tomato",

        "condition": "Septoria Leaf Spot",

        "type": "Fungal disease",

        "pathogen": "Septoria lycopersici",

        "treatment_type": "Fungicide",

        "active_ingredients": [
            "Chlorothalonil",
            "Mancozeb",
            "Copper-based fungicides"
        ],

        "target": "Septoria leaf spot",

        "chemical_guidance": (
            "Protective fungicides may be used when disease pressure "
            "requires chemical control. Follow local recommendations "
            "and rotate fungicide groups."
        ),

        "non_chemical": [
            "Remove infected lower leaves.",
            "Keep foliage dry.",
            "Water at the base.",
            "Improve airflow.",
            "Remove infected debris.",
            "Rotate crops where practical."
        ],

        "warning": (
            "Use only products labeled for tomato and Septoria leaf "
            "spot in your region."
        )
    },


    "Tomato_Spider_mites_Two_spotted_spider_mite": {

        "plant": "Tomato",

        "condition": "Two-Spotted Spider Mite",

        "type": "Mite pest",

        "pathogen": "Tetranychus urticae",

        "treatment_type": "Miticide / Insecticidal treatment",

        "active_ingredients": [
            "Insecticidal soap",
            "Horticultural oil",
            "Abamectin"
        ],

        "target": "Two-spotted spider mites",

        "chemical_guidance": (
            "Insecticidal soaps and horticultural oils can be used "
            "against mites when properly applied. Crop-specific "
            "miticides such as abamectin may be options where registered."
        ),

        "non_chemical": [
            "Inspect leaf undersides regularly.",
            "Use a strong water spray to dislodge mites.",
            "Reduce plant stress.",
            "Avoid unnecessary broad-spectrum insecticides.",
            "Encourage beneficial predatory organisms where practical."
        ],

        "warning": (
            "Soaps and oils require thorough contact with mites. "
            "Use only products labeled for tomato and spider mites. "
            "Avoid spraying under conditions that increase plant injury."
        )
    },


    "Tomato__Target_Spot": {

        "plant": "Tomato",

        "condition": "Target Spot",

        "type": "Fungal disease",

        "pathogen": "Corynespora cassiicola",

        "treatment_type": "Fungicide",

        "active_ingredients": [
            "Chlorothalonil",
            "Mancozeb",
            "Copper-based fungicides"
        ],

        "target": "Target spot",

        "chemical_guidance": (
            "Use fungicides registered for target spot and tomato "
            "where chemical control is warranted."
        ),

        "non_chemical": [
            "Remove severely affected foliage.",
            "Improve airflow.",
            "Avoid overhead irrigation.",
            "Keep foliage dry.",
            "Remove infected plant debris."
        ],

        "warning": (
            "Verify crop and disease registration on the pesticide label."
        )
    },


    "Tomato__Tomato_YellowLeaf__Curl_Virus": {

        "plant": "Tomato",

        "condition": "Tomato Yellow Leaf Curl Virus",

        "type": "Viral disease",

        "pathogen": "Tomato yellow leaf curl virus",

        "treatment_type": "No direct chemical cure",

        "active_ingredients": [
            "No direct antiviral pesticide"
        ],

        "target": "Virus / whitefly vector management",

        "chemical_guidance": (
            "There is no pesticide that directly cures an already "
            "virus-infected tomato plant. Management should focus on "
            "controlling the insect vector and removing infected plants "
            "where appropriate."
        ),

        "non_chemical": [
            "Remove severely infected plants.",
            "Use healthy planting material.",
            "Monitor whitefly populations.",
            "Use physical barriers where practical.",
            "Control volunteer host plants."
        ],

        "warning": (
            "Insecticide use should target the vector only when "
            "appropriate and must follow local registration and label rules."
        )
    },


    "Tomato__Tomato_mosaic_virus": {

        "plant": "Tomato",

        "condition": "Tomato Mosaic Virus",

        "type": "Viral disease",

        "pathogen": "Tomato mosaic virus",

        "treatment_type": "No direct chemical cure",

        "active_ingredients": [
            "No direct antiviral pesticide"
        ],

        "target": "Virus",

        "chemical_guidance": (
            "There is no direct pesticide cure for an infected plant. "
            "Chemical treatment should not be presented as a cure."
        ),

        "non_chemical": [
            "Remove infected plants where appropriate.",
            "Use clean seed and planting material.",
            "Disinfect tools.",
            "Wash hands after handling infected plants.",
            "Remove infected plant debris."
        ],

        "warning": (
            "Do not apply fungicides or insecticides claiming to cure "
            "the virus itself."
        )
    },


    "Tomato_healthy": {

        "plant": "Tomato",

        "condition": "Healthy",

        "type": "No disease detected",

        "pathogen": "None detected",

        "treatment_type": "No pesticide recommended",

        "active_ingredients": [],

        "target": "None",

        "chemical_guidance": (
            "No pesticide is recommended when the model classifies "
            "the leaf as healthy."
        ),

        "non_chemical": [
            "Continue regular inspection.",
            "Maintain proper irrigation.",
            "Maintain plant nutrition.",
            "Keep the growing area clean."
        ],

        "warning": (
            "The AI result is a screening result and does not guarantee "
            "that the plant is completely free of disease or pests."
        )
    }
}