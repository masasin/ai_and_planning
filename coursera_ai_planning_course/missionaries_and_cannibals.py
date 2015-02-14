{
 "metadata": {
  "name": "",
  "signature": "sha256:066a03aca78a2391153334bcf3f6c3a9fdffc7267812efd6628fc41fca0b4763"
 },
 "nbformat": 3,
 "nbformat_minor": 0,
 "worksheets": [
  {
   "cells": [
    {
     "cell_type": "heading",
     "level": 1,
     "metadata": {},
     "source": [
      "The Problem"
     ]
    },
    {
     "cell_type": "markdown",
     "metadata": {},
     "source": [
      "*On one bank of a river are three missionaries (black triangles) and three cannibals (red circles). There is one boat available that can hold up to two people and that they would like to use to cross the river. If the cannibals ever outnumber the missionaries on either of the river\u2019s banks, the missionaries will get eaten. How can the boat be used to safely carry all the missionaries and cannibals across the river?*\n",
      "\n",
      "Try to implement the general search algorithm just described. You can use LIFO and FIFO as queuing strategies to determine the order in which nodes are explored. These two strategies are known as depth-first and breadth-first search respectively. Be careful, depth-first search may descend down infinite branches, so best implement a depth cut-off. Then, extend your implementation with a hash table that stores all the nodes found so far. Print out a trace of the states the algorithm finds (in the order they are discovered) and see how much of the search space each algorithm explores."
     ]
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "from collections import deque\n",
      "from copy import deepcopy"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [],
     "prompt_number": 147
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "class State:\n",
      "    def __init__(self, missionaries, cannibals, boat, num_missionaries=3, num_cannibals=3, capacity=2):\n",
      "        self.missionaries = missionaries\n",
      "        self.cannibals = cannibals\n",
      "        self.boat = boat\n",
      "        self._capacity = capacity\n",
      "        self._num_missionaries = num_missionaries\n",
      "        self._num_cannibals = num_cannibals\n",
      "        \n",
      "    def is_goal(self):\n",
      "        return self.missionaries == self.cannibals == self.boat == 0\n",
      "        \n",
      "    def get_children(self):\n",
      "        next_states = []\n",
      "        if self.boat:\n",
      "            boat = 0\n",
      "            sign = -1\n",
      "        else:\n",
      "            boat = sign = 1\n",
      "        for m in range(self._capacity + 1):\n",
      "            for c in range(self._capacity + 1):\n",
      "                if 0 < m + c <= self._capacity:\n",
      "                    new_state = State(self.missionaries + m * sign,\n",
      "                                      self.cannibals + c * sign,\n",
      "                                      boat,\n",
      "                                      num_missionaries=self._num_missionaries,\n",
      "                                      num_cannibals=self._num_cannibals,\n",
      "                                      capacity=self._capacity)\n",
      "                    if new_state.is_valid() and new_state not in next_states:\n",
      "                        next_states.append(new_state)\n",
      "                        action = \"{}:{}{}{}{}\".format(\"l\" if self.boat else \"r\",\n",
      "                                                      m if m else \"\",\n",
      "                                                      \"m\" if m else \"\",\n",
      "                                                      c if c else \"\",\n",
      "                                                      \"c\" if c else \"\")\n",
      "                        yield action, new_state\n",
      "    \n",
      "    def is_valid(self):\n",
      "        if not 0 <= self.missionaries <= self._num_missionaries\\\n",
      "            or not 0 <= self.cannibals <= self._num_cannibals:\n",
      "            return False\n",
      "        if self.cannibals > self.missionaries > 0:\n",
      "            return False\n",
      "        if self._num_cannibals - self.cannibals > self._num_missionaries - self.missionaries > 0:\n",
      "            return False\n",
      "        return True\n",
      "    \n",
      "    def __hash__(self):\n",
      "        return hash((self.missionaries, self.cannibals, self.boat))\n",
      "    \n",
      "    def __eq__(self, other):\n",
      "        return self.missionaries == other.missionaries\\\n",
      "            and self.cannibals == other.cannibals\\\n",
      "            and self.boat == other.boat\n",
      "    \n",
      "    def __repr__(self):\n",
      "        return \"State\" + str((self.missionaries, self.cannibals, self.boat))"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [],
     "prompt_number": 264
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "class Node:\n",
      "    def __init__(self, state, parent, action, depth):\n",
      "        self.state = state\n",
      "        self.parent = parent\n",
      "        self.action = action\n",
      "        self.depth = depth\n",
      "    \n",
      "    def expand(self):\n",
      "        for action, next_state in self.state.get_children():\n",
      "            next_node = Node(next_state, self, action, self.depth + 1)\n",
      "            yield next_node\n",
      "    \n",
      "    def get_path(self):\n",
      "        path = []\n",
      "        node = self\n",
      "        while node.parent is not None:\n",
      "            path.append(node)\n",
      "            node = node.parent\n",
      "        path.append(node)\n",
      "        return path[::-1]\n",
      "    \n",
      "    def __repr__(self):\n",
      "        return \"Node\" + str((self.state, self.parent, self.action, self.depth))"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [],
     "prompt_number": 265
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "class Tree:\n",
      "    \n",
      "    def __init__(self, root):\n",
      "        self.root = root\n",
      "    \n",
      "    def search(self, method, max_depth = -1):\n",
      "        seen = set()\n",
      "        fringe = deque([self.root])\n",
      "        num_expansions = 0\n",
      "        max_depth = max_depth\n",
      "        \n",
      "        while True:\n",
      "            if not fringe:\n",
      "                return\n",
      "            if method == \"fifo\":\n",
      "                node = fringe.popleft()\n",
      "            elif method == \"lifo\":\n",
      "                node = fringe.pop()\n",
      "            if node.state in seen:\n",
      "                continue\n",
      "            if node.depth > max_depth:\n",
      "                max_depth = node.depth\n",
      "            if node.state.is_goal():\n",
      "                solution = node.get_path()\n",
      "                return solution\n",
      "            num_expansions += 1\n",
      "            fringe.extend(node.expand())\n",
      "            seen.add(node.state)"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [],
     "prompt_number": 266
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [
      "initial_state = State(3, 3, 1, num_missionaries=3, num_cannibals=3, capacity=3)\n",
      "root = Node(initial_state, None, None, 0)\n",
      "tree = Tree(root)\n",
      "sol_fifo = tree.search(\"fifo\")\n",
      "sol_lifo = tree.search(\"lifo\")\n",
      "print(\"\\t\\tFIFO\\t\\t\\t\\tLIFO\")\n",
      "for i, (node_fifo, node_lifo) in enumerate(zip(sol_fifo, sol_lifo)):\n",
      "    print(i, node_fifo.action, node_fifo.state, \"\", node_lifo.action, node_lifo.state, sep=\"\\t\")"
     ],
     "language": "python",
     "metadata": {},
     "outputs": [
      {
       "output_type": "stream",
       "stream": "stdout",
       "text": [
        "\t\tFIFO\t\t\t\tLIFO\n",
        "0\tNone\tState(3, 3, 1)\t\tNone\tState(3, 3, 1)\n",
        "1\tl:2c\tState(3, 1, 0)\t\tl:1m1c\tState(2, 2, 0)\n",
        "2\tr:1c\tState(3, 2, 1)\t\tr:1m\tState(3, 2, 1)\n",
        "3\tl:3m\tState(0, 2, 0)\t\tl:3m\tState(0, 2, 0)\n",
        "4\tr:1c\tState(0, 3, 1)\t\tr:2m\tState(2, 2, 1)\n",
        "5\tl:3c\tState(0, 0, 0)\t\tl:2m1c\tState(0, 1, 0)\n"
       ]
      }
     ],
     "prompt_number": 276
    },
    {
     "cell_type": "code",
     "collapsed": false,
     "input": [],
     "language": "python",
     "metadata": {},
     "outputs": []
    }
   ],
   "metadata": {}
  }
 ]
}
