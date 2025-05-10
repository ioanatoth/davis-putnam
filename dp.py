import time
import tracemalloc
import csv
import os


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
            new_clause = sorted(set(new_clause))
            if not is_tautology(new_clause):
                resolvents.append(new_clause)
    return resolvents


def davis_putnam(clauses):
    clauses = [sorted(set(cl)) for cl in clauses if not is_tautology(cl)]
    clauses_set = set(tuple(cl) for cl in clauses)
    new = set()

    while True:
        n = len(clauses)
        pairs = [(ci, cj) for i, ci in enumerate(clauses) for cj in clauses[i + 1:]]
        for ci, cj in pairs:
            for resolvent in resolve(ci, cj):
                resolvent_tuple = tuple(resolvent)
                if len(resolvent_tuple) == 0:  
                    print("Formula este NESATISFIABILĂ.")
                    return False
                if resolvent_tuple not in clauses_set:
                    new.add(resolvent_tuple)

        if not new:  
            print("Formula este SATISFIABILĂ.")
            return True

        for clause in new:
            clauses_set.add(clause)
            clauses.append(list(clause))
        new.clear()

        if len(clauses) > 1000:
            print("Limită de clauze depășită. Nu se poate determina satisfiabilitatea.")
            return None


def citeste_bloc_clauze():
    print("Introdu clauzele (câte una pe linie), termină cu o linie goală:")
    input_lines = []
    while True:
        line = input().strip()
        if line == "":
            if input_lines: 
                break
            else:
                print("Introdu cel puțin o clauză!")
                continue
        input_lines.append(line)

    clauze = []
    for linie in input_lines:
        if linie.startswith('c') or linie.startswith('p'):
            continue

        litere = linie.split()
        if litere and litere[-1] == '0':
            litere = litere[:-1]

        clauza = []
        for lit in litere:
            if lit.startswith('--'):
                clauza.append(lit[2:])
            elif lit.startswith('-'):
                clauza.append('-' + lit[1:].strip())
            else:
                clauza.append(lit.strip())

        if clauza:  # Adaugă doar dacă nu e goală
            clauze.append(clauza)

    return clauze


def salveaza_performanta_in_csv(timp, memorie_kb, numar_clauze, literali_per_clauza, satisfiabilitate,
                                nume_fisier="performanta.csv"):
    try:
        scrie_antet = not os.path.exists(nume_fisier)
        with open(nume_fisier, mode='a', newline='') as f:
            writer = csv.writer(f)
            if scrie_antet:
                writer.writerow(["timp_secunde", "memorie_kb", "nr_clauze", "literali_per_clauza", "satisfiabilitate"])
            writer.writerow([
                f"{timp:.6f}",
                f"{memorie_kb:.2f}",
                numar_clauze,
                ";".join(map(str, literali_per_clauza)),
                satisfiabilitate
            ])
        print(f"Datele au fost salvate în {nume_fisier}")
    except PermissionError:
        print(f"Eroare: Nu am permisiunea de a scrie în {nume_fisier}")
    except Exception as e:
        print(f"Eroare la scrierea în fișier: {str(e)}")


if __name__ == "__main__":
    print("=== SAT Solver cu algoritmul Davis-Putnam ===")

    formula = citeste_bloc_clauze()
    print("\nFormulă introdusă (CNF):")
    for i, clauza in enumerate(formula, 1):
        print(f"Clauza {i}: {clauza}")

    if not formula:
        print("Eroare: Nu s-au introdus clauze valide!")
        exit()

    numar_clauze = len(formula)
    literali_per_clauza = [len(clauza) for clauza in formula]

    print("\nÎncep procesarea...")
    tracemalloc.start()
    start_time = time.perf_counter()

    try:
        is_satisfiable = davis_putnam(formula)
    except Exception as e:
        print(f"Eroare în timpul execuției: {str(e)}")
        is_satisfiable = None

    end_time = time.perf_counter()
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    durata = end_time - start_time
    memorie_kb = peak / 1024
    satisfiabilitate = "SATISFIABILĂ" if is_satisfiable else "NESATISFIABILA" if is_satisfiable is False else "INDETERMINAT"

    print(f"\nRezultat: {satisfiabilitate}")
    print(f"Timp de execuție: {durata:.6f} secunde")
    print(f"Memorie maximă utilizată: {memorie_kb:.2f} KB")

    # Salvarea rezultatelor
    salveaza_performanta_in_csv(durata, memorie_kb, numar_clauze, literali_per_clauza, satisfiabilitate)
