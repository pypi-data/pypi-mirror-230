# The utiliy of dataset managment for ai development.
from typing import List, Callable
from collections import namedtuple, defaultdict
from pathlib import Path
from dataclasses import dataclass
from itertools import chain

__all__ = [
    'DataSource',
    'Parse_inst',
    'get_src_path'
]

@dataclass
class DataSource:
    path : str
    name_lst : List[str]  # support multiple instance in same path
    ext_lst : List[str]
    field : List[str] # len(field) == len(name_lst)
    make_label : Callable = None  # contains new field in this callback
    
    # Support asymmetric num of args between name_lst and ext_lst
    def __post_init__(self):
        # auto-convert to the valid args
        if len(self.name_lst) != len(self.ext_lst):
            if not (len(self.name_lst) == 1 or len(self.ext_lst) == 1):
                raise ValueError("Failed to conversion")

            # unary trick for finding max, min len lst in special case
            mx_lst, mn_lst = (self.name_lst, self.ext_lst) \
                                if len(self.name_lst) > len(self.ext_lst) \
                                    else (self.ext_lst, self.name_lst)
            # copy str by python side-effect!
            cp_val = mn_lst.pop()
            [ mn_lst.append(cp_val) for _ in mx_lst ]

    def __iter__(self):
        return zip(self.field, self.name_lst, self.ext_lst)


@dataclass
class Parse_inst:
    parse_ext : str
    file_loader : Callable
    file_parser_callbk : Callable
    js_qry_dct : dict = None

    def __post_init__(self):
        if self.js_qry_dct and self.parse_ext!='json':
            raise RuntimeError("The js_qry_dct only allow to query the json file!")


def meta_file_handler(src_path, src_dct, parse_inst):
    # qry parser e.g. ("attributes.weather", "attributes.timeofday")
    def qry_js_dct(qry_dct, js_dct, tmp_res):
        for field, qry_str in qry_dct.items():
            t_dct = js_dct
            for qry in qry_str.split('.'):
                t_dct = t_dct[qry]
            tmp_res[field].append(t_dct)

    with src_path.open('r') as js_ptr:
        js_dct = parse_inst.file_loader(js_ptr)
        
        # parser each line in js_dct into qry_res to keep order!
        if parse_inst.js_qry_dct:
            tmp_res = defaultdict(list)
            for dct in js_dct:
                qry_js_dct(parse_inst.js_qry_dct, dct, tmp_res)

            # flatten vectors into a tuples, zip type is good to lazy eval!
            # you can roll-out zip by for-loop or list(.)
            callbk_input = zip(*tmp_res.values())
        else:
            # whatever it readout by the setting backend, 
            #  s.t. json.load -> (dict, list), csv.load -> list, ..., etc
            callbk_input = js_dct
        
        file_dct = parse_inst.file_parser_callbk(callbk_input) 
        src_dct.update(file_dct)

    return list(file_dct.keys())

def get_src_path(
        rt_dir : str, 
        ds_src_lst : List[DataSource],
        parse_lst : list = [],
        sort_path : bool = True,
        sort_kwargs : dict = {},
        ret_dict : bool = True
    ) -> List[tuple]:
    '''
    # Rewrite doc-string!
    Input : 
        rt_dir : root dir of dataset. 
        ds_type : the way to structure data source, support following type :
            1. imfd (ImageFolder mode), the name of subfolder indicate 'label',
                all image under subfolder is regarded as 'path'. 
                should given field_str 'path, label'
            2. pair (Paired data mode), several combination of data source,
                it could give different path to indicate different source.
                e.g. path_lst ['/ds/img/tra', '/ds/lab/tra', '/ds/lab/msk']
                     name_lst ['*', '*', '*']
                     src_type ['jpg', 'jpg', 'png']
            3. js (parse json file), 
    Output : 
        all_dict, all items pkg into dict with corresponding keys
        namedtuple, 'path', 'label' is default fields with support following function : 
            1. 'path, other_path, label' return (path, other_path, label), 
                other_path could be 'msk_path', 'inst_path', ..., etc.
            2. 'path' return (path) to support unsupervised learning.
    '''
    def chk_empty_glob(dct, field):
        fed_lst = field if isinstance(field, list) else [field]
        for fed in fed_lst:
            if len(dct[fed]) == 0:
                tmp_path = str(src_dir / src_tmplt)
                raise RuntimeError(f"field : {fed}, glob path : '{tmp_path}' glob nothing!")

    all_dct = {}   
    for ds_src in ds_src_lst:
        dct = defaultdict(list)
        src_dir = Path(rt_dir) / ds_src.path
        for fed, src_name, src_type in ds_src:

            src_tmplt = f"{src_name}.{src_type}"
            for src_path in src_dir.rglob(src_tmplt):

                src_ext = src_path.suffix[1:]
                parse_ext_lst = [ inst.parse_ext for inst in parse_lst]
                if src_ext in parse_ext_lst:
                    idx = parse_ext_lst.index(src_ext)
                    # inplace update dct, return fed as list to record updated fields
                    fed = meta_file_handler(src_path, dct, parse_lst[idx])
                else:
                    dct[fed].append(str(src_path))

            chk_empty_glob(dct, fed)
               
        # make_label from any key in the same DataSource !
        if ds_src.make_label:
            lab_dct = ds_src.make_label(dct)
            dct.update(lab_dct)

        # merge to all_dict, warning about key override issue ~
        all_dct.update(dct)

    if sort_path:
        for lst in all_dct.values():
            lst.sort(**sort_kwargs)
        
    return all_dct

    ds_lst = []
    DS_tuple = namedtuple('DS_tuple', all_dct.keys())
    for tmp_lst in zip(*all_dct.values()):
        ds_pair = DS_tuple._make(tmp_lst)
        ds_lst.append(ds_pair)

    return ds_lst

# Let us arrange path for 3 dataset with different structure in 118 lines!
#   (and most of lines come from a wierd requirement of dataset!)
# originally, it should write in few hunder-lines of code!!
if __name__ == "__main__":
    ...
    