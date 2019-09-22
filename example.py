def _init_ipython_printing(ip, stringify_func, use_latex, euler, forecolor,
                           backcolor, fontsize, latex_mode, print_builtin,
                           latex_printer, **settings):
    """Setup printing in IPython interactive session. """
    try:
        from IPython.lib.latextools import latex_to_png
    except ImportError:
        pass

    preamble = "\\documentclass[%s]{article}\n" \
               "\\pagestyle{empty}\n" \
               "\\usepackage{amsmath,amsfonts}%s\\begin{document}"
    if euler:
        addpackages = '\\usepackage{euler}'
    else:
        addpackages = ''
    preamble = preamble % (fontsize, addpackages)

    debug("init_printing: DVIOPTIONS:", dvioptions)
    debug("init_printing: PREAMBLE:", preamble)

    latex = latex_printer or default_latex

    def _print_plain(arg, p, cycle):
        """caller for pretty, for use in IPython 0.11"""
        if _can_print_latex(arg):
            p.text(stringify_func(arg))
        else:
            p.text(IPython.lib.pretty.pretty(arg))

    def _preview_wrapper(o):
        exprbuffer = BytesIO()
        try:
            preview(o, output='png', viewer='BytesIO',
                    outputbuffer=exprbuffer, preamble=preamble,
                    dvioptions=dvioptions)
        except Exception as e:
            # IPython swallows exceptions
            debug("png printing:", "_preview_wrapper exception raised:",
                  repr(e))
            raise
        return exprbuffer.getvalue()

    def _matplotlib_wrapper(o):
        # mathtext does not understand certain latex flags, so we try to
        # replace them with suitable subs
        o = o.replace(r'\operatorname', '')
        o = o.replace(r'\overline', r'\bar')
        # mathtext can't render some LaTeX commands. For example, it can't
        # render any LaTeX environments such as array or matrix. So here we
        # ensure that if mathtext fails to render, we return None.
        try:
            return latex_to_png(o)
        except ValueError as e:
            debug('matplotlib exception caught:', repr(e))
            return None

    def _can_print_latex(o):
        """Return True if type o can be printed with LaTeX.

        If o is a container type, this is True if and only if every element of
        o can be printed with LaTeX.
        """
        from sympy import Basic
        from sympy.matrices import MatrixBase
        from sympy.physics.vector import Vector, Dyadic
        if isinstance(o, (list, tuple, set, frozenset)):
            return all(_can_print_latex(i) for i in o)
        elif isinstance(o, dict):
            return all(_can_print_latex(i) and _can_print_latex(o[i]) for i in o)
        elif isinstance(o, bool):
            return False
        # TODO : Investigate if "elif hasattr(o, '_latex')" is more useful
        # to use here, than these explicit imports.
        elif isinstance(o, (Basic, MatrixBase, Vector, Dyadic)):
            return True
        elif isinstance(o, (float, integer_types)) and print_builtin:
            return True
        return False

    def _print_latex_png(o):
        """
        A function that returns a png rendered by an external latex
        distribution, falling back to matplotlib rendering
        """
        if _can_print_latex(o):
            s = latex(o, mode=latex_mode, **settings)
            try:
                return _preview_wrapper(s)
            except RuntimeError as e:
                debug('preview failed with:', repr(e),
                      ' Falling back to matplotlib backend')
                if latex_mode != 'inline':
                    s = latex(o, mode='inline', **settings)
                return _matplotlib_wrapper(s)

    def _print_latex_matplotlib(o):
        """
        A function that returns a png rendered by mathtext
        """
        if _can_print_latex(o):
            s = latex(o, mode='inline', **settings)
            return _matplotlib_wrapper(s)

    def _print_latex_text(o):
        """
        A function to generate the latex representation of sympy expressions.
        """
        if _can_print_latex(o):
            s = latex(o, mode='plain', **settings)
            s = s.replace(r'\dag', r'\dagger')
            s = s.strip('$')
            return '$$%s$$' % s

    def _result_display(self, arg):
        """IPython's pretty-printer display hook, for use in IPython 0.10

           This function was adapted from:

            ipython/IPython/hooks.py:155

        """
        if self.rc.pprint:
            out = stringify_func(arg)

            if '\n' in out:
                print

            print(out)
        else:
            print(repr(arg))

    import IPython
    if V(IPython.__version__) >= '0.11':
        from sympy.core.basic import Basic
        from sympy.matrices.matrices import MatrixBase
        from sympy.physics.vector import Vector, Dyadic
        printable_types = [Basic, MatrixBase, float, tuple, list, set,
                frozenset, dict, Vector, Dyadic] + list(integer_types)

        plaintext_formatter = ip.display_formatter.formatters['text/plain']

        for cls in printable_types:
            plaintext_formatter.for_type(cls, _print_plain)

        png_formatter = ip.display_formatter.formatters['image/png']
        if use_latex in (True, 'png'):
            debug("init_printing: using png formatter")
            for cls in printable_types:
                png_formatter.for_type(cls, _print_latex_png)
        elif use_latex == 'matplotlib':
            debug("init_printing: using matplotlib formatter")
            for cls in printable_types:
                png_formatter.for_type(cls, _print_latex_matplotlib)
        else:
            debug("init_printing: not using any png formatter")
            for cls in printable_types:
                # Better way to set this, but currently does not work in IPython
                #png_formatter.for_type(cls, None)
                if cls in png_formatter.type_printers:
                    png_formatter.type_printers.pop(cls)

        latex_formatter = ip.display_formatter.formatters['text/latex']
        if use_latex in (True, 'mathjax'):
            debug("init_printing: using mathjax formatter")
            for cls in printable_types:
                latex_formatter.for_type(cls, _print_latex_text)
        else:
            debug("init_printing: not using text/latex formatter")
            for cls in printable_types:
                # Better way to set this, but currently does not work in IPython
                #latex_formatter.for_type(cls, None)
                if cls in latex_formatter.type_printers:
                    latex_formatter.type_printers.pop(cls)

    else:
        ip.set_hook('result_display', _result_display)
