import itertools
import json
from copy import deepcopy
import sys

class DSU:
    def __init__(self, nodes):
        self._disjoint_set = [[node] for node in set(nodes)]

    def _get_index(self, item):
        for s in self._disjoint_set:
            for _item in s:
                if _item == item:
                    return self._disjoint_set.index(s)
        return None

    def find(self, item):
        for s in self._disjoint_set:
            if item in s:
                return s
        return None

    def find_set(self, item):
        s = self._get_index(item)
        return s+1 if s is not None else None

    def join(self, item1, item2):
        i = self._get_index(item1)
        j = self._get_index(item2)

        if i != j:
            self._disjoint_set[i] += self._disjoint_set[j]
            del self._disjoint_set[j]

    def get(self):
        return self._disjoint_set


class DFA:
    def __init__(self, dfa: dict):
        self.states = dfa['states']
        self.letters = dfa['letters']
        self.transition_function = dfa['transition_matrix']
        self.start_states = dfa['start_states']
        self.final_states = dfa['final_states']
        self.make_movements()

    def make_movements(self):
        self.move = {}
        for trans in self.transition_function:
            _from, letter, to = trans
            self.move[(_from, letter)] = to

    def get_dict(self):
        return {
            'states': self.states,
            'letters': self.letters,
            'transition_matrix': self.transition_function,
            'start_states': self.start_states,
            'final_states': self.final_states
        }

    def remove_unreachable(self):
        # run bfs and collect reachable states
        reachable_states = deepcopy(self.start_states)
        queue = deepcopy(self.start_states)
        while len(queue) > 0:
            curr = queue.pop(0)
            for ch in self.letters:
                if ((curr, ch) in self.move) and (self.move[(curr, ch)] not in reachable_states):
                    queue.append(self.move[(curr, ch)])
                    reachable_states.append(self.move[(curr, ch)])

        self.states = reachable_states
        self.final_states = [ s for s in self.final_states if s in reachable_states]

    def minimize(self):
        self.remove_unreachable()
        # running myhill nerode algorithm
        # step 1: mark (fin_state, !fin_state)
        marked_state_pairs = []
        for state in itertools.combinations(self.states, 2):
            if (state[0] in self.final_states) and (state[1] not in self.final_states):
                marked_state_pairs.append(deepcopy(state))
            elif (state[0] not in self.final_states) and (state[1] in self.final_states):
                marked_state_pairs.append(deepcopy(state))

        # step 2: spread the mark
        while True:
            flag = True
            for state in itertools.combinations(self.states, 2):
                if state in marked_state_pairs:
                    continue

                for ch in self.letters:
                    n0 = self.move[(state[0], ch)]
                    n1 = self.move[(state[1], ch)]
                    if (n0, n1) in marked_state_pairs or (n1, n0) in marked_state_pairs:
                        marked_state_pairs.append(state)
                        flag = False
                        break
            if flag:
                break

        # step 3: collect unmarked pairs and unite them
        dsu = DSU(deepcopy(self.states))
        for state in itertools.combinations(self.states, 2):
            if state not in marked_state_pairs:
                dsu.join(*state)

        # step 4: update start_states, final_states, transition
        start_states = []
        for new_state in dsu.get():
            for state in new_state:
                if state in self.start_states:
                    start_states.append(new_state)
                    break
        self.start_states = start_states

        final_states = []
        for new_state in dsu.get():
            for state in new_state:
                if state in self.final_states:
                    final_states.append(new_state)
                    break
        self.final_states = final_states

        self.transition_function = []
        for (curr, ch), _next in self.move.items():
            # remove unreachable states
            if curr not in self.states:
                continue
            if _next not in self.states:
                continue
            
            done = False
            for curr1, ch1, _next1 in self.transition_function:
                if sorted(curr1) == sorted(dsu.find(curr)) and ch1 == ch:
                    done = True
            if done:
                continue

            self.transition_function.append([
                dsu.find(curr),
                ch,
                dsu.find(_next)
            ])

        self.states = dsu.get()


def get_dfa():
    input_file = str(sys.argv[1])
    with open(input_file, 'r') as f:
        data = json.load(f)
        return DFA(data)


def save_dfa(dfa: DFA):
    output_file = str(sys.argv[2])
    with open(output_file, 'w') as f:
        json.dump(dfa.get_dict(), f, indent=4)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print('incorrect input')
        print('Input format: python3 q4.py <input_file> <output_file>')
        exit()

    dfa = get_dfa()
    dfa.minimize()
    save_dfa(dfa)
