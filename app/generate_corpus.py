#!/usr/bin/env python3
"""
Generate 1,500-2,000 word executive leadership documents for all Fortune 500 CEOs
using the OpenAI API (gpt-4o), then write them to app/data/raw/.

Usage:
    python generate_corpus.py                  # generate all missing files
    python generate_corpus.py --dry-run        # print what would be created, no API calls
    python generate_corpus.py --limit 10       # generate first N entries only
    python generate_corpus.py --overwrite      # regenerate even if file already exists
    python generate_corpus.py --start 50       # skip to rank offset (0-indexed)

Requirements:
    pip install openai python-dotenv
    OPENAI_API_KEY must be set in .env or environment.
"""

import argparse
import re
import time
from pathlib import Path

import openai
from dotenv import load_dotenv

load_dotenv()

OUT_DIR = Path(__file__).parent / "app" / "data" / "raw"

# ── Fortune 500 CEO list (2025 ranking) ──────────────────────────────────────
# Format: (rank, company, ceo_name)
FORTUNE_500: list[tuple[int, str, str]] = [
    (1,   "Amazon",                              "Andy Jassy"),
    (2,   "Walmart",                             "John Furner"),
    (3,   "UnitedHealth Group",                  "Stephen Hemsley"),
    (4,   "Apple",                               "Tim Cook"),
    (5,   "Alphabet",                            "Sundar Pichai"),
    (6,   "CVS Health",                          "David Joyner"),
    (7,   "McKesson",                            "Brian Tyler"),
    (8,   "Berkshire Hathaway",                  "Greg Abel"),
    (9,   "Exxon Mobil",                         "Darren Woods"),
    (10,  "Cencora",                             "Robert Mauch"),
    (11,  "Microsoft",                           "Satya Nadella"),
    (12,  "Costco",                              "Ron Vachris"),
    (13,  "Cigna",                               "David Cordani"),
    (14,  "Cardinal Health",                     "Jason Hollar"),
    (15,  "Elevance Health",                     "Gail Boudreaux"),
    (16,  "Ford Motor",                          "Jim Farley"),
    (17,  "Meta",                                "Mark Zuckerberg"),
    (18,  "Chevron",                             "Mike Wirth"),
    (19,  "General Motors",                      "Mary Barra"),
    (20,  "Nvidia",                              "Jensen Huang"),
    (21,  "Centene",                             "Sarah London"),
    (22,  "JPMorgan Chase",                      "Jamie Dimon"),
    (23,  "Home Depot",                          "Edward Decker"),
    (24,  "Walgreens Boots Alliance",            "Tim Wentworth"),
    (25,  "Fannie Mae",                          "Priscilla Almodovar"),
    (26,  "Kroger",                              "Ron Sargent"),
    (27,  "Verizon",                             "Hans Vestberg"),
    (28,  "Marathon Petroleum",                  "Maryann Mannen"),
    (29,  "Phillips 66",                         "Mark Lashier"),
    (30,  "StoneX Group",                        "Philip Smith"),
    (31,  "Humana",                              "Jim Rechtin"),
    (32,  "AT&T",                                "John Stankey"),
    (33,  "Comcast",                             "Brian Roberts"),
    (34,  "State Farm",                          "Jon Farney"),
    (35,  "Freddie Mac",                         "Michael Hutchins"),
    (36,  "Valero Energy",                       "Lane Riggs"),
    (37,  "Target",                              "Brian Cornell"),
    (38,  "Dell Technologies",                   "Michael Dell"),
    (39,  "Bank of America",                     "Brian Moynihan"),
    (40,  "Tesla",                               "Elon Musk"),
    (41,  "Walt Disney",                         "Bob Iger"),
    (42,  "PepsiCo",                             "Ramon Laguarta"),
    (43,  "Johnson & Johnson",                   "Joaquin Duato"),
    (44,  "UPS",                                 "Carol Tome"),
    (45,  "FedEx",                               "Raj Subramaniam"),
    (46,  "RTX",                                 "Chris Calio"),
    (47,  "Progressive",                         "Tricia Griffith"),
    (48,  "Procter & Gamble",                    "Jon Moeller"),
    (49,  "Lowes",                               "Marvin Ellison"),
    (50,  "Archer Daniels Midland",              "Juan Luciano"),
    (51,  "Sysco",                               "Kevin Hourican"),
    (52,  "Albertsons",                          "Susan Morris"),
    (53,  "Boeing",                              "Kelly Ortberg"),
    (54,  "Energy Transfer",                     "Tom Long"),
    (55,  "Wells Fargo",                         "Charlie Scharf"),
    (56,  "Citigroup",                           "Jane Fraser"),
    (57,  "HCA Healthcare",                      "Sam Hazen"),
    (58,  "Lockheed Martin",                     "Jim Taiclet"),
    (59,  "MetLife",                             "Michel Khalaf"),
    (60,  "Morgan Stanley",                      "Ted Pick"),
    (61,  "Allstate",                            "Tom Wilson"),
    (62,  "IBM",                                 "Arvind Krishna"),
    (63,  "American Express",                    "Steve Squeri"),
    (64,  "Caterpillar",                         "Joe Creed"),
    (65,  "Merck",                               "Rob Davis"),
    (66,  "Delta Air Lines",                     "Ed Bastian"),
    (67,  "Pfizer",                              "Albert Bourla"),
    (68,  "New York Life Insurance",             "Craig DeSanto"),
    (69,  "Performance Food Group",              "George Holm"),
    (70,  "ConocoPhillips",                      "Ryan Lance"),
    (71,  "Oracle",                              "Safra Catz"),
    (72,  "TD Synnex",                           "Patrick Zammit"),
    (73,  "Publix Super Markets",                "Kevin Murphy"),
    (74,  "Broadcom",                            "Hock Tan"),
    (75,  "AbbVie",                              "Rob Michael"),
    (76,  "Eli Lilly",                           "Dave Ricks"),
    (77,  "TJX Companies",                       "Ernie Herrman"),
    (78,  "Nationwide",                          "Kirt Walker"),
    (79,  "United Airlines",                     "Scott Kirby"),
    (80,  "Cisco Systems",                       "Chuck Robbins"),
    (81,  "Prudential Financial",                "Andy Sullivan"),
    (82,  "Goldman Sachs",                       "David Solomon"),
    (83,  "HP",                                  "Enrique Lores"),
    (84,  "Charter Communications",              "Chris Winfrey"),
    (85,  "Tyson Foods",                         "Donnie King"),
    (86,  "American Airlines",                   "Robert Isom"),
    (87,  "Intel",                               "Lip-Bu Tan"),
    (88,  "Enterprise Products Partners",        "Jim Teague"),
    (89,  "General Dynamics",                    "Phebe Novakovic"),
    (90,  "Ingram Micro",                        "Paul Bay"),
    (91,  "Liberty Mutual Insurance",            "Tim Sweeney"),
    (92,  "Uber",                                "Dara Khosrowshahi"),
    (93,  "USAA",                                "Juan Andrade"),
    (94,  "Travelers",                           "Alan Schnitzer"),
    (95,  "Bristol-Myers Squibb",                "Chris Boerner"),
    (96,  "Coca-Cola",                           "James Quincey"),
    (97,  "TIAA",                                "Thasunda Brown Duckett"),
    (98,  "Plains All American Pipeline",        "Willie Chiang"),
    (99,  "Nike",                                "Elliott Hill"),
    (100, "Deere & Company",                     "John May"),
    (101, "Qualcomm",                            "Cristiano Amon"),
    (102, "GE Aerospace",                        "Larry Culp"),
    (103, "Abbott Laboratories",                 "Robert Ford"),
    (104, "Thermo Fisher Scientific",            "Marc Casper"),
    (105, "Netflix",                             "Ted Sarandos"),
    (106, "MassMutual",                          "Roger Crandall"),
    (107, "Molina Healthcare",                   "Joe Zubretsky"),
    (108, "Dollar General",                      "Todd Vasos"),
    (109, "Best Buy",                            "Corie Barry"),
    (110, "Northwestern Mutual",                 "Tim Gerend"),
    (111, "Northrop Grumman",                    "Kathy Warden"),
    (112, "Dow",                                 "Jim Fitterling"),
    (113, "Honeywell",                           "Vimal Kapur"),
    (114, "Salesforce",                          "Marc Benioff"),
    (115, "Visa",                                "Ryan McInerney"),
    (116, "Philip Morris International",         "Jacek Olczak"),
    (117, "CBRE Group",                          "Bob Sulentic"),
    (118, "CHS",                                 "Jay Debertin"),
    (119, "US Foods",                            "Dave Flitman"),
    (120, "Warner Bros. Discovery",              "David Zaslav"),
    (121, "GE Vernova",                          "Scott Strazik"),
    (122, "World Kinect",                        "Michael Kasbar"),
    (123, "Mondelez International",              "Dirk Van de Put"),
    (124, "Lithia Motors",                       "Bryan DeBoer"),
    (125, "Micron Technology",                   "Sanjay Mehrotra"),
    (126, "Starbucks",                           "Brian Niccol"),
    (127, "Amgen",                               "Bob Bradway"),
    (128, "Lennar",                              "Jon Jaffe"),
    (129, "Hewlett Packard Enterprise",          "Antonio Neri"),
    (130, "D.R. Horton",                         "Paul Romanowski"),
    (131, "Coupang",                             "Bom Kim"),
    (132, "Cummins",                             "Jennifer Rumsey"),
    (133, "GuideWell Mutual Holding",            "Patrick Geraghty"),
    (134, "PayPal",                              "Alex Chriss"),
    (135, "Advanced Micro Devices",              "Lisa Su"),
    (136, "Nucor",                               "Leon Topalian"),
    (137, "United Natural Foods",                "Sandy Douglas"),
    (138, "ONEOK",                               "Pierce Norton"),
    (139, "Mastercard",                          "Michael Miebach"),
    (140, "Duke Energy",                         "Harry Sideris"),
    (141, "Ferguson",                            "Kevin Murphy"),
    (142, "Penske Automotive Group",             "Roger Penske"),
    (143, "Jabil",                               "Mike Dastoor"),
    (144, "NRG Energy",                          "Larry Coben"),
    (145, "PBF Energy",                          "Matt Lucey"),
    (146, "PACCAR",                              "Preston Feight"),
    (147, "Arrow Electronics",                   "Sean Kerins"),
    (148, "Gilead Sciences",                     "Daniel ODay"),
    (149, "Southern Company",                    "Chris Womack"),
    (150, "Capital One",                         "Richard Fairbank"),
    (151, "Paramount Global",                    "David Ellison"),
    (152, "Applied Materials",                   "Gary Dickerson"),
    (153, "CarMax",                              "Bill Nash"),
    (154, "AutoNation",                          "Mike Manley"),
    (155, "Hartford Financial Services",         "Chris Swift"),
    (156, "Baker Hughes",                        "Lorenzo Simonelli"),
    (157, "Southwest Airlines",                  "Bob Jordan"),
    (158, "Apollo Global Management",            "Marc Rowan"),
    (159, "Quanta Services",                     "Earl Austin"),
    (160, "American International Group",        "Peter Zaffino"),
    (161, "HF Sinclair",                         "Tim Go"),
    (162, "Occidental Petroleum",                "Vicki Hollub"),
    (163, "Marsh & McLennan",                    "John Doyle"),
    (164, "NextEra Energy",                      "John Ketchum"),
    (165, "McDonalds",                           "Chris Kempczinski"),
    (166, "Booking Holdings",                    "Glenn Fogel"),
    (167, "US Bancorp",                          "Gunjan Kedia"),
    (168, "Freeport-McMoRan",                    "Kathleen Quirk"),
    (169, "Jones Lang LaSalle",                  "Christian Ulbrich"),
    (170, "Kraft Heinz",                         "Carlos Abrams-Rivera"),
    (171, "Marriott International",              "Tony Capuano"),
    (172, "Constellation Energy",                "Joe Dominguez"),
    (173, "3M",                                  "Bill Brown"),
    (174, "Waste Management",                    "Jim Fish"),
    (175, "PG&E",                                "Patti Poppe"),
    (176, "Live Nation Entertainment",           "Michael Rapino"),
    (177, "Union Pacific",                       "Jim Vena"),
    (178, "Stryker",                             "Kevin Lobo"),
    (179, "International Paper",                 "Andy Silvernail"),
    (180, "Exelon",                              "Calvin Butler"),
    (181, "Danaher",                             "Rainer Blair"),
    (182, "Genuine Parts",                       "Will Stengel"),
    (183, "Block",                               "Jack Dorsey"),
    (184, "Adobe",                               "Shantanu Narayen"),
    (185, "Sherwin-Williams",                    "Heidi Petz"),
    (186, "Lear",                                "Ray Scott"),
    (187, "WESCO International",                 "John Engel"),
    (188, "Charles Schwab",                      "Rick Wurster"),
    (189, "BlackRock",                           "Larry Fink"),
    (190, "Macys",                               "Tony Spring"),
    (191, "EOG Resources",                       "Ezra Yacob"),
    (192, "Group 1 Automotive",                  "Daryl Kenningham"),
    (193, "Avnet",                               "Phil Gallagher"),
    (194, "Reinsurance Group of America",        "Tony Cheng"),
    (195, "KKR",                                 "Joseph Bae"),
    (196, "Halliburton",                         "Jeff Miller"),
    (197, "CDW",                                 "Christine Leahy"),
    (198, "Carrier Global",                      "Dave Gitlin"),
    (199, "Ross Stores",                         "Jim Conroy"),
    (200, "Becton Dickinson",                    "Tom Polen"),
    (201, "PNC Financial Services",              "Bill Demchak"),
    (202, "L3Harris Technologies",               "Chris Kubasik"),
    (203, "Newmont",                             "Tom Palmer"),
    (204, "American Family Insurance",           "Bill Westrate"),
    (205, "American Electric Power",             "Bill Fehrman"),
    (206, "BJs Wholesale Club",                  "Bob Eddy"),
    (207, "Fiserv",                              "Mike Lyons"),
    (208, "Super Micro Computer",                "Charles Liang"),
    (209, "Amphenol",                            "Adam Norwitt"),
    (210, "ADP",                                 "Maria Black"),
    (211, "Cognizant Technology Solutions",      "Ravi Kumar S"),
    (212, "Tenet Healthcare",                    "Saumya Sutaria"),
    (213, "GE HealthCare Technologies",          "Peter Arduini"),
    (214, "Altria Group",                        "Sal Mancuso"),
    (215, "Colgate-Palmolive",                   "Noel Wallace"),
    (216, "Parker Hannifin",                     "Jenny Parmentier"),
    (217, "Bank of New York Mellon",             "Robin Vince"),
    (218, "Kimberly-Clark",                      "Mike Hsu"),
    (219, "Lam Research",                        "Tim Archer"),
    (220, "Intuit",                              "Sasan Goodarzi"),
    (221, "Boston Scientific",                   "Mike Mahoney"),
    (222, "AutoZone",                            "Phil Daniele"),
    (223, "General Mills",                       "Jeff Harmening"),
    (224, "Dollar Tree",                         "Mike Creedon"),
    (225, "Cheniere Energy",                     "Jack Fusco"),
    (226, "Cleveland-Cliffs",                    "Lourenco Goncalves"),
    (227, "Ameriprise Financial",                "Jim Cracchiolo"),
    (228, "Aramark",                             "John Zillmer"),
    (229, "Lincoln National",                    "Ellen Cooper"),
    (230, "Corebridge Financial",                "Kevin Hogan"),
    (231, "Goodyear Tire & Rubber",              "Mark Stewart"),
    (232, "Truist Financial",                    "Bill Rogers"),
    (233, "Loews",                               "Ben Tisch"),
    (234, "Carvana",                             "Ernie Garcia"),
    (235, "Global Partners",                     "Eric Slifka"),
    (236, "Edison International",                "Pedro Pizarro"),
    (237, "Emerson Electric",                    "Lal Karsanbhai"),
    (238, "Asbury Automotive Group",             "David Hult"),
    (239, "WW Grainger",                         "DG Macpherson"),
    (240, "Aflac",                               "Dan Amos"),
    (241, "ManpowerGroup",                       "Jonas Prising"),
    (242, "Steel Dynamics",                      "Mark Millett"),
    (243, "PulteGroup",                          "Ryan Marshall"),
    (244, "Discover Financial Services",         "Michael Shepherd"),
    (245, "Corteva",                             "Chuck Magro"),
    (246, "OReilly Automotive",                  "Brad Beckham"),
    (247, "Targa Resources",                     "Matt Meloy"),
    (248, "Leidos",                              "Tom Bell"),
    (249, "MGM Resorts International",           "Bill Hornbuckle"),
    (250, "Texas Instruments",                   "Haviv Ilan"),
    (251, "Vistra",                              "Jim Burke"),
    (252, "Murphy USA",                          "Andrew Clyde"),
    (253, "Universal Health Services",           "Marc Miller"),
    (254, "Caseys General Stores",               "Darren Rebelez"),
    (255, "Peter Kiewit Sons",                   "Rick Lanoha"),
    (256, "Consolidated Edison",                 "Tim Cawley"),
    (257, "Devon Energy",                        "Clay Gaspar"),
    (258, "CH Robinson Worldwide",               "Dave Bozeman"),
    (259, "Republic Services",                   "Jon Vander Ark"),
    (260, "Guardian Life Insurance",             "Andrew McMahon"),
    (261, "Fox",                                 "Lachlan Murdoch"),
    (262, "Kinder Morgan",                       "Kim Dang"),
    (263, "Edward Jones",                        "Penny Pennington"),
    (264, "EMCOR Group",                         "Tony Guzzi"),
    (265, "Markel Group",                        "Tom Gayner"),
    (266, "Land OLakes",                         "Beth Ford"),
    (267, "Keurig Dr Pepper",                    "Tim Cofer"),
    (268, "AECOM",                               "Troy Rudd"),
    (269, "Omnicom Group",                       "John Wren"),
    (270, "United Rentals",                      "Matt Flannery"),
    (271, "IQVIA Holdings",                      "Ari Bousbib"),
    (272, "Ecolab",                              "Christophe Beck"),
    (273, "Illinois Tool Works",                 "Chris OHerlihy"),
    (274, "Auto-Owners Insurance",               "Jamie Whisnant"),
    (275, "Pacific Life",                        "Darryl Button"),
    (276, "Dominion Energy",                     "Bob Blue"),
    (277, "Principal Financial Group",           "Deanna Strable"),
    (278, "Kohls",                               "Michael Bender"),
    (279, "PPG Industries",                      "Tim Knavish"),
    (280, "Builders FirstSource",                "Peter Jackson"),
    (281, "Fluor",                               "Jim Breuer"),
    (282, "Whirlpool",                           "Marc Bitzer"),
    (283, "Farmers Insurance Exchange",          "Raul Vargas"),
    (284, "Tractor Supply",                      "Hal Lawton"),
    (285, "Gap",                                 "Richard Dickson"),
    (286, "EchoStar",                            "Hamid Akhavan"),
    (287, "Sonic Automotive",                    "David Bruton Smith"),
    (288, "Stanley Black & Decker",              "Don Allan"),
    (289, "LPL Financial",                       "Rich Steinmeier"),
    (290, "Kyndryl",                             "Martin Schroeter"),
    (291, "Kenvue",                              "Thibaut Mongon"),
    (292, "S&P Global",                          "Martina Cheung"),
    (293, "Corning",                             "Wendell Weeks"),
    (294, "Dicks Sporting Goods",                "Lauren Hobart"),
    (295, "DTE Energy",                          "Jerry Norcia"),
    (296, "WR Berkley",                          "Robert Berkley Jr"),
    (297, "Diamondback Energy",                  "Kaes Van't Hof"),
    (298, "Mutual of Omaha Insurance",           "James Blackledge"),
    (299, "Nordstrom",                           "Erik Nordstrom"),
    (300, "Estee Lauder",                        "Stephane de La Faverie"),
    (301, "Expedia Group",                       "Ariane Gorin"),
    (302, "Otis Worldwide",                      "Judy Marks"),
    (303, "FirstEnergy",                         "Brian Tierney"),
    (304, "Regeneron Pharmaceuticals",           "Len Schleifer"),
    (305, "Textron",                             "Scott Donnelly"),
    (306, "Xcel Energy",                         "Bob Frenzel"),
    (307, "BorgWarner",                          "Joe Fadool"),
    (308, "Alaska Air Group",                    "Ben Minicucci"),
    (309, "Viatris",                             "Scott Smith"),
    (310, "CSX",                                 "Joe Hinrichs"),
    (311, "LKQ",                                 "Justin Jude"),
    (312, "Fidelity National Financial",         "Mike Nolan"),
    (313, "Raymond James Financial",             "Paul Shoukry"),
    (314, "Reliance",                            "Karla Lewis"),
    (315, "Labcorp",                             "Adam Schechter"),
    (316, "Western & Southern Financial Group",  "John Barrett"),
    (317, "MasTec",                              "Jose Mas"),
    (318, "Sempra",                              "Jeff Martin"),
    (319, "State Street",                        "Ron OHanley"),
    (320, "United States Steel",                 "David Burritt"),
    (321, "DaVita",                              "Javier Rodriguez"),
    (322, "BrightSpring Health Services",        "Jon Rousseau"),
    (323, "Erie Indemnity",                      "Tim NeCastro"),
    (324, "Eversource Energy",                   "Joe Nolan"),
    (325, "Unum Group",                          "Rick McKenney"),
    (326, "Henry Schein",                        "Stan Bergman"),
    (327, "GXO Logistics",                       "Malcolm Wilson"),
    (328, "Alcoa",                               "Bill Oplinger"),
    (329, "DuPont",                              "Lori Koch"),
    (330, "Blackstone",                          "Steve Schwarzman"),
    (331, "Entergy",                             "Andrew Marsh"),
    (332, "DXC Technology",                      "Raul Fernandez"),
    (333, "Lumen Technologies",                  "Kate Johnson"),
    (334, "Ball",                                "Dan Fisher"),
    (335, "Ryder System",                        "Rob Sanchez"),
    (336, "Kellanova",                           "Steve Cahillane"),
    (337, "ServiceNow",                          "Bill McDermott"),
    (338, "Community Health Systems",            "Kevin Hammons"),
    (339, "DoorDash",                            "Tony Xu"),
    (340, "Chewy",                               "Sumit Singh"),
    (341, "Assurant",                            "Keith Demmings"),
    (342, "KLA",                                 "Rick Wallace"),
    (343, "Darden Restaurants",                  "Ricardo Cardenas"),
    (344, "Las Vegas Sands",                     "Rob Goldstein"),
    (345, "Wayfair",                             "Niraj Shah"),
    (346, "Norfolk Southern",                    "Mark George"),
    (347, "Equitable Holdings",                  "Mark Pearson"),
    (348, "Crown Holdings",                      "Tim Donahue"),
    (349, "Hormel Foods",                        "Jim Snee"),
    (350, "AES",                                 "Andres Gluski"),
    (351, "Arthur J. Gallagher",                 "Pat Gallagher"),
    (352, "Cincinnati Financial",                "Steve Spray"),
    (353, "JB Hunt Transport Services",          "Shelley Simpson"),
    (354, "Air Products & Chemicals",            "Eduardo Menezes"),
    (355, "Jacobs Solutions",                    "Bob Pragada"),
    (356, "Huntington Ingalls Industries",       "Chris Kastner"),
    (357, "Hess",                                "John Hess"),
    (358, "Ulta Beauty",                         "Kecia Steelman"),
    (359, "Airbnb",                              "Brian Chesky"),
    (360, "Mosaic",                              "Bruce Bodine"),
    (361, "Chipotle Mexican Grill",              "Scott Boatwright"),
    (362, "Vertex Pharmaceuticals",              "Reshma Kewalramani"),
    (363, "Public Service Enterprise Group",     "Ralph LaRossa"),
    (364, "Booz Allen Hamilton",                 "Horacio Rozanski"),
    (365, "Avis Budget Group",                   "Joe Ferraro"),
    (366, "Owens Corning",                       "Brian Chambers"),
    (367, "Graybar Electric",                    "Kathy Mazzarella"),
    (368, "Andersons",                           "Bill Krueger"),
    (369, "Williams Companies",                  "Alan Armstrong"),
    (370, "Berry Global Group",                  "Kevin Kwilinski"),
    (371, "Yum China Holdings",                  "Joey Wat"),
    (372, "Hershey",                             "Michele Buck"),
    (373, "Westlake",                            "Jean-Marc Gilson"),
    (374, "Conagra Brands",                      "Sean Connolly"),
    (375, "Caesars Entertainment",               "Tom Reeg"),
    (376, "Motorola Solutions",                  "Greg Brown"),
    (377, "Oscar Health",                        "Mark Bertolini"),
    (378, "Molson Coors Beverage",               "Gavin Hattersley"),
    (379, "Burlington Stores",                   "Michael OSullivan"),
    (380, "Expeditors International",            "Dan Wall"),
    (381, "International Flavors & Fragrances",  "Erik Fyrwald"),
    (382, "Baxter International",                "Brent Shafer"),
    (383, "Analog Devices",                      "Vince Roche"),
    (384, "Hilton Worldwide",                    "Chris Nassetta"),
    (385, "Toll Brothers",                       "Doug Yearley"),
    (386, "Thrivent Financial",                  "Teresa Rasmussen"),
    (387, "Quest Diagnostics",                   "James Davis"),
    (388, "Interpublic Group",                   "Philippe Krakowsky"),
    (389, "Wabtec",                              "Rafael Santana"),
    (390, "Owens & Minor",                       "Ed Pesicka"),
    (391, "Mohawk Industries",                   "Jeff Lorberbaum"),
    (392, "eBay",                                "Jamie Iannone"),
    (393, "Delek US Holdings",                   "Avigal Soreq"),
    (394, "NVR",                                 "Eugene Bredow"),
    (395, "Cintas",                              "Todd Schneider"),
    (396, "Ally Financial",                      "Michael Rhodes"),
    (397, "Lululemon Athletica",                 "Calvin McDonald"),
    (398, "A-Mark Precious Metals",              "Greg Roberts"),
    (399, "Fidelity National Information Services", "Stephanie Ferris"),
    (400, "American Tower",                      "Steve Vondran"),
    (401, "FM Global",                           "Malcolm Roberts"),
    (402, "Autoliv",                             "Mikael Bratt"),
    (403, "Oshkosh",                             "John Pfeifer"),
    (404, "Campbells",                           "Mick Beekhuizen"),
    (405, "Western Digital",                     "Irving Tan"),
    (406, "Global Payments",                     "Cameron Bready"),
    (407, "Biogen",                              "Chris Viehbacher"),
    (408, "AGCO",                                "Eric Hansotia"),
    (409, "Dana",                                "Bruce McDonald"),
    (410, "Welltower",                           "Shankh Mitra"),
    (411, "THOR Industries",                     "Bob Martin"),
    (412, "Seaboard",                            "Robert Steer"),
    (413, "Intercontinental Exchange",           "Jeff Sprecher"),
    (414, "Concentrix",                          "Chris Caldwell"),
    (415, "Celanese",                            "Scott Richardson"),
    (416, "Vertiv Holdings",                     "Giordano Albertazzi"),
    (417, "Synchrony Financial",                 "Brian Doubles"),
    (418, "Constellation Brands",                "Bill Newlands"),
    (419, "Intuitive Surgical",                  "Gary Guthart"),
    (420, "Palo Alto Networks",                  "Nikesh Arora"),
    (421, "WEC Energy Group",                    "Scott Lauber"),
    (422, "VF Corporation",                      "Bracken Darrell"),
    (423, "SpartanNash",                         "Tony Sarsam"),
    (424, "QVC Group",                           "David Rawlinson"),
    (425, "Ace Hardware",                        "John Venhuizen"),
    (426, "Zoetis",                              "Kristin Peck"),
    (427, "APA",                                 "John Christmann"),
    (428, "Skechers USA",                        "Robert Greenberg"),
    (429, "Icahn Enterprises",                   "Andrew Teno"),
    (430, "Workday",                             "Carl Eschenbach"),
    (431, "CenterPoint Energy",                  "Jason Wells"),
    (432, "JetBlue Airways",                     "Joanna Geraghty"),
    (433, "Prologis",                            "Hamid Moghadam"),
    (434, "M&T Bank",                            "Rene Jones"),
    (435, "Equinix",                             "Adaire Fox-Martin"),
    (436, "Eastman Chemical",                    "Mark Costa"),
    (437, "Altice USA",                          "Dennis Mathew"),
    (438, "PPL",                                 "Vince Sorgi"),
    (439, "First Citizens BancShares",           "Frank Holding Jr"),
    (440, "Xylem",                               "Matt Pine"),
    (441, "CACI International",                  "John Mengucci"),
    (442, "TransDigm Group",                     "Kevin Stein"),
    (443, "PVH",                                 "Stefan Larsson"),
    (444, "Ovintiv",                             "Brendan McCracken"),
    (445, "NOV",                                 "Clay Williams"),
    (446, "Avery Dennison",                      "Deon Stander"),
    (447, "Franklin Resources",                  "Jenny Johnson"),
    (448, "Packaging Corp of America",           "Mark Kowlzan"),
    (449, "JM Smucker",                          "Mark Smucker"),
    (450, "Old Republic International",          "Craig Smiddy"),
    (451, "Sprouts Farmers Market",              "Jack Sinclair"),
    (452, "ABM Industries",                      "Scott Salmirs"),
    (453, "Advance Auto Parts",                  "Shane OKelly"),
    (454, "Graphic Packaging",                   "Robbert Rietbroek"),
    (455, "Sirius XM",                           "Jennifer Witz"),
    (456, "Hertz Global Holdings",               "Gil West"),
    (457, "Jefferies Financial Group",           "Rich Handler"),
    (458, "News Corp",                           "Robert Thomson"),
    (459, "Solventum",                           "Bryan Hanson"),
    (460, "Taylor Morrison Home",                "Sheryl Palmer"),
    (461, "Rockwell Automation",                 "Blake Moret"),
    (462, "CMS Energy",                          "Garrick Rochow"),
    (463, "Insight Enterprises",                 "Joyce Mullen"),
    (464, "Securian Financial Group",            "Chris Hilger"),
    (465, "Post Holdings",                       "Rob Vitale"),
    (466, "Fifth Third Bancorp",                 "Tim Spence"),
    (467, "Sanmina",                             "Jure Sola"),
    (468, "Voya Financial",                      "Heather Lavallee"),
    (469, "XPO",                                 "Mario Harik"),
    (470, "Yum Brands",                          "David Gibbs"),
    (471, "KBR",                                 "Stuart Bradie"),
    (472, "American Financial Group",            "Carl Lindner III"),
    (473, "Zimmer Biomet",                       "Ivan Tornos"),
    (474, "Fastenal",                            "Dan Florness"),
    (475, "Foot Locker",                         "Mary Dillon"),
    (476, "Monster Beverage",                    "Rodney Sacks"),
    (477, "Howmet Aerospace",                    "John Plant"),
    (478, "Northern Trust",                      "Michael OGrady"),
    (479, "Dover",                               "Richard Tobin"),
    (480, "Williams-Sonoma",                     "Laura Alber"),
    (481, "ARKO",                                "Arie Kotler"),
    (482, "Vulcan Materials",                    "Tom Hill"),
    (483, "Regions Financial",                   "John Turner"),
    (484, "Commercial Metals",                   "Peter Matt"),
    (485, "Core & Main",                         "Mark Witkowski"),
    (486, "Rush Enterprises",                    "Rusty Rush"),
    (487, "Microchip Technology",                "Steve Sanghi"),
    (488, "Masco",                               "Keith Allman"),
    (489, "Interactive Brokers",                 "Milan Galik"),
    (490, "Huntington Bancshares",               "Steve Steinour"),
    (491, "Endeavor Group",                      "Mark Shapiro"),
    (492, "Par Pacific Holdings",                "Bill Monteleone"),
    (493, "Citizens Financial Group",            "Bruce Van Saun"),
    (494, "Watsco",                              "Albert Nahmad"),
    (495, "Science Applications International",  "Toni Townes-Whitley"),
    (496, "Electronic Arts",                     "Andrew Wilson"),
    (497, "Newell Brands",                       "Chris Peterson"),
    (498, "Ingredion",                           "Jim Zallie"),
    (499, "KeyCorp",                             "Chris Gorman"),
    (500, "QXO",                                 "Brad Jacobs"),
]

# ── Helpers ──────────────────────────────────────────────────────────────────

def slugify(text: str) -> str:
    """Convert a name or company string to a safe filename token."""
    text = text.lower()
    text = re.sub(r"[&/\\'\"]", "", text)
    text = re.sub(r"[\s\-\.]+", "_", text)
    text = re.sub(r"[^a-z0-9_]", "", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def output_path(ceo: str, company: str) -> Path:
    """Return the target file path for a given CEO/company pair."""
    parts = ceo.split()
    first = slugify(parts[0]) if parts else "unknown"
    last  = slugify(parts[-1]) if len(parts) > 1 else "unknown"
    co    = slugify(company)
    return OUT_DIR / f"{first}_{last}_{co}.txt"


SYSTEM_PROMPT = """You are a senior strategy research analyst producing an executive intelligence knowledge base. \
Your documents are used in a RAG system to answer questions about how Fortune 500 leaders think and decide. \
Write in a third-person, analytical tone — like a high-quality research firm report. \
Be specific: reference actual strategies, products, markets, competitive decisions, and known business outcomes. \
Do not invent quotations; paraphrase or summarize known positions instead. \
Use --- SECTION HEADER --- style section breaks (all caps, surrounded by ---). \
Do not include preamble, meta-commentary, or "here is the document". Output the document text directly."""


def build_user_prompt(rank: int, company: str, ceo: str) -> str:
    return f"""Write a 1,500–2,000 word executive leadership intelligence document about {ceo}, CEO of {company} \
(Fortune 500 rank #{rank}).

Begin with exactly this header line (fill in the bracketed themes yourself):
"{ceo} on [Theme], [Theme], and [Theme]"
followed by:
"Source: [comma-separated list of relevant public sources such as earnings calls, shareholder letters, keynotes, interviews]"

Then write 6–8 thematic sections using --- SECTION HEADER --- dividers. Each section should be 2–4 substantial paragraphs.

Cover topics relevant to this leader's domain, for example:
- Strategic philosophy and decision-making approach
- Competitive positioning and market strategy
- Capital allocation and investment priorities
- Technology, innovation, or operational bets
- Culture, talent, and organizational design
- Industry-specific challenges and how they are navigated
- Leadership through disruption, downturns, or crises
- Long-term vision and platform bets

Draw from publicly available information. For less publicly prominent leaders, focus on the company's strategy, \
business model, and competitive dynamics under their tenure."""


# ── Generation ────────────────────────────────────────────────────────────────

def generate_document(client: openai.OpenAI, rank: int, company: str, ceo: str) -> str:
    """Call the OpenAI API and return the generated document text."""
    max_retries = 5
    base_delay  = 10.0

    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                max_tokens=3000,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": build_user_prompt(rank, company, ceo)},
                ],
            )
            return response.choices[0].message.content or ""

        except openai.RateLimitError:
            delay = base_delay * (2 ** attempt)
            print(f"    Rate limited — waiting {delay:.0f}s before retry {attempt + 1}/{max_retries}")
            time.sleep(delay)
        except openai.APIStatusError as e:
            print(f"    API error {e.status_code}: {e.message} — skipping")
            return ""
        except Exception as e:
            print(f"    Unexpected error: {e} — skipping")
            return ""

    print(f"    Max retries exhausted for {ceo} / {company}")
    return ""


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run",   action="store_true", help="Print targets, make no API calls")
    parser.add_argument("--overwrite", action="store_true", help="Regenerate even if file exists")
    parser.add_argument("--limit",     type=int, default=0,  help="Stop after N documents (0 = all)")
    parser.add_argument("--start",     type=int, default=0,  help="Skip first N entries (0-indexed)")
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    client = None if args.dry_run else openai.OpenAI()  # reads OPENAI_API_KEY from env

    entries   = FORTUNE_500[args.start:]
    generated = 0
    skipped   = 0
    total     = len(entries) if not args.limit else min(args.limit, len(entries))

    print(f"Fortune 500 corpus generator")
    print(f"Output dir : {OUT_DIR}")
    print(f"Mode       : {'dry-run' if args.dry_run else 'generate'}")
    print(f"Overwrite  : {args.overwrite}")
    print(f"Entries    : {total} (starting at offset {args.start})")
    print()

    for i, (rank, company, ceo) in enumerate(entries):
        if args.limit and generated + skipped >= args.limit:
            break

        path = output_path(ceo, company)
        label = f"[{i + 1 + args.start:3d}/{500}] #{rank:3d} {company} — {ceo}"

        if path.exists() and not args.overwrite:
            print(f"  SKIP  {label}")
            print(f"        → {path.name}")
            skipped += 1
            continue

        if args.dry_run:
            print(f"  WOULD {label}")
            print(f"        → {path.name}")
            generated += 1
            continue

        print(f"  GEN   {label}")
        doc = generate_document(client, rank, company, ceo)

        if doc:
            path.write_text(doc, encoding="utf-8")
            print(f"        → {path.name} ({len(doc):,} chars)")
            generated += 1
        else:
            print(f"        → FAILED, skipped")
            skipped += 1

        # Polite pacing: ~40 requests/min well within API limits
        time.sleep(1.5)

    print()
    print(f"Done. Generated: {generated}  Skipped/failed: {skipped}")
    if generated:
        print(f"Re-ingest with:  python app/ingest.py")


if __name__ == "__main__":
    main()
