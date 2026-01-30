#!/usr/bin/env python3
import copy
from engine.common_structs import AccessPoint, State, ComputeFrame, Symbol
from engine.core.stmt_states import StmtStates
from engine.events.handler_template import EventData
from engine.config.constants import (
    EVENT_KIND,
    ENGINE_INTERNAL,
    STATE_TYPE_KIND,
    ENGINE_SYMBOL_KIND,
    ACCESS_POINT_KIND,
    ANALYSIS_PHASE_ID,
)
import engine.events.event_return as er
from engine.util import util
from engine.util.loader import Loader
from engine.config.constants import ENGINE_INTERNAL

def check_this_write(receiver_symbol, receiver_states, frame):
    this_flag = False
    if len(receiver_states) != 0:
        for each_receiver_state_index in receiver_states:
            each_receiver_state : State = frame.symbol_state_space[each_receiver_state_index]
            if hasattr(each_receiver_state, "data_type") and each_receiver_state.data_type == ENGINE_INTERNAL.THIS:
                this_flag = True
                break
    if receiver_symbol.name != ENGINE_INTERNAL.THIS and this_flag == False:
        return False
    return True

def write_to_this_class(data: EventData):
    in_data = data.in_data
    frame: ComputeFrame = in_data.frame
    status = in_data.status
    receiver_states = in_data.receiver_states
    receiver_symbol: Symbol = in_data.receiver_symbol
    field_states = in_data.field_states
    defined_symbol = in_data.defined_symbol
    stmt_id = in_data.stmt_id
    stmt = in_data.stmt
    state_analysis:StmtStates = in_data.state_analysis
    loader:Loader = frame.loader
    source_states = in_data.source_states
    defined_states = in_data.defined_states
    app_return = er.config_event_unprocessed()
    resolver = state_analysis.resolver
    if not check_this_write(receiver_symbol, receiver_states, frame):
        return app_return
    class_id = loader.convert_method_id_to_class_id(frame.method_id)
    class_members = loader.convert_class_id_to_members(class_id)
    for each_field_state_index in field_states:
        each_field_state = frame.symbol_state_space[each_field_state_index]
        if not isinstance(each_field_state, State):
            continue
        field_name = str(each_field_state.value)
        if len(field_name) == 0:
            continue
        # FIXME living graph
        class_members[field_name] = source_states
    loader.save_class_id_to_members(class_id, class_members)
    return app_return

def appstorage_read_and_write(data: EventData):
    frame: ComputeFrame = data.in_data.frame
    name_states = data.in_data.name_states
    args = data.in_data.args
    space = data.in_data.space
    positional_args = args.positional_args
    loader:Loader = frame.loader
    defined_symbol = data.in_data.defined_symbol
    state_analysis = data.in_data.state_analysis
    if state_analysis.analysis_phase_id != ANALYSIS_PHASE_ID.GLOBAL_SEMANTICS:
        return er.config_event_unprocessed()
    if len(positional_args) == 0:
        return er.config_event_unprocessed()
    arg0 = list(positional_args[0])
    # arg1 = list(positional_arg[1])
    arg0_state = space[arg0[0].index_in_space]
    arg0_access_path = access_path_formatter(arg0_state.access_path)
    class_members = loader.convert_class_id_to_members(1000086)
    app_return = er.config_event_unprocessed()
    # arg_index_set = set()
    # for arg in positional_args[1]:
    #     arg_index_set.add(arg.index_in_space)
    print(data.in_data.stmt_id)
    for state_index in name_states:
        state = space[state_index]
        access_path = access_path_formatter(state.access_path)
        # TODO: NO hard code
        if data.in_data.stmt_id == 1937:
            print(access_path)
        if access_path == "os.AppStorage.setOrCreate":
            class_members[arg0_access_path] = positional_args[1]
            loader.save_class_id_to_members(1000086, class_members)
            app_return = er.config_block_event_requester(app_return)
            break
        elif access_path == "os.AppStorage.Get":
            read_members = loader.convert_class_id_to_members(1000086)
            if read_members and read_members != set():
                for member in read_members.values():
                    for arg in member:
                        defined_symbol.states.add(arg.index_in_space)
                app_return = er.config_block_event_requester(app_return)
            break
    return app_return


def access_path_formatter(state_access_path):
    key_list = []
    if not state_access_path:
        return ""
    for item in state_access_path:
        key = item.key
        key = key if isinstance(key, str) else str(key)
        if key != "":
            key_list.append(key)

    #  key 
    access_path = '.'.join(key_list)
    return access_path
