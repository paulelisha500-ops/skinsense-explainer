"""Checks on the validation layer - the part that fails silently if it is wrong."""
from guard import validate, find_violations, ungrounded_sentences, fallback
from retrieve import by_label, search, entry_text

SRC = entry_text(by_label("eczema"))

def check(name, cond):
    print(("PASS  " if cond else "FAIL  ") + name)
    return cond

ok = True
ok &= check("blocks dosage advice",
            bool(find_violations("Apply the cream twice a day and take 500mg of it.")))
ok &= check("blocks definitive diagnosis",
            bool(find_violations("You have eczema, this is definitely it.")))
ok &= check("blocks over-long output", bool(find_violations("word " * 400)))
ok &= check("blocks empty output", bool(find_violations("   ")))

grounded = ("Eczema is a chronic inflammatory skin condition linked to a weakened "
            "skin barrier. It often appears as dry scaly itchy patches in skin creases.")
good, why = validate(grounded, SRC)
ok &= check("accepts grounded, non-prescriptive text", good)

invented = ("Eczema is caused by a parasite contracted from drinking river water "
            "during the monsoon season in coastal regions.")
ok &= check("flags invented statement", bool(ungrounded_sentences(invented, SRC)))

ok &= check("fallback names condition and disclaims diagnosis",
            "Eczema" in fallback(by_label("eczema"), 0.81)
            and "not a diagnosis" in fallback(by_label("eczema"), 0.81))
ok &= check("fallback itself passes validation",
            validate(fallback(by_label("eczema"), 0.81), SRC)[0])

ok &= check("label lookup works", by_label("Psoriasis")["name"] == "Psoriasis")
ok &= check("unknown label returns None", by_label("not_a_condition") is None)
ok &= check("search finds itchy weals -> urticaria",
            any(k == "urticaria" for k, _, _ in search("itchy weals that vanish in hours")))
ok &= check("search returns nothing for off-topic question",
            search("how do I renew my passport") == [])

print("\nALL PASS" if ok else "\nFAILURES ABOVE")
raise SystemExit(0 if ok else 1)
