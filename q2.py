import json 
import sys

class NFA: 
    def __init__(self, nfa: dict):
        self.states = nfa['states']
        self.letters = nfa['letters']
        self.transition_function = nfa['transition_function']
        self.start_states = nfa['start_states']
        self.final_states = nfa['final_states']
        self.make_movements()
    
    def make_movements(self):
        self.move = {}
        for trans in self.transition_function:
            _from, letter, to = trans
            if (_from, letter) in self.move:
                self.move[(_from, letter)] = self.move[(_from, letter)] | set([to])
            else:
                self.move[(_from, letter)] = set([to])

class DFA:
    def __init__(self):
        self.states = None
        self.letters = None
        self.transition_function = None
        self.start_states = None
        self.final_states = None

    def initialize_from_nfa(self, nfa: NFA):
        self.states = []
        for idx in range(2**len(nfa.states)):
            curr_state = []
            for pos in range(len(nfa.states)):
                if (idx >> pos) & 1:
                    curr_state.append(nfa.states[pos])
            self.states.append(curr_state)

        self.letters = nfa.letters
        self.start_states = [nfa.start_states]
    
    def get_dict(self):
        return {
            'states': self.states,
            'letters': self.letters,
            'transition_matrix': self.transition_function,
            'start_states': self.start_states,
            'final_states': self.final_states
        }

    
def nfa_to_dfa(nfa: NFA):
    dfa = DFA()

    # got dfa states, letters, start_states
    dfa.initialize_from_nfa(nfa)

    # got dfa transition_function
    dfa.transition_function = []
    for from_states in dfa.states:
        for ch in dfa.letters:
            to_states = set()
            for from_state in from_states:
                if (from_state, ch) in nfa.move:
                    to_states = to_states | nfa.move[(from_state, ch)]
            dfa.transition_function.append([from_states, ch, list(to_states)])
    
    # got dfa finish_states
    dfa.final_states = []
    for curr_states in dfa.states:
        for state in curr_states:
            if state in nfa.final_states:
                dfa.final_states.append(curr_states)
                break
    return dfa


def get_nfa():
    input_file = str(sys.argv[1])
    with open(input_file, 'r') as f:
        data = json.load(f)
        return NFA(data)


def save_dfa(dfa: DFA):
    output_file = str(sys.argv[2])
    with open(output_file, 'w') as f:
        json.dump(dfa.get_dict(), f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('incorrect input')
        print('Input format: python3 q2.py <input_file> <output_file>')
        exit()

    nfa = get_nfa()
    dfa = nfa_to_dfa(nfa)
    save_dfa(dfa)

    