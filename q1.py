import json 
import sys

precedenceMap = {
  '*': 4,
  '.': 3,
  '+': 2
}

def precedenceOf(c):
    if c in precedenceMap:
        return precedenceMap[c]
    else:
        return 1

letters = None

class NFA: 
    def __init__(self, states = None, letters = None, transition_function = None, start_states = None, final_states = None):
        self.states = states
        self.letters = letters
        self.transition_function = transition_function
        self.start_states = start_states
        self.final_states = final_states
    
    def map_state(self, state: int):
        return 'Q' + str(state)

    def get_dict(self):
        return {
            'states': [self.map_state(state) for state in range(self.states)],
            'letters': [letter for letter in self.letters],
            'transition_matrix': [(self.map_state(trans[0]), trans[1], self.map_state(trans[2])) 
                                        for trans in self.transition_function],
            'start_states': [self.map_state(state) for state in self.start_states],
            'final_states': [self.map_state(state) for state in self.final_states]
        }

class ConvertNFA:
    @classmethod
    def single_state(self, ch: str):
        trans = [(0, ch, 1)]
        return NFA(2, letters, trans, [0], [1])

    @classmethod
    def apply_star(self, nfa: NFA):
        new_state = nfa.states
        nfa.states += 1
        for start_state in nfa.start_states:
            nfa.transition_function.append((new_state, '$', start_state))
        
        for finish_state in nfa.final_states:
            nfa.transition_function.append((finish_state, '$', new_state))

        nfa.start_states = [new_state]
        nfa.final_states = [new_state]
        return nfa      

    @classmethod
    def apply_union(self, nfa1: NFA, nfa2: NFA):
        # index shifting of nfa2 states
        delta = nfa1.states
        nfa2.final_states = [delta + i for i in nfa2.final_states]
        nfa2.start_states = [delta + i for i in nfa2.start_states]
        nfa2.transition_function = [ (delta + t[0], t[1], delta + t[2])
                                        for t in nfa2.transition_function]

        nfa = NFA()  
        nfa.states = nfa1.states + nfa2.states + 1
        nfa.letters = letters
        nfa.start_states = [nfa.states - 1]
        nfa.final_states = nfa1.final_states + nfa2.final_states
        nfa.transition_function = nfa1.transition_function + nfa2.transition_function
        for start_state in nfa1.start_states:
            nfa.transition_function.append((nfa.start_states[0], '$', start_state))
        for start_state in nfa2.start_states:
            nfa.transition_function.append((nfa.start_states[0], '$', start_state))        
        return nfa
    
    @classmethod
    def apply_concatenation(self, nfa1: NFA, nfa2: NFA):
        # index shifting of nfa2 states
        delta = nfa1.states
        nfa2.final_states = [delta + i for i in nfa2.final_states]
        nfa2.start_states = [delta + i for i in nfa2.start_states]
        nfa2.transition_function = [ (delta + t[0], t[1], delta + t[2])
                                        for t in nfa2.transition_function]
        
        nfa = NFA()  
        nfa.states = nfa1.states + nfa2.states
        nfa.letters = letters
        nfa.start_states = nfa1.start_states
        nfa.final_states = nfa2.final_states
        nfa.transition_function = nfa1.transition_function + nfa2.transition_function
        for state1 in nfa1.final_states:
            for state2 in nfa2.start_states:
                nfa.transition_function.append((state1, '$', state2))
        return nfa
    
    
class RE:
    def __init__(self, re: str):
        self.re = re
    
    def check_concat(self, c1: str, c2: str):
        if c1.isalnum() or c1 == ')' or c1 == '*' or c1 == '$':
            if c2.isalnum() or c2 == '(' or c2 == '$':
                return True
        return False

    def add_concatenation_operator(self, re: str):
        new_re = ''
        for i in range(len(re)):
            if (i + 1) < len(re) and self.check_concat(re[i], re[i+1]):
                new_re += (re[i] + '.')
            else:
                new_re += (re[i])
        return new_re
    
    def infix_to_posfix_re(self, re: str):
        postfix_re = []
        stack = []
        for c in re:
            if c.isalnum() or c == '$':
                postfix_re.append(c)
            elif c == '(':
                stack.append(c)
            elif c == ')':
                while stack[-1] != '(':
                    postfix_re.append(stack.pop())
                stack.pop() # '('
            else:
                while len(stack) > 0 and stack[-1] != '(' and\
                     precedenceOf(stack[-1]) >= precedenceOf(c):
                    postfix_re.append(stack.pop())
                stack.append(c)

        while len(stack) > 0:
            postfix_re.append(stack.pop())

        return ''.join(postfix_re)


def re_to_nfa(re: RE):
    global letters
    letters = set()
    for c in re.re:
        if c.isalnum() or c == '$':
            letters.add(c)
    letters = list(letters)
    
    re.re = re.add_concatenation_operator(re.re)
    # print('added concat operator: ', re.re) 
    
    re.re = re.infix_to_posfix_re(re.re)
    # print(f'post_fix_re: {re.re}')

    # a stack of NFAs
    stack = []
    for c in re.re:
        if c.isalnum() or c == '$':
            stack.append(ConvertNFA.single_state(c))
        elif c == '*':
            nfa = stack.pop()
            stack.append(ConvertNFA.apply_star(nfa))
        elif c == '+':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(ConvertNFA.apply_union(nfa1, nfa2))
        elif c == '.':
            nfa2 = stack.pop()
            nfa1 = stack.pop()
            stack.append(ConvertNFA.apply_concatenation(nfa1, nfa2))
    
    assert len(stack) == 1
    return stack[0]

def get_re():
    input_file = str(sys.argv[1])
    with open(input_file, 'r') as f:
        data = json.load(f)
        # print(f'input_re: {data["regex"]}')
        regex = str(data['regex'])
        return RE(regex)


def save_nfa(nfa: NFA):
    output_file = str(sys.argv[2])
    with open(output_file, 'w') as f:
        json.dump(nfa.get_dict(), f, indent=4)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('incorrect input')
        print('Input format: python3 q1.py <input_file> <output_file>')
        exit()

    re = get_re()
    nfa = re_to_nfa(re)
    save_nfa(nfa)
