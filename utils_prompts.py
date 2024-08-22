MODIFIERS_SITUATIONS = [
    "in einer Stadt",
    "im Büro",
    "bei der Arbeit",
    "auf der Baustelle",
    "im Radio",
    "im Fernsehen",
    "in Zürich",
    "auf einem Bauernhof",
    "auf einem Schiff",
    "in der Schule",
    "in der Universität",
    "in der Bibliothek",
    "in der Bar",
    "in der Disco",
    "im Kindergarten",
    "im Altersheim",
    "im Krankenhaus",
    "im Hotel",
    "im Restaurant",
    "im Flugzeug",
    "im Zug",
    "im Bus",
    "im Auto",
    "im Taxi",
    "im Park",
    "im Wald",
    "im Garten",
    "im Schwimmbad",
    "im Meer",
    "im See",
    "im Fluss",
    "im Stadion",
    "im Museum",
    "im Kino",
    "im Theater",
    "im Konzert",
    "im Supermarkt",
    "im Geschäft",
    "im Kaufhaus",
    "mit einem Freund",
    "mit einer Freundin",
    "mit einem Haustier",
    "mit einem Spielzeug",
    "mit einem Computer",
    "mit einem Fussball",
    "mit einem Buch",
    "mit einer Politikerin",
    "mit einem Schauspieler",
    "mit einem Musiker",
    "mit einer Beamtin",
]

BASE_PROMPT_SITUATIONS = """Beschreibe kurz eine alltägliche Situation {prompt}.
Erstelle 6 verschiedene Sprachversionen von CEFR A1 bis C2.
Gib das Ergebnis in XML Tags aus:

<A1>...</A1>
<A2>...</A2>
<B1>...</B1>
<B2>...</B2>
<C1>...</C1>
<C2>...</C2>

Nutze ausschliesslich diese Tags. Gib das Ergebnis innerhalb dieser Tags als reinen Text aus, ohne jegliche weiteren Tags.
Schreibe immer sieben deutsche Sätze pro Sprachniveau.
Gib nur das Ergebnis in Tags aus, ohne jeglichen weiteren Text."""


MODIFIERS_TOPICS = [
    "Mathematik",
    "Deutsch",
    "Englisch",
    "Französisch",
    "Biologie",
    "Chemie",
    "Physik",
    "Geschichte",
    "Geographie",
    "Politik",
    "Wirtschaft",
    "Kunst",
    "Musik",
    "Sport",
    "Informatik",
    "Ethik",
    "Religion",
    "Soziologie",
    "Technik",
    "Hauswirtschaft",
]

BASE_PROMPT_TOPICS = """Beschreibe detailliert das Schulfach {prompt}.
Erstelle 6 verschiedene Sprachversionen von CEFR A1 bis C2.
Gib das Ergebnis in XML Tags aus:

<A1>...</A1>
<A2>...</A2>
<B1>...</B1>
<B2>...</B2>
<C1>...</C1>
<C2>...</C2>

Nutze ausschliesslich diese Tags. Gib das Ergebnis innerhalb dieser Tags als reinen Text aus, ohne jegliche weiteren Tags.
Schreibe immer 10 deutsche Sätze pro Sprachniveau.
Gib nur das Ergebnis in Tags aus, ohne jeglichen weiteren Text."""


MODIFIERS_SWISS = [
    "Bundesrat",
    "Bundesversammlung",
    "Nationalrat",
    "Ständerat",
    "Landsgemeinde",
    "Kanton",
    "Gemeinde",
    "Föderalismus",
    "Direkte Demokratie",
    "Referendum",
    "Initiative",
    "Verfassung",
    "Gesetz",
    "Verordnungen",
    "Staatsrecht",
    "Justiz",
    "Bundesgericht",
    "Kantonale Gerichtsbarkeit",
    "Exekutive",
    "Legislative",
    "Judikative",
    "Regierungsrat",
    "Kantonsrat",
    "Minderheitenschutz",
    "Volksabstimmung",
    "Kantonsverfassung",
    "Eidgenossenschaft",
    "Schweizerische Eidgenossenschaft",
    "Aussenpolitik",
    "Neutralität",
    "Milizsystem",
    "Wahlrecht",
    "Parteien",
    "Koalition",
    "Opposition",
    "Verwaltung",
    "Öffentliches Recht",
    "Privatrecht",
    "Bürgerrechte",
    "Freiheitsrechte",
    "Sozialpolitik",
    "Bildungspolitik",
    "Finanzpolitik",
    "Steuerrecht",
    "Länderabkommen",
    "Schuldenbremse",
    "Staatsbudget",
    "Föderale Kompetenzverteilung",
    "Vernehmlassungsverahren",
    "Konkordanz",
]

BASE_PROMPT_SWISS = """Beschreibe detailliert den Begriff: {prompt}.
Erstelle 6 verschiedene Sprachversionen von CEFR A1 bis C2.
Gib das Ergebnis in XML Tags aus:

<A1>...</A1>
<A2>...</A2>
<B1>...</B1>
<B2>...</B2>
<C1>...</C1>
<C2>...</C2>

Nutze ausschliesslich diese Tags. Gib das Ergebnis innerhalb dieser Tags als reinen Text aus, ohne jegliche weiteren Tags.
Schreibe immer 10 deutsche Sätze pro Sprachniveau.
Gib nur das Ergebnis aus, ohne jeglichen weiteren Text."""
