from main import *

intentfp, thesaurusfp, UIName = "intents.json", "thesaurus.json", "Ultron"

JanexPT = JanexPT(intentfp)

#JanexPT.trainpt()
inputstr = input("You: ")
IC = JanexPT.pattern_compare(inputstr)

print(IC)
