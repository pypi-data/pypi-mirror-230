from abstract_gui import create_window_manager,agf
from .abstract_rpcs import get_default_rpc_list,rpc_win_while,get_rpc_layout,get_rpc_js,RPCData
from .abstract_abis import ABIBridge,default_rpc
# Initialize the window manager and bridge 
# (Assuming you still want to name it "blockchain_gui_consol")
new_window_mgr, new_bridge, new_script_name = create_window_manager(script_name="blockchain_gui_consol", global_var=globals())
new_bridge_global = new_bridge.return_global_variables(new_script_name)
def get_type(input_type,value):
    if "uint" in input_type:
        return int(value)
    return str(value)
def contract_win_while(event: str):
    values = new_window_mgr.get_values()
    if "-CALL-" in event:
        function_name = event.split("-")[2]
        # Extracting inputs and outputs associated with the function
        inputs = {}
        output_key = None
        for key, value in values.items():
            if f"-INPUT_{function_name}_" in key:
                input_name = f"{key.split('_')[-2]}"
                input_type = f"{key.split('_')[-1][:-1]}"# Assuming the name of the input is second to the last in the split result
                inputs[input_name] = get_type(input_type,value)
            elif f"-OUTPUT_{function_name}_" in key:
                output_key = key
        try:
            # If there's only one input and it's of type address
            if len(list(inputs.keys())) == 1:
                result = new_bridge_global["abi_manager"].call_function(function_name, inputs[list(inputs.keys())[0]])
            # For multiple inputs, unpack them as positional arguments
            elif inputs:
                args = tuple(inputs.values())  # Convert the dictionary values to a tuple
                result = new_bridge_global["abi_manager"].call_function(function_name, *args)
            else:
                result = new_bridge_global["abi_manager"].call_function(function_name=function_name)
            if output_key:
                new_window_mgr.update_values(key=output_key, args={"value": result})
        except Exception as e:
            print(f"Error calling function: {e}")
            print(inputs)
def win_while(event: str):
    rpc_win_while(event)
    values = new_window_mgr.get_values()
    rpc_manager = get_rpc()
    if event == "-OK_RPC-":
        rpc_manager.rpc_js
    if event == "-GET_ABI-":
        contract_address = values["-CONTRACT_ADDRESS-"]
        new_bridge_global["abi_manager"] = ABIBridge(contract_address=contract_address, rpc=rpc_manager.rpc_js)
        function_js = {}
        for each in new_bridge_global["abi_manager"].abi:
            if each["type"] == "function":
                if each["stateMutability"] not in function_js:
                    function_js[each["stateMutability"]] = []
                inputs = _parse_io(each.get("inputs", []),function_name=each["name"])
                outputs = _parse_io(each.get("outputs", []), is_output=True,function_name=each["name"])
                layout = inputs + outputs  # Combine inputs and outputs
                button = [agf("Button", args={"button_text": f"Call {each['name']}", "key": f"-CALL-{each['name']}-"})]
                layout.append(button)
                function_js[each["stateMutability"]].append(
                    agf("Frame", args={"title": each["name"], "layout": layout})
                )
        # Organizing framed groups with 4 columns per row
        all_layouts = []
        for state, funcs in function_js.items():
            rows = [funcs[i:i+7] for i in range(0, len(funcs), 7)]
            state_layout = []
            for row in rows:
                state_layout.append(row)
            all_layouts.append([agf("Frame", args={"title": state, "layout": state_layout})])
        new_window = new_window_mgr.get_new_window(title="functions", layout=all_layouts, event_function="contract_win_while")
        new_window_mgr.while_basic(window=new_window)
        
def _parse_io(io_data,function_name:str, is_output=False):
    layout = []
    for i, io_type in enumerate(io_data):
        text = f"{io_type['name']}({io_type['type']}): "
        key_suffix = "OUTPUT" if is_output else "INPUT"
        key = f"-{key_suffix}_{function_name}{'_{i}' if key_suffix is 'INPUT' else ''}_{io_type['name']}_{io_type['type']}-"
        if is_output:
            layout.append([agf("Text", args={"text": text}),get_push(), agf("Input", args={"size": (20, 1), "key": key, "disabled": True})])
        else:
            layout.append([agf("Text", args={"text": text}),get_push(),  agf("Input", args={"size": (20, 1), "key": key})])
    return layout

# If you need the ABI helper function in the new script, define it here 
def get_abi():
    frame_layout = [agf("Input",args={"key":"-CONTRACT_ADDRESS-"}),
                    agf("Button", args={"button_text":"GET ABI","enable_events":True,"key":"-GET_ABI-"})]
    return agf("Frame", "ABI", frame_layout)
def get_rpc():
    rpc={}
    rpc_js = get_rpc_js()
    for rpc_key,window_key in rpc_js.items():
        rpc[rpc_key] = new_window_mgr.get_values()[window_key]
    return RPCData(rpc)
def abstract_contract_consil_main():
    # Get the rpc_layout and other associated values
    rpc_list = get_default_rpc_list()
    rpc_layout= [[agf("Frame", "RPC_LAY",args={"layout":get_rpc_layout(RPC_list=rpc_list,window_mgr=new_window_mgr)})]]

    # Construct the final layout
    new_layout = [get_abi(),rpc_layout]

    # Create and run the window
    new_window = new_window_mgr.get_new_window(title="New Blockchain Console", layout=[new_layout], event_function="win_while")
    new_window_mgr.while_basic(window=new_window)
