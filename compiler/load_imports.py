import parse
import os.path

def load_imports(lib_dir, filename):
    dir, name = filename.rsplit('/', 1)
    assert name.endswith('.plst')
    name = name[:-5]

    def load_module(module_name):
        module_name = module_name.replace('.', '/')
        try:
            filename = os.path.join(lib_dir, module_name) + '.plst'
            with open(filename, 'r') as fd:
                source = fd.read()
        except IOError:
            filename = os.path.join(dir, module_name) + '.plst'
            with open(filename, 'r') as fd:
                source = fd.read()
        try:
            return parse.parser.parse(source)
        except:
            print filename
            raise

    modules = {}
    to_load = [name]
    while to_load:
        module = to_load.pop()
        if not module in modules:
            m = load_module(module)
            modules[module] = m
            to_load.extend(m.imports)

    done = set()
    ordered_modules = []

    while modules:
        loop = True
        for module_name, module in modules.items():
            if set(module.imports) <= done:
                del modules[module_name]
                ordered_modules.append((module_name, module))
                done.add(module_name)
                loop = False
        if loop:
            raise Exception('import loop')

    return (name, ordered_modules)
