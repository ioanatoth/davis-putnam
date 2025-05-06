import time
import tracemalloc
import csv

def is_tautology(clause):
    return any(
        (lit[0] == '-' and lit[1:] in clause) or
        (not lit.startswith('-') and '-' + lit in clause)
        for lit in clause
    )

def resolve(ci, cj):
    resolvents = []
    for lit in ci:
        complement = '-' + lit if not lit.startswith('-') else lit[1:]
        if complement in cj:
            new_clause = [l for l in ci if l != lit] + [l for l in cj if l != complement]
            if not is_tautology(new_clause):
                resolvents.append(sorted(set(new_clause)))
    return resolvents

def davis_putnam(clauses):
    clauses = [sorted(set(cl)) for cl in clauses if not is_tautology(cl)]
    clauses_set = set(tuple(cl) for cl in clauses)
    new = set()

    while True:
        pairs = [(ci, cj) for i, ci in enumerate(clauses) for cj in clauses[i+1:]]
        for ci, cj in pairs:
            for resolvent in resolve(ci, cj):
                resolvent_tuple = tuple(sorted(set(resolvent)))
                if resolvent_tuple == ():
                    print("Formula este NESATISFIABILĂ.")
                    return False
                if resolvent_tuple not in clauses_set:
                    new.add(resolvent_tuple)
        if new.issubset(clauses_set):
            print("Formula este SATISFIABILĂ.")
            return True
        for clause in new:
            clauses_set.add(clause)
            clauses.append(list(clause))
        new.clear()

def citeste_bloc_clauze():
    print("Lipește toate clauzele (ex: dintr-un fișier .cnf), apoi apasă Enter de 2 ori:")
    input_lines = []
    while True:
        try:
            line = input()
            if line.strip() == "":
                break
            input_lines.append(line.strip())
        except EOFError:
            break
    clauze = []
    for linie in input_lines:
        litere = linie.strip().split()
        if litere and litere[-1] == '0':
            litere = litere[:-1]
        clauza = [lit if not lit.startswith('-') else '-' + lit[1:] if lit[1:].isdigit() else lit for lit in litere]
        clauze.append(clauza)
    return clauze

def salveaza_performanta_in_csv(timp, memorie_kb, numar_clauze, literali_per_clauza, satisfiabilitate, nume_fisier="performanta.csv"):
    scrie_antet=False
    try:
        with open(nume_fisier, mode='r'):
            pass
    except FileNotFoundError:
        scrie_antet = True
    with open(nume_fisier, mode='a', newline='') as f:
        writer = csv.writer(f)
        if scrie_antet:
            writer.writerow(["timp_secunde", "memorie_kb", "nr_clauze", "literali_per_clauza", "satisfiabilitate"])
        writer.writerow([f"{timp:.6f}",f"{memorie_kb:.2f}",numar_clauze,";".join(str(nr) for nr in literali_per_clauza),satisfiabilitate])

if __name__ == "__main__":
    formula = citeste_bloc_clauze()
    print("\nFormulă introdusă (CNF):", formula)

    numar_clauze = len(formula)
    literali_per_clauza = [len(clauza) for clauza in formula]

    tracemalloc.start()
    start_time = time.perf_counter()

    is_unsatisfiable = davis_putnam(formula)

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    durata = end_time - start_time
    memorie_kb = peak / 1024
    satisfiabilitate = "SATISFIABILĂ" if is_unsatisfiable else "NESATISFIABILA"

    salveaza_performanta_in_csv(durata, memorie_kb, numar_clauze, literali_per_clauza, satisfiabilitate)

    print(f"\nTimp de execuție: {durata:.6f} secunde")
    print(f"Memorie maximă utilizata: {memorie_kb:.2f} KB")
