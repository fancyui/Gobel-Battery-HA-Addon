<?php

function views($bms_type) {
    $output = "views:\n";
    if ($bms_type == 'jkbms') {
        $output .= "  - title: Gobel Battery JK\n";
    } else {
        $output .= "  - title: Gobel Battery\n";
    }
    $output .= "    type: sidebar\n";
    $output .= "    cards:\n";
    $output .= "      - show_name: true\n";
    $output .= "        show_icon: true\n";
    $output .= "        show_state: true\n";
    return $output;
}

function glance($device_name, $bms_type) {
  $output = "        type: glance\n";
  $output .= "        entities:\n";
  $output .= "          - entity: sensor.".$device_name."_total_soc\n";
  $output .= "            name: SOC\n";
  $output .= "          - entity: sensor.".$device_name."_total_voltage\n";
  $output .= "            name: Voltage\n";
  $output .= "          - entity: sensor.".$device_name."_total_current\n";
  $output .= "            name: Current\n";
  $output .= "          - entity: sensor.".$device_name."_total_power\n";
  $output .= "            name: Power\n";
  $output .= "        columns: 4\n";
  return $output;
}

function pack_warn_entity_filter($device_name, $total_packs_num, $bms_type) {
  $output = "";
  for ($i = 0; $i < $total_packs_num; $i++) {
    $pack_str = "pack_" . sprintf("%02d", $i+1);
    $output .= "      - type: entity-filter\n";
    $output .= "        card:\n";
    $output .= "          type: entities\n";
    $output .= "          title: Pack " . sprintf("%02d", $i+1) . " Warning\n";
    $output .= "        conditions:\n";
    $output .= "          - condition: state\n";
    $output .= "            state: 'on'\n";
    $output .= "        show_empty: false\n";
    $output .= "        view_layout:\n";
    $output .= "          position: sidebar\n";
    $output .= "        entities:\n";
    
    if ($bms_type == 'jkbms') {
      $entity_prefix = "binary_sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_protect_";
      $output .= "          - entity: " . $entity_prefix . "protect_short_circuit\n";
      $output .= "            name: Protect Short Circuit\n";
      $output .= "          - entity: " . $entity_prefix . "protect_high_discharge_current\n";
      $output .= "            name: Protect High Discharge Current\n";
      $output .= "          - entity: " . $entity_prefix . "protect_high_charge_current\n";
      $output .= "            name: Protect High Charge Current\n";
      $output .= "          - entity: " . $entity_prefix . "protect_low_total_voltage\n";
      $output .= "            name: Protect Low Total Voltage\n";
      $output .= "          - entity: " . $entity_prefix . "protect_high_total_voltage\n";
      $output .= "            name: Protect High Total Voltage\n";
      $output .= "          - entity: " . $entity_prefix . "protect_low_cell_voltage\n";
      $output .= "            name: Protect Low Cell Voltage\n";
      $output .= "          - entity: " . $entity_prefix . "protect_high_cell_voltage\n";
      $output .= "            name: Protect High Cell Voltage\n";
      $output .= "          - entity: " . $entity_prefix . "protect_low_charge_temp\n";
      $output .= "            name: Protect Low Charge Temp\n";
      $output .= "          - entity: " . $entity_prefix . "protect_high_charge_temp\n";
      $output .= "            name: Protect High Charge Temp\n";
      $output .= "          - entity: " . $entity_prefix . "protect_high_mos_temp\n";
      $output .= "            name: Protect High MOS Temp\n";
      $output .= "          - entity: " . $entity_prefix . "protect_high_discharge_temp\n";
      $output .= "            name: Protect High Discharge Temp\n";
      $output .= "          - entity: " . $entity_prefix . "fault_cell\n";
      $output .= "            name: Fault Cell Qty Mismatch\n";
      $output .= "          - entity: " . $entity_prefix . "fault_ntc\n";
      $output .= "            name: Fault Temperature Sensor\n";
    } else {
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_fault_cell\n";
      $output .= "            name: Fault Cell\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_fault_charge_mos\n";
      $output .= "            name: Fault Charge MOS\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_fault_discharge_mos\n";
      $output .= "            name: Fault Charge MOS\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_fault_ntc\n";
      $output .= "            name: Fault NTC\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_fault_sampling\n";
      $output .= "            name: Fault Sampling\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_high_charge_current\n";
      $output .= "            name: Protect High Charge Current\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_high_charge_temp\n";
      $output .= "            name: Protect High Charge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_high_discharge_current\n";
      $output .= "            name: Protect High Discharge Current\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_high_discharge_temp\n";
      $output .= "            name: Protect High Discharge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_high_env_temp\n";
      $output .= "            name: Protect High ENV Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_high_mos_temp\n";
      $output .= "            name: Protect High MOS Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_high_total_voltage\n";
      $output .= "            name: Protect High Total Voltage\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_low_cell_voltage\n";
      $output .= "            name: Protect Low Cell Voltage\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_low_charge_temp\n";
      $output .= "            name: Protect Low Charge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_low_discharge_temp\n";
      $output .= "            name: Protect Low Discharge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_low_env_temp\n";
      $output .= "            name: Protect Low ENV Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_low_total_voltage\n";
      $output .= "            name: Protect Low Total Voltage\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_protect_short_circuit\n";
      $output .= "            name: Protect Short Circuit\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_cell_voltage\n";
      $output .= "            name: Warn High Cell Voltage\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_charge_current\n";
      $output .= "            name: Warn High Charge Current\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_charge_temp\n";
      $output .= "            name: Warn High Charge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_discharge_current\n";
      $output .= "            name: Warn High Discharge Current\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_discharge_temp\n";
      $output .= "            name: Warn High Discharge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_env_temp\n";
      $output .= "            name: Warn High ENV Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_mos_temp\n";
      $output .= "            name: Warn High MOS Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_high_total_voltage\n";
      $output .= "            name: Warn High Total Voltage\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_low_cell_voltage\n";
      $output .= "            name: Warn Low Cell Voltage\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_low_charge_temp\n";
      $output .= "            name: Warn Low Charge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_low_discharge_temp\n";
      $output .= "            name: Warn Low Discharge Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_low_env_temp\n";
      $output .= "            name: Warn Low ENV Temperature\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_low_soc\n";
      $output .= "            name: Warn Low SOC\n";
      $output .= "          - entity: binary_sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_warn_low_total_voltage\n";
      $output .= "            name: Warn Low Total Voltage\n";
    }
  }
  return $output;
}

function cell_warn_entity_filter($device_name, $total_packs_num, $num_cells, $bms_type) {
  $output = "";
  for ($i = 0; $i < $total_packs_num; $i++) {
    $pack_str = "pack_" . sprintf("%02d", $i+1);
    $output .= "      - type: entity-filter\n";
    $output .= "        card:\n";
    $output .= "          type: entities\n";
    $output .= "          title: Pack " . sprintf("%02d", $i+1) . " Cell Warning\n";
    $output .= "        conditions:\n";
    $output .= "          - condition: state\n";
    $output .= "            state_not: normal\n";
    $output .= "        show_empty: false\n";
    $output .= "        view_layout:\n";
    $output .= "          position: sidebar\n";
    $output .= "        entities:\n";
    for ($j = 1; $j <= $num_cells; $j++) {
      if ($bms_type == 'jkbms') {
        $output .= "          - entity: sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_protect_cell_voltage_warning_" . sprintf("%02d", $j) . "\n";
      } else {
        $output .= "          - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_cell_voltage_warning_" . sprintf("%02d", $j) . "\n";
      }
      $output .= "            name: Warn Cell" . sprintf("%02d", $j) . " Voltage\n";
    }
  }
  return $output;
}

function total_entities($device_name, $bms_type) {
  $output = "";
  $output .= "      - type: entities\n";
  $output .= "        state_color: true\n";
  $output .= "        view_layout:\n";
  $output .= "          position: sidebar\n";
  $output .= "        title: System Overview\n";
  $output .= "        entities:\n";
  $output .= "          - entity: sensor." . $device_name . "_total_current\n";
  $output .= "            name: Total Current\n";
  $output .= "          - entity: sensor." . $device_name . "_total_power\n";
  $output .= "            name: Total Power\n";
  $output .= "          - entity: sensor." . $device_name . "_total_voltage\n";
  $output .= "            name: Total Voltage\n";
  $output .= "          - entity: sensor." . $device_name . "_total_soc\n";
  $output .= "            name: Total SOC\n";
  $output .= "          - entity: sensor." . $device_name . "_total_soh\n";
  $output .= "            name: Total SOH\n";
  $output .= "          - entity: sensor." . $device_name . "_total_remain_capacity\n";
  $output .= "            name: Total Remain Capacity\n";
  $output .= "          - entity: sensor." . $device_name . "_total_full_capacity\n";
  $output .= "            name: Total Full Capacity\n";
  $output .= "          - entity: sensor." . $device_name . "_total_cell_voltage_max\n";
  $output .= "            name: Total Cell Voltage Max\n";
  $output .= "          - entity: sensor." . $device_name . "_total_cell_voltage_min\n";
  $output .= "            name: Total Cell Voltage Min\n";
  $output .= "          - entity: sensor." . $device_name . "_total_cell_voltage_diff\n";
  $output .= "            name: Total Cell Voltage Diff\n";
  if ($bms_type == 'jkbms') {
    $output .= "          - entity: sensor." . $device_name . "_total_energy_charged\n";
    $output .= "            name: Total Energy Charged\n";
    $output .= "          - entity: sensor." . $device_name . "_total_energy_discharged\n";
    $output .= "            name: Total Energy Discharged\n";
  }
  $output .= "          - entity: sensor." . $device_name . "_total_packs_num\n";
  $output .= "            name: Total Packs Number\n";
  return $output;
}

function pack_settings_entities($device_name, $total_packs_num, $bms_type) {
  $output = "";
  if ($bms_type != 'jkbms') {
    return $output;
  }
  for ($i = 0; $i < $total_packs_num; $i++) {
    $pack_str = "pack_" . sprintf("%02d", $i+1);
    $sensor_prefix = "sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_setting_";
    $binary_prefix = "binary_sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_setting_";
    
    $output .= "      - type: entities\n";
    $output .= "        title: Pack " . sprintf("%02d", $i+1) . " Settings\n";
    $output .= "        state_color: true\n";
    $output .= "        view_layout:\n";
    $output .= "          position: sidebar\n";
    $output .= "        entities:\n";
    
    // Group 1: Switch Settings
    $output .= "          - type: section\n";
    $output .= "            label: Function Switches\n";
    $output .= "          - entity: " . $binary_prefix . "charge_switch_enabled\n";
    $output .= "            name: Charge Switch\n";
    $output .= "          - entity: " . $binary_prefix . "discharge_switch_enabled\n";
    $output .= "            name: Discharge Switch\n";
    $output .= "          - entity: " . $binary_prefix . "balance_switch_enabled\n";
    $output .= "            name: Balance Switch\n";
    $output .= "          - entity: " . $binary_prefix . "function_heating_enabled\n";
    $output .= "            name: Heating Function\n";
    $output .= "          - entity: " . $binary_prefix . "function_smart_sleep_enabled\n";
    $output .= "            name: Smart Sleep Function\n";
    
    // Group 2: Voltages Settings
    $output .= "          - type: section\n";
    $output .= "            label: Voltage Parameters\n";
    $output .= "          - entity: " . $sensor_prefix . "cell_overvoltage_protection\n";
    $output .= "            name: Cell Overvoltage Protection\n";
    $output .= "          - entity: " . $sensor_prefix . "cell_overvoltage_recovery\n";
    $output .= "            name: Cell Overvoltage Recovery\n";
    $output .= "          - entity: " . $sensor_prefix . "cell_undervoltage_protection\n";
    $output .= "            name: Cell Undervoltage Protection\n";
    $output .= "          - entity: " . $sensor_prefix . "cell_undervoltage_recovery\n";
    $output .= "            name: Cell Undervoltage Recovery\n";
    $output .= "          - entity: " . $sensor_prefix . "balance_start_voltage\n";
    $output .= "            name: Balance Start Voltage\n";
    $output .= "          - entity: " . $sensor_prefix . "balance_trigger_voltage\n";
    $output .= "            name: Balance Trigger Voltage\n";
    
    // Group 3: Current Settings
    $output .= "          - type: section\n";
    $output .= "            label: Current & Delay Parameters\n";
    $output .= "          - entity: " . $sensor_prefix . "charge_overcurrent_protection\n";
    $output .= "            name: Charge Overcurrent Protection\n";
    $output .= "          - entity: " . $sensor_prefix . "discharge_overcurrent_protection\n";
    $output .= "            name: Discharge Overcurrent Protection\n";
    $output .= "          - entity: " . $sensor_prefix . "max_balance_current\n";
    $output .= "            name: Max Balance Current\n";
    $output .= "          - entity: " . $sensor_prefix . "short_circuit_delay\n";
    $output .= "            name: Short Circuit Delay\n";
    
    // Group 4: Temperature Settings
    $output .= "          - type: section\n";
    $output .= "            label: Temperature Parameters\n";
    $output .= "          - entity: " . $sensor_prefix . "charge_over_temperature_protection\n";
    $output .= "            name: Charge Over Temp Protection\n";
    $output .= "          - entity: " . $sensor_prefix . "charge_low_temperature_protection\n";
    $output .= "            name: Charge Low Temp Protection\n";
    $output .= "          - entity: " . $sensor_prefix . "discharge_over_temperature_protection\n";
    $output .= "            name: Discharge Over Temp Protection\n";
    $output .= "          - entity: " . $sensor_prefix . "mos_over_temperature_protection\n";
    $output .= "            name: MOS Over Temp Protection\n";
    
    // Group 5: Other Settings
    $output .= "          - type: section\n";
    $output .= "            label: Hardware Settings\n";
    $output .= "          - entity: " . $sensor_prefix . "cell_count_setting\n";
    $output .= "            name: Cell Count Setting\n";
    $output .= "          - entity: " . $sensor_prefix . "cell_design_capacity\n";
    $output .= "            name: Cell Design Capacity\n";
    $output .= "          - entity: " . $sensor_prefix . "device_address\n";
    $output .= "            name: Device Address\n";
  }
  return $output;
}

function pack_entities($device_name, $total_packs_num, $bms_type) {
  $output = "";
  for ($i = 0; $i < $total_packs_num; $i++) {
    $pack_str = "pack_" . sprintf("%02d", $i+1);
    
    $output .= "      - type: vertical-stack\n";
    $output .= "        cards:\n";
    
    // 1. Glance Card for live metrics
    $output .= "          - type: glance\n";
    $output .= "            title: Pack " . sprintf("%02d", $i+1) . " Overview\n";
    $output .= "            entities:\n";
    if ($bms_type == 'jkbms') {
      $sensor_prefix = "sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_view_";
      $output .= "              - entity: " . $sensor_prefix . "soc\n";
      $output .= "                name: SOC\n";
      $output .= "              - entity: " . $sensor_prefix . "voltage\n";
      $output .= "                name: Voltage\n";
      $output .= "              - entity: " . $sensor_prefix . "current\n";
      $output .= "                name: Current\n";
      $output .= "              - entity: " . $sensor_prefix . "soh\n";
      $output .= "                name: SOH\n";
      $output .= "              - entity: " . $sensor_prefix . "cycle_count\n";
      $output .= "                name: Cycles\n";
      $output .= "              - entity: " . $sensor_prefix . "temp_mos\n";
      $output .= "                name: MOS Temp\n";
      $output .= "            columns: 6\n";
    } else {
      $output .= "              - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_SOC\n";
      $output .= "                name: SOC\n";
      $output .= "              - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_voltage\n";
      $output .= "                name: Voltage\n";
      $output .= "              - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_current\n";
      $output .= "                name: Current\n";
      $output .= "              - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_SOH\n";
      $output .= "                name: SOH\n";
      $output .= "              - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_cycle_number\n";
      $output .= "                name: Cycles\n";
      $output .= "            columns: 5\n";
    }
    
    // 2. Grid card for details (multi-column)
    if ($bms_type == 'jkbms') {
      $sensor_prefix = "sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_view_";
      $binary_prefix = "binary_sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_view_";
      
      $output .= "          - type: grid\n";
      $output .= "            title: Pack " . sprintf("%02d", $i+1) . " Details\n";
      $output .= "            columns: 3\n";
      $output .= "            square: false\n";
      $output .= "            cards:\n";
      
      // Column 1: Capacity & Voltages
      $output .= "              - type: entities\n";
      $output .= "                title: Capacity & Voltages\n";
      $output .= "                entities:\n";
      $output .= "                  - entity: " . $sensor_prefix . "remain_capacity\n";
      $output .= "                    name: Remain Capacity\n";
      $output .= "                  - entity: " . $sensor_prefix . "full_capacity\n";
      $output .= "                    name: Full Capacity\n";
      $output .= "                  - entity: " . $sensor_prefix . "design_capacity\n";
      $output .= "                    name: Design Capacity\n";
      $output .= "                  - entity: " . $sensor_prefix . "cell_voltage_max\n";
      $output .= "                    name: Cell Voltage Max\n";
      $output .= "                  - entity: " . $sensor_prefix . "cell_voltage_min\n";
      $output .= "                    name: Cell Voltage Min\n";
      $output .= "                  - entity: " . $sensor_prefix . "cell_voltage_diff\n";
      $output .= "                    name: Cell Voltage Diff\n";
      
      // Column 2: Specs & Stats
      $output .= "              - type: entities\n";
      $output .= "                title: Specs & Stats\n";
      $output .= "                entities:\n";
      $output .= "                  - entity: " . $sensor_prefix . "num_cells\n";
      $output .= "                    name: Cells Number\n";
      $output .= "                  - entity: " . $sensor_prefix . "num_temps\n";
      $output .= "                    name: NTC Number\n";
      $output .= "                  - entity: " . $sensor_prefix . "balance_current\n";
      $output .= "                    name: Balance Current\n";
      $output .= "                  - entity: " . $sensor_prefix . "energy_charged\n";
      $output .= "                    name: Energy Charged\n";
      $output .= "                  - entity: " . $sensor_prefix . "energy_discharged\n";
      $output .= "                    name: Energy Discharged\n";
      $output .= "                  - entity: " . $sensor_prefix . "system_uptime\n";
      $output .= "                    name: System Uptime\n";
      $output .= "                  - entity: " . $sensor_prefix . "fault_count\n";
      $output .= "                    name: Fault Count\n";
      
      // Column 3: Switches & States
      $output .= "              - type: entities\n";
      $output .= "                title: Switches & States\n";
      $output .= "                entities:\n";
      $output .= "                  - entity: " . $binary_prefix . "charge_mos\n";
      $output .= "                    name: Charge Switch\n";
      $output .= "                  - entity: " . $binary_prefix . "discharge_mos\n";
      $output .= "                    name: Discharge Switch\n";
      $output .= "                  - entity: " . $binary_prefix . "balance_mos\n";
      $output .= "                    name: Balance Switch\n";
      $output .= "                  - entity: " . $binary_prefix . "heating_state\n";
      $output .= "                    name: Heating State\n";
      $output .= "                  - entity: " . $binary_prefix . "charger_plugged\n";
      $output .= "                    name: Charger Plugged\n";
      
    } else {
      $output .= "          - type: grid\n";
      $output .= "            title: Pack " . sprintf("%02d", $i+1) . " Details\n";
      $output .= "            columns: 2\n";
      $output .= "            square: false\n";
      $output .= "            cards:\n";
      
      // Column 1: Capacity
      $output .= "              - type: entities\n";
      $output .= "                title: Capacity\n";
      $output .= "                entities:\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_remain_capacity\n";
      $output .= "                    name: Remain Capacity\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_full_capacity\n";
      $output .= "                    name: Full Capacity\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_design_capacity\n";
      $output .= "                    name: Design Capacity\n";
      
      // Column 2: Voltages & Specs
      $output .= "              - type: entities\n";
      $output .= "                title: Voltages & Specs\n";
      $output .= "                entities:\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_cell_voltage_max\n";
      $output .= "                    name: Cell Voltage Max\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_cell_voltage_min\n";
      $output .= "                    name: Cell Voltage Min\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_cell_voltage_diff\n";
      $output .= "                    name: Cell Voltage Diff\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_num_cells\n";
      $output .= "                    name: Cells Number\n";
      $output .= "                  - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_view_num_temps\n";
      $output .= "                    name: NTC Number\n";
    }
  }
  return $output;
}

function pack_cell_history($device_name, $total_packs_num, $num_cells, $bms_type) {
  $output = "";
  for ($i = 0; $i < $total_packs_num; $i++) {
    $pack_str = "pack_" . sprintf("%02d", $i+1);
    $output .= "      - title: Pack " . sprintf("%02d", $i+1) . " Cell Voltages\n";
    $output .= "        type: history-graph\n";
    $output .= "        hours_to_show: 48\n";
    $output .= "        min_y_axis: 2000\n";
    $output .= "        max_y_axis: 4000\n";
    $output .= "        fit_y_data: false\n";
    $output .= "        entities:\n";
    for ($j = 1; $j <= $num_cells; $j++) {
      if ($bms_type == 'jkbms') {
        $output .= "          - entity: sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_view_cell_voltage_" . sprintf("%02d", $j) . "\n";
      } else {
        $output .= "          - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_cell_voltage_" . sprintf("%02d", $j) . "\n";
      }
      $output .= "            name: Cell" . sprintf("%02d", $j) . "\n";
    }
  }
  return $output;
}

function pack_temp_history($device_name, $total_packs_num, $num_temps, $bms_type) {
  $output = "";
  for ($i = 0; $i < $total_packs_num; $i++) {
    $pack_str = "pack_" . sprintf("%02d", $i+1);
    $output .= "      - title: Pack " . sprintf("%02d", $i+1) . " Temperatures\n";
    $output .= "        type: history-graph\n";
    $output .= "        hours_to_show: 48\n";
    $output .= "        entities:\n";
    
    if ($bms_type == 'jkbms') {
      for ($j = 1; $j <= $num_temps; $j++) {
        $output .= "          - entity: sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_view_temperature_" . sprintf("%02d", $j) . "\n";
        $output .= "            name: Temp " . sprintf("%02d", $j) . "\n";
      }
      $output .= "          - entity: sensor." . $device_name . "_" . $pack_str . "_" . $pack_str . "_view_temp_mos\n";
      $output .= "            name: MOS\n";
    } else {
      for ($j = 1; $j <= $num_temps; $j++) {
        if ($j < 5) {
          $output .= "          - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_temperature_" . sprintf("%02d", $j) . "\n";
          $output .= "            name: Cell" . sprintf("%02d", $j) . "\n";
        } elseif ($j == 5) {
          $output .= "          - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_temperature_" . sprintf("%02d", $j) . "\n";
          $output .= "            name: MOS\n";
        } elseif ($j == 6) {
          $output .= "          - entity: sensor." . $device_name . "_pack_" . sprintf("%02d", $i+1) . "_temperature_" . sprintf("%02d", $j) . "\n";
          $output .= "            name: Environment\n";
        }
      }
    }
  }
  return $output;
}

function generate_dashboard_template($device_name, $total_packs_num, $num_cells, $num_temps, $bms_type) {
    $output = views($bms_type);
    $output .= glance($device_name, $bms_type);
    $output .= pack_warn_entity_filter($device_name, $total_packs_num, $bms_type);
    $output .= cell_warn_entity_filter($device_name, $total_packs_num, $num_cells, $bms_type);
    $output .= total_entities($device_name, $bms_type);
    $output .= pack_settings_entities($device_name, $total_packs_num, $bms_type);
    $output .= pack_entities($device_name, $total_packs_num, $bms_type);
    $output .= pack_cell_history($device_name, $total_packs_num, $num_cells, $bms_type);
    $output .= pack_temp_history($device_name, $total_packs_num, $num_temps, $bms_type);

    $output = str_replace(" ", "&nbsp;", $output);

    return $output;
}

if (isset($_GET['device_name'])) {

  $device_name = $_GET['device_name'];
  $total_packs_num = $_GET['total_packs_num'];
  $num_cells = $_GET['num_cells'];
  $num_temps = $_GET['num_temps'];
  $bms_type = isset($_GET['bms_type']) ? $_GET['bms_type'] : 'pacebms';

  $device_name = strtolower(str_replace(" ", "_", $device_name));
}

?>

<style>
  #yaml_codes {
    white-space: pre-wrap;
    background-color: #111;
    color: #fff;
    font-family: monospace;
    padding: 10px;
    position: relative;
  }
  #copy_button {
    padding: 10px;
    cursor: pointer;
    float: text;
    background: #ddd;
    margin-right: 10px;
  }

  .yaml_title{
    background-color: #555;
    text-align: right;
    line-height: 50px;
    height: 50px;
    margin-top: 30px;
  }

  .form_ctn {
    padding: 10px 10px 50px 10px;
    max-width: 300px;
    margin: auto;
  }

  .form_ctn input, .form_ctn select {
    display: block;
    margin-top: 10px;
    width: 100%;
    box-sizing: border-box;
  }
  .cssButton {
    margin-top: 20px!important;
  }
</style>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/styles/default.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.5.1/highlight.min.js"></script>

<div class="form_ctn">
  <form action="/ha_dashboard_ap46.html">
    <input type="text" name="device_name" placeholder="Device Name" class="input_box" value="<?php echo isset($_GET['device_name']) ? htmlspecialchars($_GET['device_name']) : ''; ?>">
    <input type="number" name="total_packs_num" placeholder="Total Packs Num" class="input_box" value="<?php echo isset($_GET['total_packs_num']) ? htmlspecialchars($_GET['total_packs_num']) : ''; ?>">
    <input type="number" name="num_cells" placeholder="View Num Cells" class="input_box" value="<?php echo isset($_GET['num_cells']) ? htmlspecialchars($_GET['num_cells']) : ''; ?>">
    <input type="number" name="num_temps" placeholder="View Num Temps" class="input_box" value="<?php echo isset($_GET['num_temps']) ? htmlspecialchars($_GET['num_temps']) : ''; ?>">
    <select name="bms_type" class="input_box" style="margin-top: 10px; height: 35px; background: #fff; border: 1px solid #ccc; padding: 5px;">
      <option value="pacebms" <?php if (isset($_GET['bms_type']) && $_GET['bms_type'] == 'pacebms') echo 'selected'; ?>>PACE BMS</option>
      <option value="jkbms" <?php if (isset($_GET['bms_type']) && $_GET['bms_type'] == 'jkbms') echo 'selected'; ?>>JK BMS</option>
    </select>
    <input type="submit" name="Generate" class="cssButton button_send">
  </form>
</div>

<?php if (isset($_GET['device_name'])) { ?>

<div class="yaml_title">
  <button id="copy_button">
    Copy Code
  </button>
</div>

<div id="yaml_codes" style="white-space: pre-wrap; background-color: #222; color: #fff; font-family: monospace; padding: 10px;">
  <?php echo generate_dashboard_template($device_name, $total_packs_num, $num_cells, $num_temps, $bms_type); ?>
</div>

<script>
  // Initialize syntax highlighting
  hljs.highlightElement(document.getElementById('yaml_codes'));

  // Function to handle copy action
  document.getElementById('copy_button').addEventListener('click', function() {
    // Create a temporary textarea to hold the code for copying
    const tempTextArea = document.createElement('textarea');
    
    // Get the text content from the div and replace non-breaking spaces with regular spaces
    const codeText = document.getElementById('yaml_codes').innerText.replace(/\u00A0/g, ' ');
    tempTextArea.value = codeText;
    
    document.body.appendChild(tempTextArea);

    // Select and copy the code
    tempTextArea.select();
    tempTextArea.setSelectionRange(0, 99999); // For mobile devices

    // Execute the copy command
    document.execCommand('copy');

    // Remove the temporary textarea
    document.body.removeChild(tempTextArea);

    // Change button text to "Copied!" to give feedback to the user
    const copyButton = document.getElementById('copy_button');
    copyButton.innerText = 'Copied!';
    
    // Optional: Revert the button text back to "Copy Code" after a few seconds
    setTimeout(function() {
      copyButton.innerText = 'Copy Code';
    }, 2000); // Change text back after 2 seconds
  });
</script>

<?php } ?>