import json
from copy import deepcopy
import sys

class DFA:
    def __init__(self, dfa: dict):
        self.states = dfa['states']
        self.letters = dfa['letters']
        self.transition_function = dfa['transition_matrix']
        self.start_states = dfa['start_states']
        self.final_states = dfa['final_states']

    def make_gnfa(self):
        self.trans = {}
        # initliaze with phi
        for i in self.states:
            self.trans[i] = {}
            for j in self.states:
                self.trans[i][j] = 'ϕ'
        # add re to edge 
        for _from, ch, to in self.transition_function:
            if self.trans[_from][to] == 'ϕ':
                self.trans[_from][to] = ch
            else:
                self.trans[_from][to] += f'+{ch}'
        
        self.gnfa_start = 'Q#' + str(len(self.states)) 
        self.gnfa_final = 'Q#' + str(len(self.states) + 1)
        self.trans[self.gnfa_start] = {}
        self.trans[self.gnfa_final] = {}
        self.trans[self.gnfa_start][self.gnfa_final] = 'ϕ'
        for state in self.states:
            if state in self.start_states:
                self.trans[self.gnfa_start][state] = '$'
            else:
                self.trans[self.gnfa_start][state] = 'ϕ'

            if state in self.final_states:
                self.trans[state][self.gnfa_final] = '$'
            else:
                self.trans[state][self.gnfa_final] = 'ϕ'



    def get_dict(self):
        return {
            'states': self.states,
            'letters': self.letters,
            'transition_function': self.transition_function,
            'start_states': self.start_states,
            'final_states': self.final_states
        }
    
    def get_predecessors(self, state):
        result = []
        for key, val in self.trans.items():
            if key == state:
                continue
            if state in val and val[state] != 'ϕ':
                result.append(key)
        return result
    
    def get_successors(self, state):
        result = []
        for key, val in self.trans[state].items():
            if val != 'ϕ' and key != state:
                result.append(key)
        return result

    def add_brackets(self, x, y):
        # if self.trans[x][y] != 'ϕ' and self.trans[x][y] != '$':
        if self.trans[x][y] != 'ϕ':
            return str('(' + self.trans[x][y] + ')')
        else:
            return ''

    
    def reduced_state_trans(self, i, rip, j):
        # if (self.trans[i][rip] == '$' and self.trans[rip][j] == '$') or self.trans[i][j] == '$':
        #     return '$'
        # \eps in concate: ignore
        # r1:(i, rip)
        r1 = self.add_brackets(i, rip)
        # r2:(rip, rip)
        r2 = self.add_brackets(rip, rip)
        # r3:(rip, j)
        r3 = self.add_brackets(rip, j)
        # r4:(i, j)
        r4 = self.add_brackets(i, j)
        # res: (r1)(r2)*(r3)+(r4)
        if r2 != '':
            if r4 != '':
                res = (r1 + r2 + '*' + r3 + '+' + r4)
            else:
                res = (r1 + r2 + '*' + r3)            
        else:
            if r4 != '':
                res = (r1 + r3 + '+' + r4)
            else:
                res = (r1 + r3)            
        # print(f'i: {i}, rip: {rip}, j: {j}')
        # print(f'r1: {r1}')
        # print(f'r2: {r2}')
        # print(f'r3: {r3}')
        # print(f'res: {res}')
        return res
    

    def get_re(self):
        # single start and single finish state present
        self.make_gnfa()
        intermediate_states = self.states

        # print(self.trans)
        for rip in intermediate_states:
            predecessors = self.get_predecessors(rip)
            successors = self.get_successors(rip)
            # print(f'rip: {rip}\npredecessors: {predecessors}\nsuccessors: {successors}')
            temp_trans = deepcopy(self.trans)
            for i in predecessors:
                for j in successors:
                    temp_trans[i][j] = self.reduced_state_trans(i, rip, j)
            # remove rip from trans
            new_trans = {}
            for i, _next in temp_trans.items():
                if i == rip:
                    continue
                new_trans[i] = {}
                for j, re in _next.items():
                    if j == rip:
                        continue
                    new_trans[i][j] = re
            self.trans = deepcopy(new_trans)    
            # print(self.trans)
        return self.trans[self.gnfa_start][self.gnfa_final]

def get_dfa():
    input_file = str(sys.argv[1])
    with open(input_file, 'r') as f:
        data = json.load(f)
        return DFA(data)


def save_re(re: str):
    output_file = str(sys.argv[2])
    re_dic = {'regex': re}
    with open(output_file, 'w') as f:
        json.dump(re_dic, f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('incorrect input')
        print('Input format: python3 q3.py <input_file> <output_file>')
        exit()

    dfa = get_dfa()
    re = dfa.get_re()
    save_re(re)
