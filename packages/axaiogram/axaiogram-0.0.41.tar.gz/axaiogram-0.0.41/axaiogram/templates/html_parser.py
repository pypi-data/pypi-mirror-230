class HTMLTepmlateParser:
    def __init__(self, folder: str) -> None:
        self.folder = folder
        
    def parse(self, name: str, **kwargs):
        with open(f"{self.folder}/{name}", 'r') as f:
            content = f.read()
            return content.format(**kwargs)
        
