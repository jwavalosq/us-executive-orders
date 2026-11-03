# Transparent keyword rules. First matching category wins, in the order listed.
# Keywords are matched as substrings in the lowercased title. This is a blunt tool
# on purpose: it is explainable, and its limits are measured in notebook 03.
RULES = [
    ("Emergency and Disaster", ["emergency", "disaster", "hurricane", "flood", "pandemic", "covid", "coronavirus", "earthquake", "drought"]),
    ("Civil Rights and Equality", ["civil rights", "discrimination", "equal employment", "equal opportunity", "desegregat", "segregat", "affirmative action", "women", "disability", "handicap"]),
    ("Immigration and Citizenship", ["immigration", "immigrant", "alien", "citizenship", "naturalization", "border", "visa", "deport", "refugee", "asylum"]),
    ("Defense and Military", ["military", "army", "navy", "air force", "armed forces", "national guard", "defense", "war ", "wartime", "soldier", "naval", "fort ", "arsenal", "militia"]),
    ("Veterans", ["veteran"]),
    ("Foreign Policy and Trade", ["foreign", "tariff", "sanction", "treaty", "ambassador", "international", "import", "export", "embargo", "diplomat"]),
    ("Health and Public Health", ["health", "disease", "medical", "drug", "public health", "hospital", "vaccine", "opioid", "mental health"]),
    ("Environment and Energy", ["environment", "pollution", "energy", "climate", "conservation", "wildlife", "water quality", "clean air", "clean water", "carbon", "oil ", "petroleum", "natural gas"]),
    ("Land and Public Lands", ["land", "reservation", "refuge", "national park", "forest", "public lands", "withdrawal", "homestead", "territory", "indian", "tribal", "tribe"]),
    ("Agriculture and Food", ["agricultur", "farm", "food", "crop", "livestock", "ranch"]),
    ("Education and Science", ["education", "school", "science", "research", "technology", "university", "college", "student"]),
    ("Economy and Finance", ["economic", "finance", "financial", "tax", "budget", "bank", "commerce", "business", "wage", "salary", "pay ", "employment", "labor", "union", "inflation", "price"]),
    ("Transportation and Infrastructure", ["transportation", "railroad", "railway", "highway", "aviation", "aircraft", "postal", "post office", "bridge", "road", "port "]),
    ("Law Enforcement and Justice", ["justice", "crime", "law enforcement", "police", "prison", "pardon", "clemency", "federal bureau", "investigation"]),
    ("Government Administration", ["agency", "department", "committee", "commission", "council", "reorganization", "executive office", "advisory", "board", "administration", "federal service", "civil service", "personnel", "appointment", "office of"]),
]
def categorize(title):
    t = " " + (title or "").lower() + " "
    for cat, kws in RULES:
        for kw in kws:
            if kw in t:
                return cat, kw
    return "Other or General", ""
