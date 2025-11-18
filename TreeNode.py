class TreeNode:
    """Represents a node in the minimax tree"""
    def __init__(self, node_type, depth, col=None, score=None, alpha=None, beta=None, pruned=False, probability=None):
        self.node_type = node_type  # 'MAX', 'MIN', 'CHANCE', 'LEAF'
        self.depth = depth
        self.col = col  # Column choice
        self.score = score
        self.alpha = alpha
        self.beta = beta
        self.pruned = pruned
        self.probability = probability  # For expectiminimax
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)


def print_tree(node, prefix="", is_last=True, file=None):
    """Print the tree in a readable format"""
    # Node symbol
    connector = "└── " if is_last else "├── "
    
    # Build node label
    label = f"{node.node_type}"
    
    if node.col is not None:
        label += f" [Col {node.col}]"
    
    if node.probability is not None:
        label += f" (p={node.probability:.2f})"
    
    if node.score is not None:
        label += f" Score: {node.score:.2f}" if isinstance(node.score, float) else f" Score: {node.score}"
    
    if node.alpha is not None or node.beta is not None:
        label += f" [α={node.alpha:.1f if node.alpha != float('-inf') and node.alpha != float('inf') else node.alpha}, β={node.beta:.1f if node.beta != float('-inf') and node.beta != float('inf') else node.beta}]"
    
    if node.pruned:
        label += " ✂️ PRUNED"
    
    # Print current node
    print(prefix + connector + label, file=file)
    
    # Print children
    if node.children:
        extension = "    " if is_last else "│   "
        for i, child in enumerate(node.children):
            print_tree(child, prefix + extension, i == len(node.children) - 1, file)

def print_board_state(board, indent=""):
    """Print the board state as a matrix with 0, 1, 2 values"""
    print(f"{indent}Board State (0=Empty, 1=Human/Red, 2=AI/Yellow):")
    print(f"{indent}┌─────────────────────┐")
    for row in board.board:
        row_str = " ".join(str(cell) for cell in row)
        print(f"{indent}│ {row_str} │")
    print(f"{indent}└─────────────────────┘")

def print_tree_node(depth, col, score, is_maximizing, indent_level=0):
    """Print a tree node vertically"""
    indent = "  " * indent_level
    player_type = "MAX (AI)" if is_maximizing else "MIN (Human)"
    print(f"{indent}{'│' if indent_level > 0 else ''}├─ Depth {depth}, Col {col if col is not None else 'ROOT'}, {player_type}")
    print(f"{indent}{'│' if indent_level > 0 else ''}   Score: {score:.2f}")
