
class TreeNode:
    """Represents a node in the minimax tree"""
    def __init__(self, node_type, depth, col=None, score=None, alpha=None, beta=None, 
                 pruned=False, probability=None, cached=False):
        self.node_type = node_type
        self.depth = depth
        self.col = col
        self.score = score
        self.alpha = alpha
        self.beta = beta
        self.pruned = pruned
        self.probability = probability
        self.cached = cached  # Mark if retrieved from transposition table
        self.children = []
    
    def add_child(self, child):
        self.children.append(child)


def print_tree(node, prefix="", is_last=True, file=None):
    """Print the tree in a readable format"""
    connector = "└── " if is_last else "├── "
    
    label = f"{node.node_type}"
    
    if node.col is not None:
        label += f" [Col {node.col}]"
    
    if node.probability is not None:
        label += f" (p={node.probability:.2f})"
    
    if node.score is not None:
        label += f" Score: {node.score:.2f}" if isinstance(node.score, float) else f" Score: {node.score}"
    
    if node.alpha is not None or node.beta is not None:
        label += f" [α={node.alpha:.1f if node.alpha != float('-inf') and node.alpha != float('inf') else node.alpha}, β={node.beta:.1f if node.beta != float('-inf') and node.beta != float('inf') else node.beta}]"
    
    if node.cached:
        label += " 💾 CACHED"
    
    if node.pruned:
        label += " ✂️ PRUNED"
    
    print(prefix + connector + label, file=file)
    
    if node.children:
        extension = "    " if is_last else "│   "
        for i, child in enumerate(node.children):
            print_tree(child, prefix + extension, i == len(node.children) - 1, file)

