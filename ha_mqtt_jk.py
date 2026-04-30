#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JK BMS-specific MQTT publisher.

Wraps a generic HA_MQTT instance (composition) to provide JK-native
entity naming and publishing orchestration. Reuses the MQTT connection
and low-level publish methods from HA_MQTT.

Entity naming convention (no 'view_' prefix):
  pack_01_current            (was: pack_01_view_current)
  pack_01_soc                (was: pack_01_view_SOC)
  pack_01_cycle_count        (was: pack_01_view_cycle_number)
  pack_01_charge_mos         (NEW: binary sensor)
  pack_01_temp_mos           (NEW: MOS temperature)
  setup_cell_ovp_mv          (NEW: from 0x161E config frame)
"""

import logging


class HA_MQTT_JK:
    """
    JK BMS-specific MQTT publisher.

    Composes an HA_MQTT instance (not inherits) to reuse its MQTT
    connection and low-level publish_sensor_discovery / publish_sensor_state
    methods, while providing JK-specific entity naming and orchestration.

    Args:
        ha_comm: An initialized HA_MQTT instance.
    """

    def __init__(self, ha_comm):
        self.mqtt = ha_comm
        self.logger = logging.getLogger(__name__)

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _pub_sensor(self, entity_id, value, unit, icon, devclass, stateclass):
        """Publish discovery + state for a single sensor entity."""
        self.mqtt.publish_sensor_discovery(entity_id, unit, icon, devclass, stateclass)
        self.mqtt.publish_sensor_state(value, unit, entity_id)

    def _pub_binary(self, entity_id, value, icon):
        """Publish discovery + state for a single binary sensor entity."""
        self.mqtt.publish_binary_sensor_discovery(entity_id, icon)
        self.mqtt.publish_binary_sensor_state(value, entity_id)

    def _pub_warn(self, entity_id, value, icon):
        """Publish warning discovery + state for a single warn entity."""
        self.mqtt.publish_warn_discovery(entity_id, icon)
        self.mqtt.publish_warn_state(value, entity_id)

    # ------------------------------------------------------------------ #
    # Analog data
    # ------------------------------------------------------------------ #

    def publish_analog_data(self, pack_data):
        """
        Publish JK analog data.

        Args:
            pack_data: A single dict (one pack) with JK-native keys, as
                       returned by JKBMS485.get_jk_native_data().
        """
        if not pack_data:
            return

        packs = [pack_data] if isinstance(pack_data, dict) else pack_data

        self._publish_totals(packs)

        for idx, pack_data in enumerate(packs):
            self._publish_pack_analog(pack_data, idx + 1)

    # ------------------------------------------------------------------ #
    # Totals (aggregated across all packs)
    # ------------------------------------------------------------------ #

    def _publish_totals(self, packs):
        """Publish aggregate totals computed from all packs."""

        totals = {
            'packs_num': len(packs),
            'full_capacity': round(sum(p.get('full_capacity', 0) for p in packs), 2),
            'remain_capacity': round(sum(p.get('remain_capacity', 0) for p in packs), 2),
            'current': round(sum(p.get('current', 0) for p in packs), 2),
            'voltage': round(sum(p.get('voltage', 0) for p in packs) / len(packs), 2),
            'power': round(sum(p.get('power', 0) for p in packs), 1),
            'soh': round(sum(p.get('soh', 0) for p in packs) / len(packs), 1),
            'energy_charged': round(sum(p.get('energy_charged', 0) for p in packs), 2),
            'energy_discharged': round(sum(p.get('energy_discharged', 0) for p in packs), 2),
        }

        # Cell voltage extremes across all packs
        all_cells = [v for p in packs for v in p.get('cell_voltages', [])]
        if all_cells:
            totals['cell_voltage_max'] = max(all_cells)
            totals['cell_voltage_min'] = min(all_cells)
            totals['cell_voltage_diff'] = max(all_cells) - min(all_cells)

        # SOC from remain/full capacity
        remain = totals.get('remain_capacity', 0)
        full = totals.get('full_capacity', 0)
        totals['soc'] = round(remain / full * 100, 1) if full > 0 else 0

        total_defs = {
            'packs_num':         ('packs', 'mdi:database', 'null', 'measurement'),
            'full_capacity':     ('Ah', 'mdi:battery-high', 'null', 'measurement'),
            'remain_capacity':   ('Ah', 'mdi:battery-clock', 'null', 'measurement'),
            'current':           ('A', 'mdi:current-dc', 'current', 'measurement'),
            'soc':               ('%', 'mdi:battery-70', 'battery', 'measurement'),
            'voltage':           ('V', 'mdi:sine-wave', 'voltage', 'measurement'),
            'power':             ('kW', 'mdi:battery-charging', 'power', 'measurement'),
            'soh':               ('%', 'mdi:battery-plus-variant', 'null', 'measurement'),
            'energy_charged':    ('Wh', 'mdi:battery-positive', 'energy', 'total'),
            'energy_discharged': ('Wh', 'mdi:battery-negative', 'energy', 'total'),
            'cell_voltage_max':  ('mV', 'mdi:align-vertical-top', 'voltage', 'measurement'),
            'cell_voltage_min':  ('mV', 'mdi:align-vertical-bottom', 'voltage', 'measurement'),
            'cell_voltage_diff': ('mV', 'mdi:format-align-middle', 'voltage', 'measurement'),
        }

        for key, (unit, icon, devclass, stateclass) in total_defs.items():
            if key in totals:
                self._pub_sensor(
                    f'total_{key}', totals[key],
                    unit, icon, devclass, stateclass
                )

    # ------------------------------------------------------------------ #
    # Per-pack analog
    # ------------------------------------------------------------------ #

    def _publish_pack_analog(self, pack, pack_num):
        """Publish analog data for a single pack."""
        prefix = f'pack_{pack_num:02}'

        # Cell voltages
        cells = pack.get('cell_voltages', [])
        for i, mv in enumerate(cells):
            eid = f'{prefix}_cell_voltage_{i + 1:02}'
            self._pub_sensor(eid, mv, 'mV', 'mdi:sine-wave', 'voltage', 'measurement')

        # Temperatures
        temps = pack.get('temperatures', [])
        for i, t in enumerate(temps):
            eid = f'{prefix}_temperature_{i + 1:02}'
            self._pub_sensor(eid, t, '°C', 'mdi:thermometer', 'temperature', 'measurement')

        # Scalar sensor definitions: key -> (unit, icon, device_class, state_class)
        analog_defs = {
            'num_cells':         ('cells', 'mdi:database', 'null', 'measurement'),
            'cell_voltage_max':  ('mV', 'mdi:align-vertical-top', 'voltage', 'measurement'),
            'cell_voltage_min':  ('mV', 'mdi:align-vertical-bottom', 'voltage', 'measurement'),
            'cell_voltage_diff': ('mV', 'mdi:format-align-middle', 'voltage', 'measurement'),
            'current':           ('A', 'mdi:current-dc', 'current', 'measurement'),
            'voltage':           ('V', 'mdi:sine-wave', 'voltage', 'measurement'),
            'power':             ('kW', 'mdi:battery-charging', 'power', 'measurement'),
            'soc':               ('%', 'mdi:battery-70', 'battery', 'measurement'),
            'soh':               ('%', 'mdi:battery-plus-variant', 'null', 'measurement'),
            'remain_capacity':   ('Ah', 'mdi:battery-clock', 'null', 'measurement'),
            'full_capacity':     ('Ah', 'mdi:battery-high', 'null', 'measurement'),
            'design_capacity':   ('Ah', 'mdi:battery-high', 'null', 'measurement'),
            'cycle_count':       ('cycles', 'mdi:battery-sync', 'null', 'measurement'),
            'balance_current':   ('A', 'mdi:scale-balance', 'current', 'measurement'),
            'energy_charged':    ('Wh', 'mdi:battery-positive', 'energy', 'total'),
            'energy_discharged': ('Wh', 'mdi:battery-negative', 'energy', 'total'),
            'hardware_version':  ('', 'mdi:chip', 'null', 'null'),
            'software_version':  ('', 'mdi:application-cog', 'null', 'null'),
            'num_temps':         ('NTCs', 'mdi:database', 'null', 'measurement'),
            'temp_mos':          ('°C', 'mdi:thermometer', 'temperature', 'measurement'),
        }

        for key, (unit, icon, devclass, stateclass) in analog_defs.items():
            if key in pack:
                self._pub_sensor(
                    f'{prefix}_{key}', pack[key],
                    unit, icon, devclass, stateclass
                )

        # Binary sensors (MOS states)
        binary_defs = {
            'charge_mos':    'mdi:flash',
            'discharge_mos': 'mdi:flash',
            'balance_mos':   'mdi:scale-balance',
        }
        for key, icon in binary_defs.items():
            if key in pack:
                self._pub_binary(f'{prefix}_{key}', pack[key], icon)

    # ------------------------------------------------------------------ #
    # Warning / alarm data
    # ------------------------------------------------------------------ #

    def publish_warning_data(self, warn_data):
        """
        Publish JK warning/alarm data with JK-native entity names.

        Args:
            warn_data: List of pack warning dicts (as returned by
                       JKBMS485.get_warning_data()).
        """
        if not warn_data:
            return

        packs = [warn_data] if isinstance(warn_data, dict) else warn_data

        for idx, pack in enumerate(packs):
            self._publish_pack_warnings(pack, idx + 1)

    def _publish_pack_warnings(self, pack, pack_num):
        """Publish warning data for a single pack."""
        prefix = f'pack_{pack_num:02}'

        for key, value in pack.items():

            # Cell voltage warnings (per-cell array)
            if key == 'cell_voltage_warnings':
                icon = 'mdi:battery-heart-variant'
                for i, w in enumerate(value):
                    self._pub_warn(
                        f'{prefix}_cell_voltage_warning_{i + 1:02}',
                        w, icon
                    )

            # Temperature sensor warnings (per-sensor array)
            elif key == 'temp_sensor_warnings':
                icon = 'mdi:battery-heart-variant'
                for i, w in enumerate(value):
                    self._pub_warn(
                        f'{prefix}_temperature_warning_{i + 1:02}',
                        w, icon
                    )

            # Nested boolean dicts → binary sensors
            elif key in ('protect_state_1', 'protect_state_2'):
                icon = 'mdi:battery-alert'
                for sub_key, sub_value in value.items():
                    self._pub_binary(f'{prefix}_{sub_key}', sub_value, icon)

            elif key == 'fault_state':
                icon = 'mdi:alert'
                for sub_key, sub_value in value.items():
                    self._pub_binary(f'{prefix}_{sub_key}', sub_value, icon)

            elif key in ('warn_state_1', 'warn_state_2'):
                icon = 'mdi:battery-heart-variant'
                for sub_key, sub_value in value.items():
                    self._pub_binary(f'{prefix}_{sub_key}', sub_value, icon)

            elif key == 'instruction_state':
                icon = 'mdi:battery-check'
                for sub_key, sub_value in value.items():
                    self._pub_binary(f'{prefix}_{sub_key}', sub_value, icon)

            # Skip internal metadata keys
            elif key in ('cell_number', 'temp_sensor_number',
                         'control_state', 'balance_state_1', 'balance_state_2'):
                continue

            # Scalar warning sensor
            else:
                icon = 'mdi:battery-heart-variant'
                self._pub_warn(f'{prefix}_{key}', value, icon)

    # ------------------------------------------------------------------ #
    # Setup / config data (0x161E frame)
    # ------------------------------------------------------------------ #

    def publish_setup_data(self, setup_data):
        """
        Publish JK setup/config (0x161E) parameters.

        Args:
            setup_data: Dict with setup parameter keys, as returned by
                        JKBMS485.parse_jkbms_setup_frame().
        """
        if not setup_data:
            return

        setup_defs = {
            'cell_ovp_protect':       ('mV', 'mdi:shield-check', 'voltage', 'measurement'),
            'cell_uvp_protect':       ('mV', 'mdi:shield-check', 'voltage', 'measurement'),
            'cell_ovp_recover':       ('mV', 'mdi:shield-check', 'voltage', 'measurement'),
            'cell_uvp_recover':       ('mV', 'mdi:shield-check', 'voltage', 'measurement'),
            'battery_ovp_protect':    ('mV', 'mdi:shield-check', 'voltage', 'measurement'),
            'balancer_start_delta':   ('mV', 'mdi:scale-balance', 'voltage', 'measurement'),
            'battery_uvp_protect':    ('mV', 'mdi:shield-check', 'voltage', 'measurement'),
            'discharge_ocp_threshold': ('mA', 'mdi:current-ac', 'current', 'measurement'),
            'charge_ocp_threshold':   ('mA', 'mdi:current-ac', 'current', 'measurement'),
            'cell_balance_start':     ('mV', 'mdi:scale-balance', 'voltage', 'measurement'),
            'cell_balance_stop':      ('mV', 'mdi:scale-balance', 'voltage', 'measurement'),
        }

        for key, (unit, icon, devclass, stateclass) in setup_defs.items():
            if key in setup_data:
                self._pub_sensor(
                    f'setup_{key}', setup_data[key],
                    unit, icon, devclass, stateclass
                )
