"""
Post Correspondence Problem (PCP) Puzzle Game
==============================================
Redesigned GUI - clean layout with no overlapping elements
- Top toolbar: title + difficulty + action buttons on separate rows
- Sidebar pool + main work area
- BFS guarantees solvability with minimum moves requirement
- Drag-and-drop interface with hint system
"""

import pygame
import sys
from game import PCPGame

def main():
    pygame.init()
    game = PCPGame()
    game.run()

if __name__ == '__main__':
    main()