from project.problem import Problem
import argparse

class DFA:
    def __init__(self, states, alphabet, start, finals, transitions):
        self.states = states
        self.alphabet = alphabet
        self.start = start
        self.finals = finals
        self.transitions = transitions  #{(allapot, betu): allapot}
        
    @staticmethod
    def from_file(path):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
            
        states = lines[0].split()
        alphabet = lines[1].split()
        start = lines[2].strip()
        finals = set(lines[3].split())
        
        transitions = {}
        for line in lines[4:]:
            parts = line.split()
            if len(parts) == 3:
                src, symbol, dst = parts
                transitions[(src, symbol)] = dst
                
        return DFA(states, alphabet, start, finals, transitions)
    
    def accepts(self, word):
        state = self.start
        for ch in word:
            #ismeretlen betu v hianyzo atmenet = elutasitas
            if (state, ch) not in self.transitions:
                return False
            state = self.transitions[(state, ch)]
        return state in self.finals
    
class DFAProblems(Problem):

    def initialize_parser(self, parser: argparse.ArgumentParser):
        """
        Initialize the parser with the necessary arguments
        """
        parser.add_argument('--check', help='comma separated words to check')
    
    def is_chosen_problem(self, args):
        """
        Check if the problem is chosen
        """
        return args.check is not None

    def run(self, args):
        """
        Run the problem
        """
        dfa = DFA.from_file(args.input)
        words = args.check.split(',')
        results = ["IGEN" if dfa.accepts(w) else "NEM" for w in words]
        
        with open(args.output, 'w', encoding="utf-8") as f:
            f.write("\n".join(results))
