import dataclasses
import engine.events.event_return as er
from engine import util
from engine.events.handler_template import EventData
from engine.config.constants import ENGINE_INTERNAL


@dataclasses.dataclass
class StackFrame:
    # default_factory=dict/listStackFrame
    stmts: list
    variables: dict = dataclasses.field(default_factory=dict)
    in_block: bool = False
    hoist_collector: list = dataclasses.field(default_factory=list) # variable_declPython/ABC/ block 
    index: int = 0
    to_delete_indices: list = dataclasses.field(default_factory=list) 

def remove_unnecessary_tmp_variables(data: EventData):
    """
    
    UNFLATTENED_GIR_LIST_GENERATEDGIR
    
    """
    in_data = data.in_data
    recursive_remove_tmp_vars(in_data)
    data.out_data = in_data

def recursive_remove_tmp_vars(obj):
    """
    GIR
    
    
    """
    if isinstance(obj, list):
        # 
        remove_unnecessary_tmp_variables_in_list(obj)
        # 
        for item in obj:
            recursive_remove_tmp_vars(item)
    elif isinstance(obj, dict):
        # 
        for value in obj.values():
            recursive_remove_tmp_vars(value)

def extract_stmt_info(stmt_dict):
    """
    GIR
    UNFLATTENEDGIR : {"": {}}
    : {"assign_stmt": {"target": "x", "operand": "y"}}
    Returns:
        tuple: (, ) (None, None)
    """
    if not isinstance(stmt_dict, dict) or not stmt_dict:
        return None, None
    op = list(stmt_dict.keys())[0]
    content = stmt_dict[op]
    return (op, content) if isinstance(content, dict) else (None, None)

def remove_unnecessary_tmp_variables_in_list(stmts: list):
    """
    
    
    
       %v1 = expr; ...; d = %v1  d = expr; ...
    
    
      1.  d = %v1 
      2.  %v1 
      3. 
         -  variable_decl
         -  %v1 
         - 
    """
    if len(stmts) < 2:
        return
    
    # 
    CAN_OPTIMIZE_OPS = {
        "array_read", "assign_stmt", "call_stmt", "addr_of", 
        "field_read", "asm_stmt", "mem_read", "type_cast_stmt", "new_object"
    }
    
    # 
    for i in range(len(stmts) - 1, 0, -1):
        curr_op, curr_content = extract_stmt_info(stmts[i])
        if (curr_op != "assign_stmt" 
            or not curr_content 
            or curr_content.get("operand2") 
            or curr_content.get("operator")):
            continue
        
        final_target = curr_content.get("target")
        temp_var = curr_content.get("operand")
        
        if (not temp_var or not temp_var.startswith(ENGINE_INTERNAL.VARIABLE_DECL_PREF)):
            continue

        """
         %v1 = expr; ...; d = %v1  d = expr; ...
        013
        """
        LOOKBACK_LIMIT = 3
        search_limit = max(-1, i - 1 - LOOKBACK_LIMIT)
        found_optimization = False
        
        for k in range(i - 1, search_limit, -1):
            prev_op, prev_content = extract_stmt_info(stmts[k])
            if not prev_op:
                break 
            if prev_op == "variable_decl":
                continue
            prev_target = prev_content.get("target")
            if (prev_target == temp_var 
                and prev_op in CAN_OPTIMIZE_OPS):
                prev_content["target"] = final_target
                del stmts[i]
                found_optimization = True
                break
            break #


def adjust_variable_decls(data: EventData):
    """
    
    """
    #  GIR 
    remove_unnecessary_tmp_variables(data)
    
    out_data = data.in_data
    is_python_like = data.lang in ["python", "abc"] #  Python  ABC 
    global_stmts_to_insert = []

    stack = [StackFrame(stmts=out_data)]

    while stack:
        frame = stack[-1] 

        # ===  1:  ===
        if frame.index >= len(frame.stmts):
            stack.pop() # 
            finalize_frame(frame, is_python_like)
            continue

        # ===  2:  ===
        stmt = frame.stmts[frame.index]
        current_stmt_index = frame.index
        frame.index += 1 

        if not isinstance(stmt, dict):
            continue
        
        key = list(stmt.keys())[0]
        value = stmt[key]

        # ===  3:  () ===
        sub_frames = []
        
        '''       
         class/interface/record/enum/struct...
         methods/fields/nested
          StackFrame(stmts=...) 
         '''
        if key in ("class_decl", "interface_decl", "record_decl", "annotation_type_decl", "enum_decl", "struct_decl"):
            for sub_key in ["methods", "fields", "nested"]:
                if sub_key in value and value[sub_key]:
                    sub_frames.append(StackFrame(stmts=value[sub_key]))

        elif key == "method_decl":
            # method_vars   
            method_vars: dict = {}
            if "parameters" in value:
                for param in value["parameters"]:
                    if isinstance(param, dict):
                        p_key = list(param.keys())[0]
                        if p_key == "parameter_decl":
                            method_vars[param[p_key]["name"]] = True
            
            if "body" in value and value["body"]:
                sub_frames.append(StackFrame(stmts=value["body"], variables=method_vars))
 
        elif key == "variable_decl":
            process_variable_decl(frame, value, current_stmt_index, is_python_like, global_stmts_to_insert)

        elif key in ("global_stmt", "nonlocal_stmt"):
            name = value.get("name")
            if name in frame.variables:
                util.error(f"global or nonlocal variable <{name}> has defined!")
            else:
                frame.variables[name] = True

        elif key.endswith("_stmt"):
            for sub_key, sub_val in value.items():
                if sub_key.endswith("body") and isinstance(sub_val, list) and sub_val:
                    # Python/ABC: block“/”collector
                    # : blockblockcollector
                    next_collector = frame.hoist_collector if is_python_like else []
                    sub_frames.append(StackFrame(
                        stmts=sub_val, 
                        variables=frame.variables, 
                        in_block=True, 
                        hoist_collector=next_collector
                    ))

        # ===  4:  ===
        if sub_frames:
            # 
            for sub_frame in reversed(sub_frames):
                stack.append(sub_frame)

    # 
    for stmt in global_stmts_to_insert:
        out_data.insert(0, stmt)

    data.out_data = out_data
    return er.EventHandlerReturnKind.SUCCESS


def process_variable_decl(frame: StackFrame, value: dict, index: int, is_python_like: bool, global_stmts: list):
    """"""
    name = value.get("name")
    attrs = value.get("attrs", [])
    
    if is_python_like:
        if name in frame.variables:
            frame.to_delete_indices.append(index)
        else:
            frame.variables[name] = True
            # Python/ABC:  ( block )
            frame.to_delete_indices.append(index)
            if frame.hoist_collector is not None:
                frame.hoist_collector.append({"variable_decl": value})
    else:
        if "var" in attrs:
            if name in frame.variables:
                frame.to_delete_indices.append(index)
            else:
                frame.variables[name] = True
                frame.to_delete_indices.append(index)
                if frame.hoist_collector is not None:
                    frame.hoist_collector.append({"variable_decl": value})
        
        elif "global" in attrs:
            if name in frame.variables:
                frame.to_delete_indices.append(index)
            else:
                frame.variables[name] = True
                frame.to_delete_indices.append(index)
                global_stmts.append({"variable_decl": value})
                
        elif "let" in attrs or "const" in attrs:
            if name in frame.variables and frame.variables.get(name) is False:
                frame.to_delete_indices.append(index)
            else:
                frame.variables[name] = False


def finalize_frame(frame: StackFrame, is_python_like: bool):
    """"""
    stmts = frame.stmts
    
    # 1. 
    for idx in sorted(frame.to_delete_indices, reverse=True):
        if idx < len(stmts):
            stmts.pop(idx)

    # 2. 
    if is_python_like:
        # Python/ABC:  block  (/) 
        if not frame.in_block and frame.hoist_collector:
            for stmt in frame.hoist_collector:
                stmts.insert(0, stmt)
            frame.hoist_collector.clear()
    else:
        # Other:  ( Block )
        if frame.hoist_collector:
            for stmt in frame.hoist_collector:
                stmts.insert(0, stmt)
    
    # 3. block  let/const 
    if not is_python_like and frame.in_block:
        vars_to_remove = [k for k, v in frame.variables.items() if v is False]
        for k in vars_to_remove:
            del frame.variables[k]
