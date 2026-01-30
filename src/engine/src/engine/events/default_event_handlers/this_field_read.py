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
    ACCESS_POINT_KIND
)
import engine.events.event_return as er
from engine.util import util
from engine.util.loader import Loader
from engine.config.constants import ENGINE_INTERNAL

def check_this_read(receiver_symbol, receiver_states, frame):
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

def resolve_this_field_method(data: EventData):
    in_data = data.in_data
    frame: ComputeFrame = in_data.frame
    status = in_data.status
    receiver_states = in_data.receiver_states
    receiver_symbol: Symbol = in_data.receiver_symbol
    field_states = in_data.field_states
    defined_symbol = in_data.defined_symbol
    stmt_id = in_data.stmt_id
    state_analysis:StmtStates = in_data.state_analysis
    loader:Loader = frame.loader
    defined_states = in_data.defined_states
    app_return = er.config_event_unprocessed()

    # selffield_read
    if not check_this_read(receiver_symbol,receiver_states,frame):
        data.out_data.receiver_states = receiver_states
        app_return = er.config_continue_event_processing(app_return)
        return app_return
    # methods_in_class
    current_method_id = frame.method_id
    current_class_id = loader.convert_method_id_to_class_id(current_method_id)
    methods_in_class = copy.deepcopy(loader.get_methods_in_class(current_class_id))
    # print(methods_in_class)
    # print(f": {asizeof.asizeof(methods_in_class)} ")
    for each_class in frame.classes_of_method:
        if each_class != current_class_id:
            method_in_current_class = loader.get_methods_in_class(each_class)
            methods_in_class.extend(method_in_current_class)
    method_name = loader.convert_method_id_to_method_name(current_method_id)
    class_name = loader.convert_class_id_to_class_name(current_class_id)
    # print("methods_in_class: \n",methods_in_class)
    # print("receiver_states:",receiver_states,\
    #       "\n",class_name,"",method_name)
    # print([frame.symbol_state_space[i].data_type for i in receiver_states])
    for each_receiver_state_index in receiver_states:
        each_receiver_state : State = frame.symbol_state_space[each_receiver_state_index]
        if not isinstance(each_receiver_state, State):
            continue

        for each_field_state_index in field_states:
            each_field_state = frame.symbol_state_space[each_field_state_index]
            if not isinstance(each_field_state, State):
                continue
            field_name = str(each_field_state.value)
            # print("resolve_this_field_method@ field_name",field_name)
            if len(field_name) == 0:
                continue

            # receiver_this_statefieldpass
            if field_name in each_receiver_state.fields and len(each_receiver_state.fields[field_name]) > 0:
                continue

            # methods_in_classfield_name
            found_method_ids = [method.stmt_id for method in methods_in_class if method.name == field_name]
            if util.is_empty(found_method_ids):
                continue

            # copy_on_change receiver_state
            new_receiver_state_index = state_analysis.create_copy_of_state_and_add_space(status, stmt_id, each_receiver_state_index)
            new_receiver_state = frame.symbol_state_space[new_receiver_state_index]
            for each_method_id in found_method_ids:
                field_method_state_index = state_analysis.create_state_and_add_space(
                    stmt_id = stmt_id,
                    status = status,
                    source_symbol_id = each_method_id,
                    source_state_id = each_receiver_state.source_state_id,
                    data_type = ENGINE_INTERNAL.METHOD_DECL,
                    value = each_method_id,
                    access_path = state_analysis.copy_and_extend_access_path(
                        each_receiver_state.access_path,
                        AccessPoint(
                            kind = ACCESS_POINT_KIND.FIELD_NAME,
                            key = field_name
                        )
                    )
                )
                state_analysis.update_access_path_state_id(field_method_state_index)
                util.add_to_dict_with_default_set(new_receiver_state.fields, field_name, field_method_state_index)
            receiver_states.discard(each_receiver_state_index)
            receiver_states.add(new_receiver_state_index)
            # this_statesummarykey_dynamic_contentthis_statethis_state
            state_analysis.unset_key_state_flag(receiver_symbol.symbol_id, each_receiver_state_index)
            # print("copy_on_change state",new_receiver_state_index,"",each_receiver_state_index)
            # pprint.pprint(new_receiver_state)

    data.out_data.receiver_states = receiver_states
    app_return = er.config_continue_event_processing(app_return)
    return app_return


def read_from_this_class(data: EventData):
    in_data = data.in_data
    frame: ComputeFrame = in_data.frame
    status = in_data.status
    receiver_states = in_data.receiver_states
    receiver_symbol: Symbol = in_data.receiver_symbol
    field_states = in_data.field_states
    defined_symbol = in_data.defined_symbol
    stmt_id = in_data.stmt_id
    state_analysis:StmtStates = in_data.state_analysis
    loader:Loader = frame.loader
    defined_states = in_data.defined_states
    app_return = er.config_event_unprocessed()
    resolver = state_analysis.resolver

    # global_analysisthis_field_read
    if not check_this_read(receiver_symbol,receiver_states,frame) or state_analysis.analysis_phase_id != 3:
        data.out_data.receiver_states = receiver_states
        app_return = er.config_continue_event_processing(app_return)
        return app_return

    result = set()
    class_id = loader.convert_method_id_to_class_id(frame.method_id)
    class_members = loader.convert_class_id_to_members(class_id)
    for each_field_state_index in field_states:
        each_field_state = frame.symbol_state_space[each_field_state_index]
        if not isinstance(each_field_state, State):
            continue
        field_name = str(each_field_state.value)
        if len(field_name) == 0 or each_field_state.state_type == STATE_TYPE_KIND.ANYTHING:
            continue
        if field_name in class_members:
            index_set = class_members.get(field_name, set())
            result.update(index_set)

    if not util.is_empty(result):
        defined_symbol.states.update(result)
        data.out_data.defined_states = result
        app_return = er.config_block_event_requester(app_return)
        return app_return

    data.out_data.receiver_states = receiver_states
    app_return = er.config_continue_event_processing(app_return)
    return app_return
