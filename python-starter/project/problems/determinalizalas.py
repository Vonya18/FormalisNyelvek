from project.problem import Problem
import argparse
import sys


class NFA:
    """Nemdeterminisztikus véges automata, determinizálással."""

    def __init__(self, states, alphabet, start, finals, transitions):
        self.states = states
        self.alphabet = alphabet
        self.start = start
        self.finals = finals
        # {(állapot, betű): {célállapotok halmaza}}
        # Halmaz, mert egy betűre több célállapot is lehet.
        self.transitions = transitions

    @staticmethod
    def from_file(path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()

        # Az első négy sor pozíció alapján: állapotok, ábécé, kezdő, végállapotok
        states = lines[0].split()
        alphabet = lines[1].split()
        start = lines[2].strip()
        finals = set(lines[3].split())

        # A többi sor az átmenet: honnan betű hova
        transitions = {}
        for line in lines[4:]:
            if line.strip() == "":
                continue
            parts = line.split()
            if len(parts) != 3:
                raise ValueError(f"Hibás átmenet-sor: '{line}'")
            src, symbol, dst = parts

            # Hibakezelés: csak a fájl elején felsorolt elemek szerepelhetnek
            if src not in states or dst not in states:
                raise ValueError(f"Ismeretlen állapot az átmenetben: '{line}'")
            if symbol not in alphabet:
                raise ValueError(f"Ismeretlen jel az átmenetben: '{line}'")

            transitions.setdefault((src, symbol), set()).add(dst)

        return NFA(states, alphabet, start, finals, transitions)

    def determinize(self):
        """
        Részhalmaz-konstrukció: az új automata egy állapota az eredeti
        automata állapotainak egy HALMAZA (azokat jelenti, ahol az automata
        egyszerre lehet).

        Visszaad: (állapotok száma, végállapotok sorszámai, átmenetek listája)
        """
        # Kezdőállapot: az eredeti kezdőállapotot tartalmazó halmaz
        start = frozenset([self.start])

        names = {start: 0}   # halmaz -> sorszám (a sorszám lesz az s-szám)
        order = [start]      # a halmazok a felfedezés sorrendjében
        transitions = []     # (honnan, betű, hová) számokkal

        i = 0
        while i < len(order):          # amíg van feldolgozatlan halmaz
            current = order[i]

            for symbol in sorted(self.alphabet):   # ábécé sorrendben
                # Az összes állapot, ahová current-ből symbol-lal eljutunk
                target = set()
                for state in current:
                    target |= self.transitions.get((state, symbol), set())

                if not target:
                    continue           # nincs átmenet -> nem írjuk ki

                target = frozenset(target)

                # Új halmaz? Akkor kap egy új sorszámot.
                if target not in names:
                    names[target] = len(order)
                    order.append(target)

                transitions.append((names[current], symbol, names[target]))

            i += 1

        # Végállapot az, amelyik halmaz tartalmaz eredeti végállapotot
        finals = [names[s] for s in order if s & self.finals]

        return len(order), finals, transitions


class DeterminizeProblem(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--det', help='determinize the automaton', action='store_true')

    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return bool(args.det)

    def run(self, args):
        """
        Run the problem
        """
        try:
            nfa = NFA.from_file(args.input)
        except ValueError as error:
            print(f"Hiba: {error}", file=sys.stderr)
            sys.exit(1)

        count, finals, transitions = nfa.determinize()

        # Kimenet összeállítása a feladat formátuma szerint
        lines = [
            " ".join(f"s{n}" for n in range(count)),        # állapotok
            " ".join(sorted(nfa.alphabet)),                  # ábécé
            "s0",                                            # kezdőállapot
            " ".join(f"s{n}" for n in finals),               # végállapotok
        ]
        for src, symbol, dst in transitions:
            lines.append(f"s{src} {symbol} s{dst}")

        with open(args.output, 'w', encoding="utf-8") as f:
            f.write("\n".join(lines))
            