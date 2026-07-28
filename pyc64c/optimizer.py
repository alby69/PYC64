"""Optimizer — Optimization passes for PYC64 AST."""

def optimize_ast(ast):
    """
    Apply optimization passes to the AST.
    Current passes:
    - Constant folding
    - Loop Unrolling
    - Dead Code Elimination (DCE)
    """
    if ast is None:
        return None

    ast = fold_constants(ast)
    ast = unroll_loops(ast)
    ast = eliminate_dead_code(ast)
    return ast

def fold_constants(node):
    if node is None:
        return None

    # Process children first (bottom-up)
    if node['k'] == 'Program':
        for g in node.get('globals', []):
            fold_constants(g)
        for f in node.get('funcs', []):
            fold_constants(f)
    elif node['k'] == 'VarDecl':
        if node.get('init'):
            node['init'] = fold_constants(node['init'])
    elif node['k'] == 'FuncDecl':
        node['body'] = fold_constants(node['body'])
    elif node['k'] == 'Block':
        new_stmts = []
        for s in node.get('stmts', []):
            new_s = fold_constants(s)
            if new_s:
                new_stmts.append(new_s)
        node['stmts'] = new_stmts
    elif node['k'] == 'ExprStmt':
        node['expr'] = fold_constants(node['expr'])
    elif node['k'] == 'Assign':
        node['value'] = fold_constants(node['value'])
    elif node['k'] == 'If':
        node['cond'] = fold_constants(node['cond'])
        node['then'] = fold_constants(node['then'])
        if node.get('else'):
            node['else'] = fold_constants(node['else'])
    elif node['k'] == 'While':
        node['cond'] = fold_constants(node['cond'])
        node['body'] = fold_constants(node['body'])
    elif node['k'] == 'For':
        if node.get('init'): node['init'] = fold_constants(node['init'])
        if node.get('cond'): node['cond'] = fold_constants(node['cond'])
        if node.get('incr'): node['incr'] = fold_constants(node['incr'])
        node['body'] = fold_constants(node['body'])
    elif node['k'] == 'Return':
        if node.get('value'): node['value'] = fold_constants(node['value'])
    elif node['k'] == 'Call':
        new_args = []
        for a in node.get('args', []):
            new_args.append(fold_constants(a))
        node['args'] = new_args
    elif node['k'] == 'BinaryOp':
        node['left'] = fold_constants(node['left'])
        node['right'] = fold_constants(node['right'])

        # Try folding
        if node['left']['k'] == 'Literal' and node['right']['k'] == 'Literal':
            lval = node['left']['value']
            rval = node['right']['value']
            op = node['op']

            # Simple integer folding
            if isinstance(lval, (int, float)) and isinstance(rval, (int, float)):
                res = None
                if op == '+': res = lval + rval
                elif op == '-': res = lval - rval
                elif op == '*': res = lval * rval
                elif op == '/': res = lval // rval if rval != 0 else 0
                elif op == '//': res = lval // rval if rval != 0 else 0
                elif op == '%': res = lval % rval if rval != 0 else 0
                elif op == '&': res = int(lval) & int(rval)
                elif op == '|': res = int(lval) | int(rval)
                elif op == '^': res = int(lval) ^ int(rval)
                elif op == '<<': res = int(lval) << int(rval)
                elif op == '>>': res = int(lval) >> int(rval)
                elif op == '==': res = 1 if lval == rval else 0
                elif op == '!=': res = 1 if lval != rval else 0
                elif op == '<': res = 1 if lval < rval else 0
                elif op == '>': res = 1 if lval > rval else 0
                elif op == '<=': res = 1 if lval <= rval else 0
                elif op == '>=': res = 1 if lval >= rval else 0
                elif op == 'and': res = 1 if (lval and rval) else 0
                elif op == 'or': res = 1 if (lval or rval) else 0

                if res is not None:
                    kind = 'float' if isinstance(res, float) else 'int'
                    if op in ('==', '!=', '<', '>', '<=', '>=', 'and', 'or'):
                        kind = 'bool'
                    return {'k': 'Literal', 'value': res, 'kind': kind, '_type': node.get('_type', kind)}

    elif node['k'] == 'UnaryOp':
        node['operand'] = fold_constants(node['operand'])
        if node['operand']['k'] == 'Literal':
            val = node['operand']['value']
            op = node['op']
            if op == '-':
                return {'k': 'Literal', 'value': -val, 'kind': 'int', '_type': node.get('_type', 'int')}
            elif op == '!':
                return {'k': 'Literal', 'value': 0 if val else 1, 'kind': 'bool', '_type': 'bool'}

    return node

def unroll_loops(node):
    if node is None:
        return None

    k = node.get('k')
    # Recursively unroll children first (bottom-up)
    if k == 'Program':
        for g in node.get('globals', []):
            unroll_loops(g)
        new_funcs = []
        for f in node.get('funcs', []):
            new_f = unroll_loops(f)
            if new_f:
                new_funcs.append(new_f)
        node['funcs'] = new_funcs
    elif k == 'FuncDecl':
        node['body'] = unroll_loops(node['body'])
    elif k == 'Block':
        new_stmts = []
        for s in node.get('stmts', []):
            new_s = unroll_loops(s)
            if new_s:
                if new_s.get('k') == 'Block' and not new_s.get('is_unrolled'):
                    new_stmts.extend(new_s.get('stmts', []))
                else:
                    new_stmts.append(new_s)
        node['stmts'] = new_stmts
    elif k == 'VarDecl':
        if node.get('init'):
            node['init'] = unroll_loops(node['init'])
    elif k == 'Assign':
        node['value'] = unroll_loops(node['value'])
    elif k == 'While':
        node['cond'] = unroll_loops(node['cond'])
        node['body'] = unroll_loops(node['body'])
    elif k == 'If':
        node['cond'] = unroll_loops(node['cond'])
        node['then'] = unroll_loops(node['then'])
        if node.get('else'):
            node['else'] = unroll_loops(node['else'])
    elif k == 'Return':
        if node.get('value'): node['value'] = unroll_loops(node['value'])
    elif k == 'Call':
        node['args'] = [unroll_loops(arg) for arg in node.get('args', [])]
    elif k == 'BinaryOp':
        node['left'] = unroll_loops(node['left'])
        node['right'] = unroll_loops(node['right'])
    elif k == 'UnaryOp':
        node['operand'] = unroll_loops(node['operand'])
    elif k == 'For':
        init = node.get('init')
        cond = node.get('cond')
        incr = node.get('incr')
        body = node.get('body')

        if (init and init.get('k') == 'Assign' and init['target'].get('k') == 'Ident' and
            init['value'].get('k') == 'Literal' and isinstance(init['value']['value'], int) and
            cond and cond.get('k') == 'BinaryOp' and cond['op'] == '<' and cond['left'].get('k') == 'Ident' and
            cond['left']['name'] == init['target']['name'] and
            cond['right'].get('k') == 'Literal' and isinstance(cond['right']['value'], int)):

            loop_var = init['target']['name']
            start_val = init['value']['value']
            end_val = cond['right']['value']

            is_simple_incr = False
            if (incr and incr.get('k') == 'Assign' and incr['target'].get('k') == 'Ident' and
                incr['target']['name'] == loop_var and incr['value'].get('k') == 'BinaryOp' and
                incr['value']['op'] == '+' and incr['value']['left'].get('k') == 'Ident' and
                incr['value']['left']['name'] == loop_var and incr['value']['right'].get('k') == 'Literal' and
                incr['value']['right']['value'] == 1):
                is_simple_incr = True

            if is_simple_incr and (end_val - start_val) <= 4 and (end_val - start_val) > 0:
                unrolled_stmts = []
                import copy
                for val in range(start_val, end_val):
                    assign = {
                        'k': 'Assign',
                        'target': {'k': 'Ident', 'name': loop_var, 'line': node.get('line', 0)},
                        'value': {'k': 'Literal', 'kind': 'int', 'value': val, 'raw': str(val)},
                        'line': node.get('line', 0)
                    }
                    unrolled_stmts.append(assign)
                    copied_body = copy.deepcopy(body)
                    if copied_body.get('k') == 'Block':
                        unrolled_stmts.extend(copied_body.get('stmts', []))
                    else:
                        unrolled_stmts.append(copied_body)

                return {
                    'k': 'Block',
                    'stmts': unrolled_stmts,
                    'is_unrolled': True
                }
    return node

def eliminate_dead_code(ast):
    if ast is None:
        return None

    # 1. Simplify conditionals (constant if statements)
    ast = simplify_conditionals(ast)

    # 2. Prune local variables inside functions
    if ast.get('k') == 'Program':
        for f in ast.get('funcs', []):
            decls = set()
            refs = set()
            find_local_decls_and_refs(f.get('body'), decls, refs)
            for p in f.get('params', []):
                refs.add(p['name'])
            f['body'] = remove_unused_local_decls(f['body'], refs)

    # 3. Prune unused global variables and functions
    ast = eliminate_unused_globals_and_funcs(ast)

    return ast

def simplify_conditionals(node):
    if node is None:
        return None

    k = node.get('k')
    # First, simplify children recursively (bottom-up)
    if k == 'Program':
        for g in node.get('globals', []):
            simplify_conditionals(g)
        new_funcs = []
        for f in node.get('funcs', []):
            new_f = simplify_conditionals(f)
            if new_f:
                new_funcs.append(new_f)
        node['funcs'] = new_funcs
    elif k == 'FuncDecl':
        node['body'] = simplify_conditionals(node['body'])
    elif k == 'Block':
        new_stmts = []
        for s in node.get('stmts', []):
            new_s = simplify_conditionals(s)
            if new_s:
                if new_s.get('k') == 'Block':
                    new_stmts.extend(new_s.get('stmts', []))
                else:
                    new_stmts.append(new_s)
        node['stmts'] = new_stmts
    elif k == 'VarDecl':
        if node.get('init'):
            node['init'] = simplify_conditionals(node['init'])
    elif k == 'Assign':
        node['value'] = simplify_conditionals(node['value'])
    elif k == 'While':
        node['cond'] = simplify_conditionals(node['cond'])
        node['body'] = simplify_conditionals(node['body'])
    elif k == 'For':
        if node.get('init'): node['init'] = simplify_conditionals(node['init'])
        if node.get('cond'): node['cond'] = simplify_conditionals(node['cond'])
        if node.get('incr'): node['incr'] = simplify_conditionals(node['incr'])
        node['body'] = simplify_conditionals(node['body'])
    elif k == 'Return':
        if node.get('value'): node['value'] = simplify_conditionals(node['value'])
    elif k == 'Call':
        node['args'] = [simplify_conditionals(arg) for arg in node.get('args', [])]
    elif k == 'BinaryOp':
        node['left'] = simplify_conditionals(node['left'])
        node['right'] = simplify_conditionals(node['right'])
    elif k == 'UnaryOp':
        node['operand'] = simplify_conditionals(node['operand'])
    elif k == 'If':
        node['cond'] = simplify_conditionals(node['cond'])
        node['then'] = simplify_conditionals(node['then'])
        if node.get('else'):
            node['else'] = simplify_conditionals(node['else'])

        cond = node['cond']
        if cond.get('k') == 'Literal':
            val = cond.get('value')
            is_truthy = bool(val) if val not in (0, '0', False) else False
            if is_truthy:
                return simplify_conditionals(node['then'])
            else:
                if node.get('else'):
                    return simplify_conditionals(node['else'])
                else:
                    return None
    return node

def find_local_decls_and_refs(node, decls, refs):
    if node is None:
        return
    k = node.get('k')
    if k == 'VarDecl':
        decls.add(node['name'])
        if node.get('init'):
            find_local_decls_and_refs(node['init'], decls, refs)
    elif k == 'Ident':
        refs.add(node['name'])
    elif k == 'ArrayAccess':
        refs.add(node['name'])
        find_local_decls_and_refs(node.get('idx'), decls, refs)
    elif isinstance(node, dict):
        for v in node.values():
            if isinstance(v, dict):
                find_local_decls_and_refs(v, decls, refs)
            elif isinstance(v, list):
                for item in v:
                    find_local_decls_and_refs(item, decls, refs)
    elif isinstance(node, list):
        for item in node:
            find_local_decls_and_refs(item, decls, refs)

def remove_unused_local_decls(node, used_refs):
    if node is None:
        return None
    k = node.get('k')
    if k == 'Block':
        new_stmts = []
        for s in node.get('stmts', []):
            if s.get('k') == 'VarDecl':
                if s['name'] not in used_refs:
                    if s.get('init') and has_side_effects(s['init']):
                        new_stmts.append({'k': 'ExprStmt', 'expr': s['init'], 'line': s.get('line', 0)})
                    continue
            simplified = remove_unused_local_decls(s, used_refs)
            if simplified:
                new_stmts.append(simplified)
        node['stmts'] = new_stmts
    elif isinstance(node, dict):
        for k_key, v in list(node.items()):
            if isinstance(v, dict):
                node[k_key] = remove_unused_local_decls(v, used_refs)
            elif isinstance(v, list):
                new_list = []
                for item in v:
                    simplified_item = remove_unused_local_decls(item, used_refs)
                    if simplified_item:
                        new_list.append(simplified_item)
                node[k_key] = new_list
    return node

def has_side_effects(node):
    if node is None:
        return False
    k = node.get('k')
    if k == 'Call':
        return True
    if isinstance(node, dict):
        return any(has_side_effects(v) for v in node.values() if isinstance(v, (dict, list)))
    if isinstance(node, list):
        return any(has_side_effects(item) for item in node)
    return False

def collect_used_symbols(node, used_vars, used_funcs):
    if node is None:
        return
    k = node.get('k')
    if k == 'Ident':
        used_vars.add(node['name'])
    elif k == 'Call':
        used_funcs.add(node['name'])
        for arg in node.get('args', []):
            collect_used_symbols(arg, used_vars, used_funcs)
    elif k == 'ArrayAccess':
        used_vars.add(node['name'])
        collect_used_symbols(node.get('idx'), used_vars, used_funcs)
    elif isinstance(node, dict):
        for v in node.values():
            if isinstance(v, dict):
                collect_used_symbols(v, used_vars, used_funcs)
            elif isinstance(v, list):
                for item in v:
                    collect_used_symbols(item, used_vars, used_funcs)
    elif isinstance(node, list):
        for item in node:
            collect_used_symbols(item, used_vars, used_funcs)

def eliminate_unused_globals_and_funcs(program):
    if program is None or program.get('k') != 'Program':
        return program

    used_vars = set()
    used_funcs = set()

    for f in program.get('funcs', []):
        collect_used_symbols(f.get('body'), used_vars, used_funcs)

    for g in program.get('globals', []):
        if g.get('init'):
            collect_used_symbols(g['init'], used_vars, used_funcs)

    new_globals = []
    for g in program.get('globals', []):
        if g['name'] in used_vars:
            new_globals.append(g)
    program['globals'] = new_globals

    while True:
        funcs_to_keep = []
        current_used_funcs = set()
        for f in program.get('funcs', []):
            if f['name'] == 'main' or f['name'] in used_funcs:
                collect_used_symbols(f.get('body'), used_vars, current_used_funcs)
                funcs_to_keep.append(f)

        if len(funcs_to_keep) < len(program.get('funcs', [])):
            program['funcs'] = funcs_to_keep
            used_funcs = current_used_funcs
        else:
            break

    return program
