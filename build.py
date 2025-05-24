import re
import os

def bundle_imported_file(source: str, pattern: str, replace_pattern: str):
    tags = re.findall(pattern.replace('*', '([^"]+)').format(r'([^"]+)'), source)
    total = """"""
    for i, src in enumerate(tags):
        r = None
        if type(src) is tuple:
            r = src[:-1]
            src = src[-1:][0]

        content = open(src.strip(), "r").read()
        total += content + "\n"

        p = pattern.format(src)
        if r != None:
            for x in r: p = p.replace("*", x, 1)
        
        if i == len(tags) - 1:
            source = source.replace(p, replace_pattern.format(total))
        else:
            source = re.sub(p, "", source)
    
    return source

def bundle_css(html):
    return re.sub(r'@import url\([^\)]+\);', '', bundle_imported_file(html, '<link rel="stylesheet" href="{}">', "<style>\n{}\n</style>"))

def bundle_js(html):
    return bundle_imported_file(html, '<script*src="{}"></script>', "<script>\n{}\n</script>")

def compress_js(html):
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    for script in scripts:
        html = html.replace(script, re.sub(r'\n}\n', r'\n};\n', script))
    return html

def parse_variable(src, key, name = None, n = 1):
    if name == None:
        name = "{" + key.replace("--", "").replace("let ", "").replace("const ", "").removeprefix("<").removesuffix(">").replace("-", "_") + "}"

    if "*" in key:
        return re.sub(key, name, src, n)
    
    return re.sub(rf"({re.escape(key)}\s*[:=]\s*)([^;]*)(;?)", rf"\1{name}\3", src, count=n)

def build_template(content: str) -> str:
    print(">> Building src")

    print("  | Bundling css")
    content = bundle_css(content)

    print("  | Bundling js")
    content = bundle_js(content)

    content = compress_js(content)

    print("  | Compressing src")
    content = re.sub(r" //.*", "", content)
    content = re.sub(r"/\*\*([\s\S]*?)\*/", "", content)
    content = content.replace("\\n", "\\\\n")
    content = re.sub(r"^\s+", "", content, flags=re.MULTILINE)
    content = re.sub(r">\s+<", "><", content)
    content = re.sub(r"\s+", " ", content).strip()
    content = re.sub(r'\\/', r'\\\\/', content)
    content = re.sub(r'\\\.', r'\\\\.', content)
    content = re.sub(r'\\\[', r'\\\\[', content)
    content = re.sub(r'\\\]', r'\\\\]', content)
    content = re.sub(r'\\\{', r'\\\\{', content)
    content = re.sub(r'\\\}', r'\\\\}', content)
    content = re.sub(r'\\s', r'\\\\s', content)
    content = content.replace("{", "{{").replace("}", "}}")

    print("  | Parsing variables")
    content = parse_variable(content, "let items")
    content = parse_variable(content, "--bg")
    content = parse_variable(content, "--item-width")
    content = parse_variable(content, "--item-height")
    content = parse_variable(content, "--item-zoom-scale")
    content = parse_variable(content, "--highlight")
    content = parse_variable(content, "--primary")
    content = parse_variable(content, "--font")
    content = parse_variable(content, "--accent")
    content = parse_variable(content, "<title>.*?</title>", "<title>{title}</title>")

    return content

def file_to_template(file):
    src = open(file, "r").read()
    return build_template(src)

def template_to_file(tmp, file):
    open(file, "w").write(tmp)

def replace_temp(file, src):
    file = file
    new = re.sub(r'return """.*?"""', 'return """--source--"""', open(file, "r").read(), re.DOTALL).replace("--source--", src)
    open(file, "w").write(new)

os.chdir("src")
replace_temp("../main.py", file_to_template("index.html"))