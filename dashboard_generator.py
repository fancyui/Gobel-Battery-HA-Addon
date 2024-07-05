
def views():
    print("views:")
    print("  - title: Gobel Battery")
    print("    type: sidebar")
    print("    cards:")
    print("      - show_name: true")
    print("        show_icon: true")
    print("        show_state: true")

def glance(device_name):
    print("        type: glance")
    print("        entities:")
    print(f"          - entity: sensor.{device_name}_monitor_total_soc")
    print("            name: SOC")
    print(f"          - entity: sensor.{device_name}_monitor_total_voltage")
    print("            name: Voltage")
    print(f"          - entity: sensor.{device_name}_monitor_total_current")
    print("            name: Current")
    print(f"          - entity: sensor.{device_name}_monitor_total_power")
    print("            name: Power")
    print("        columns: 4")


def pack_warn_entity_filter(device_name, total_packs_num):

    for i in range(total_packs_num):
        print("      - type: entity-filter")
        print("        card:")
        print("          type: entities")
        print(f"          title: Pack {i+1:02} Warning")
        print("        conditions:")
        print("          - condition: state")
        print("            state: 'on'")
        print("        show_empty: false")
        print("        view_layout:")
        print("          position: sidebar")
        print("        entities:")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_fault_cell")
        print(f"            name: Fault Cell")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_fault_charge_mos")
        print(f"            name: Fault Charge MOS")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_fault_discharge_mos")
        print(f"            name: Fault Charge MOS")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_fault_ntc")
        print(f"            name: Fault NTC")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_fault_sampling")
        print(f"            name: Fault Sampling")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_high_charge_current")
        print(f"            name: Protect High Charge Current")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_high_charge_temp")
        print(f"            name: Protect High Charge Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_high_discharge_current")
        print(f"            name: Protect High Discharge Current")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_high_discharge_temp")
        print(f"            name: Protect High Discharge Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_high_env_temp")
        print(f"            name: Protect High ENV Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_high_mos_temp")
        print(f"            name: Protect High MOS Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_high_total_voltage")
        print(f"            name: Protect High Total Voltage")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_low_cell_voltage")
        print(f"            name: Protect Low Cell Voltage")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_low_charge_temp")
        print(f"            name: Protect Low Charge Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_low_discharge_temp")
        print(f"            name: Protect Low Discharge Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_low_env_temp")
        print(f"            name: Protect Low ENV Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_low_total_voltage")
        print(f"            name: Protect Low Total Voltage")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_protect_short_circuit")
        print(f"            name: Protect Short Circuit")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_high_cell_voltage")
        print(f"            name: Warn High Cell Voltage")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_high_charge_current")
        print(f"            name: Warn High Charge Current")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_high_discharge_current")
        print(f"            name: Warn High Discharge Current")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_high_discharge_temp")
        print(f"            name: Warn High Discharge Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_high_env_temp")
        print(f"            name: Warn High ENV Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_high_mos_temp")
        print(f"            name: Warn High MOS Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_high_total_voltage")
        print(f"            name: Warn High Total Voltage")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_low_cell_voltage")
        print(f"            name: Warn Low Cell Voltage")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_low_charge_temp")
        print(f"            name: Warn Low Charge Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_low_discharge_temp")
        print(f"            name: Warn Low Discharge Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_low_env_temp")
        print(f"            name: Warn Low ENV Temperature")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_low_soc")
        print(f"            name: Warn Low SOC")
        print(f"          - entity: binary_sensor.{device_name}_monitor_pack_{i+1:02}_warn_low_total_voltage")
        print(f"            name: Warn Low Total Voltage")



def cell_warn_entity_filter(device_name, total_packs_num, num_cells):

    for i in range(total_packs_num):
        print("      - type: entity-filter")
        print("        card:")
        print("          type: entities")
        print(f"          title: Pack {i+1:02} Cell Warning")
        print("        conditions:")
        print("          - condition: state")
        print("            state: normal")
        print("        show_empty: false")
        print("        view_layout:")
        print("          position: sidebar")
        print("        entities:")
        for j in range(1, num_cells + 1):
            print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_cell_voltage_warning_{j:02}")
            print(f"            name: Warn Cell{j:02} Voltage")


def total_entites(device_name):
    print("      - type: entities")
    print("        state_color: true")
    print("        view_layout:")
    print("          position: sidebar")
    print("        title: System Overview")
    print("        entities:")
    print(f"          - entity: sensor.{device_name}_monitor_total_current")
    print("            name: Total Current")
    print(f"          - entity: sensor.{device_name}_monitor_total_power")
    print("            name: Total Power")
    print(f"          - entity: sensor.{device_name}_monitor_total_voltage")
    print("            name: Total Voltage")
    print(f"          - entity: sensor.{device_name}_monitor_total_soc")
    print("            name: Total SOC")
    print(f"          - entity: sensor.{device_name}_monitor_total_soh")
    print("            name: Total SOH")
    print(f"          - entity: sensor.{device_name}_monitor_total_remain_capacity")
    print("            name: Total Remain Capacity")
    print(f"          - entity: sensor.{device_name}_monitor_total_full_capacity")
    print("            name: Total Full Capacity")
    print(f"          - entity: sensor.{device_name}_monitor_total_packs_num")
    print("            name: Total Packs Number")


def pack_entites(device_name, total_packs_num):

    for i in range(total_packs_num):
        print("      - type: entities")
        print("        state_color: true")
        print("        view_layout:")
        print("          position: sidebar")
        print(f"        title: Pack {i+1:02} Overview")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_current")
        print(f"            name: Current")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_voltage")
        print(f"            name: Total Voltage")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_soc")
        print(f"            name: SOC")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_soh")
        print(f"            name: SOH")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_remain_capacity")
        print(f"            name: Remain Capacity")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_full_capacity")
        print(f"            name: Full Capacity")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_design_capacity")
        print(f"            name: Design Capacity")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_cycle_number")
        print(f"            name: Cycles")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_num_cells")
        print(f"            name: Cells Number")
        print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_view_num_temps")
        print(f"            name: NTC Number")


def pack_cell_history(device_name, total_packs_num, num_cells):

    for i in range(total_packs_num):
        print(f"      - title: Pack {i+1:02} Cell Voltages")
        print("        type: history-graph")
        print("        hours_to_show: 48")
        print("        min_y_axis: 2000")
        print("        max_y_axis: 4000")
        print("        fit_y_data: false")
        for j in range(1, num_cells + 1):
            print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_cell_voltage_{j:02}")
            print(f"            name: Cell{j:02}")


def pack_temp_history(device_name, total_packs_num, num_cells):

    for i in range(total_packs_num):
        print(f"      - title: Pack {i+1:02} Temperatures")
        print("        type: history-graph")
        print("        hours_to_show: 48")
        for j in range(1, num_cells + 1):
            if j < 5:
                print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_temperature_{j:02}")
                print(f"            name: Cell{j:02}")
            elif j == 5:
                print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_temperature_{j:02}")
                print("            name: MOS")
            elif j ==6:
                print(f"          - entity: sensor.{device_name}_monitor_pack_{i+1:02}_temperature_{j:02}")
                print("            name: Environment")


def generate_dashboard_template(device_name, total_packs_num, num_cells):

	views()
	glance(device_name)
	pack_warn_entity_filter(device_name, total_packs_num)
	cell_warn_entity_filter(device_name, total_packs_num, num_cells)
	total_entites(device_name)
	pack_entites(device_name, total_packs_num)
	pack_cell_history(device_name, total_packs_num, num_cells)
	pack_temp_history(device_name, total_packs_num, num_cells)

