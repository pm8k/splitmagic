from IPython.core.magic import Magics, magics_class, line_magic
from IPython.display import display_javascript
import pandas as pd
import redbaron
from IPython.core.magic_arguments import magic_arguments,argument, parse_argstring


def parse_func_args(func):
    args = func.arguments
    strlist = ["# declare function arguments for "+func.name]
    for arg in args:
        if arg.value != None:
            if type(arg)==redbaron.nodes.ListArgumentNode:
                newstr = arg.name.dumps() + ' = []'
            elif type(arg)==redbaron.nodes.DictArgumentNode:
                newstr = arg.name.dumps() + ' = {}'
            else:
                newstr = arg.name.dumps() + ' = ' + arg.value.dumps()
        else:
            newstr = arg.name.dumps() + ' ='
        strlist.append(newstr)

    finalstr = "\n".join(strlist)

    return finalstr

def find_func(red,func_name):
    for item in red:
        if type(item)==redbaron.nodes.DefNode:
            if item.name == func_name:
                return item

    return None


def group_extraction(bod,pattern):
    grouplist = []
    currentgroup = []
    for b in bod:
        if type(b)==redbaron.nodes.CommentNode:
            text = b.value
            if text[:len(pattern)]==pattern:
                grouplist.append(currentgroup)
                currentgroup = [b.dumps()]
            else:
                currentgroup.append(b.dumps())

        else:
            currentgroup.append(b.dumps())

    if len(currentgroup)>0:
        grouplist.append(currentgroup)

    return grouplist


def make_cell(s):

    display_javascript("""
    var t_cell = IPython.notebook.insert_cell_below()
    t_cell.set_text(  '{}');
    var t_index = IPython.notebook.get_cells().indexOf(t_cell);
    IPython.notebook.get_cell(t_index).render();
     """.format(s.replace('\n','\\n')), raw=True)


@magics_class
class SplitMagic(Magics):


    @magic_arguments()
    @argument(
        '-t','--target',action='append',help='derp'
    )
    @argument(
        '-f','--function',action='append',help='derp'
    )
    @argument(
        '-d','--delimiter',action='append',help='derp'
    )
    @line_magic
    def msplit(self, line):
        print line
        args = parse_argstring(self.msplit,line)
        print args
        if not args.target:
            raise ValueError('FF')
        if args.delimiter:
            delim = args.delimiter[0]
        else:
            delim='#%#'

        filename = args.target[0]
        shell=self.shell
        with open(filename, "r") as source_code:
            red = redbaron.RedBaron(source_code.read())
        # r = open('test.py','r')
        # t = ast.parse(r.read())
        if not args.function:
            outlist = group_extraction(red,delim)
            for stringlist in outlist[::-1]:
                string = "\n".join(stringlist)
                make_cell(string)
        else:
            func_name = args.function[0]
            func = find_func(red,func_name)

            # get everything BUT that function
            first_outlist=[]
            for item in red:
                if item!=func:
                    first_outlist.append(item.dumps())
            firstoutstr = "\n".join(first_outlist)

            # lets modify a copy of the function
            func = func.copy()

            # parse arguments
            argstr = parse_func_args(func)
            func.value.decrease_indentation(4)
            secondoutlist = group_extraction(func.value,delim)
            tocelllist = [firstoutstr,argstr]
            for stringlist in secondoutlist:
                string = "\n".join(stringlist)
                if string.strip('\n').strip(' ')!='':
                    tocelllist.append(string)

            for item in tocelllist[::-1]:
                make_cell(item)





def load_ipython_extension(ip):
    ip.register_magics(Splitmagic)
