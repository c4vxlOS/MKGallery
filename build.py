import re
import os

def bundle_imported_code(source: str, pattern: str, replace_pattern: str):
    tags = re.findall(pattern.replace('*', '([^"]+)').format(r'([^"]+)'), source)
    for src in tags:
        r = None
        if type(src) is tuple:
            r = src[:-1]
            src = src[-1:][0]
        print(src.strip())
        content = open(src.strip(), "r").read()
        p = pattern.format(src)
        if r != None:
            for x in r:
                p = p.replace("*", x, 1)
        print(f"Bundling {p}")
        source = source.replace(p, replace_pattern.format(content))
    
    return source

def bundle_css(html):
    return re.sub(r'@import url\([^\)]+\);', '', bundle_imported_code(html, '<link rel="stylesheet" href="{}">', "<style>\n{}\n</style>"))

def bundle_js(html):
    return bundle_imported_code(html, '<script*src="{}"></script>', "<script>\n{}\n</script>")

def compress_js(html):
    scripts = re.findall(r'<script>(.*?)</script>', html, re.DOTALL)
    for script in scripts:
        html = html.replace(script, re.sub(r'\}\n(?!\s*[\];])', "};", script))
    return html

def interprete(content):
    print(">> Interpreting src")

    print("  | Bundling css")
    print("  | Bundling js")
    content = bundle_js(bundle_css(content))

    print("  | Compressing js")
    content = compress_js(content)

    print("  | Compressing src")
    content = re.sub(r" //.*", "", content)
    content = content.replace("\\n", "\\\\n")
    content = re.sub(r"^\s+", "", content, flags=re.MULTILINE)
    content = re.sub(r">\s+<", "><", content)
    content = re.sub(r"\s+", " ", content).strip()
    content = content.replace("{", "{{").replace("}", "}}")

    # Change vars
    content = re.sub(r"<title>.*?</title>", "<title>{title}</title>", content)
    content = re.sub(r"--bg: .*?;", "--bg: {bg};", content)
    content = re.sub(r"--text: .*?;", "--text: {text};", content)
    content = re.sub(r"--primary: .*?;", "--primary: {primary};", content)
    content = re.sub(r"--secondary: .*?;", "--secondary: {secondary};", content)
    content = re.sub(r"--font: .*?;", "--font: {font};", content)
    content = re.sub(r"--max-width: .*?;", "--max-width: {max_width};", content)
    content = re.sub(r"--font: .*?;", "--font: {font};", content)
    content = re.sub(r"let items = .*?;", "let items = {urls};", content, 1)
    print()
    return content

def interprete_file(file):
    return interprete(open(file, "r").read())

def replace_temp(file, src):
    file = file
    new = re.sub(r'return """.*?"""', 'return """--source--"""', open(file, "r").read(), re.DOTALL).replace("--source--", src)
    open(file, "w").write(new)

def compile_to_template(file):
    extension = file.split(".")[-1:][0]
    name = ".".join(file.split(".")[:-1])
    open(f"{name}_template.{extension}", "w").write(interprete_file(file))

os.chdir("src")

replace_temp("../index.py", interprete_file("index.html"))