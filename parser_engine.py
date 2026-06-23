import ast 
import os 
import json 
def analyze_python_file(file_path , base_dir):
    """
    Parses a single Python file to extract top-level 
    imports, classes, and functions.
    """
    with open(file_path , "r",encoding="utf-8")as f:
        try:
            tree = ast.parse(f.read())
        except SyntaxError:
            return  None
    
    file_info ={
        "file":os.path.relpath(file_path,base_dir).replace('\\','/'),
        "imports":[],
        "classes":[],
        "functions":[]
    }
    for node in ast.walk(tree):
        if isinstance(node,ast.Import): #captures the satndard imports
            for n in node.names:
                file_info["imports"].append(n.name)
        
        elif isinstance(node,ast.ImportFrom):
            if node.module:
                file_info["imports"].append(node.module)
        
        elif isinstance(node, ast.ClassDef):
            file_info["classes"].append(node.name)

        elif isinstance(node,ast.FunctionDef):
            file_info["functions"].append(node.name)
    return file_info        


def scan_repo(repo_path):
    """
    for walking through repository 
    """
    repo_report=[]
    for root,_,files in os.walk(repo_path):
        for file in files:
            if "venv" in root or ".git" in root:
                continue
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                analysis = analyze_python_file(full_path, repo_path)
                if analysis:
                    repo_report.append(analysis)
    return repo_report

if __name__ == "__main__":
    # Test the parser engine on its own directory
    print("Testing parser engine on current directory...")
    current_dir = os.path.dirname(os.path.abspath(__file__)) if os.path.dirname(os.path.abspath(__file__)) else "."
    result = scan_repo(current_dir)
    print(json.dumps(result, indent=2))