# Translation state keys

Entity names, enum states, select options, fan presets, and action errors are
translated into the language selected in Home Assistant. English, Dutch, and
German catalogs are included.

This update replaces English state labels with stable lowercase translation keys.
Review automations, scripts, and templates that compare enum states or pass
select options or fan presets. Use the new key in configuration; Home Assistant
displays its translated label in the interface.

| Entity or attribute | Previous value | New value |
| --- | --- | --- |
| Ventilation level sensor | `Off`, `Low`, `Medium`, `High`, `CN1` | `off`, `low`, `medium`, `high`, `cn1` |
| Ventilation level select | `Level 0`, `Level 1`, `Level 2`, `Level 3`, `CN1` | `level_0`, `level_1`, `level_2`, `level_3`, `cn1` |
| Operating mode select | `Automatic mode`, `Manual`, `Holiday mode`, `Party mode`, `Night ventilation mode` | `automatic_mode`, `manual`, `holiday_mode`, `party_mode`, `night_ventilation_mode` |
| Fan `preset_mode` | `Automatic`, `Manual`, `Holiday`, `Party`, `Night ventilation` | `automatic`, `manual`, `holiday`, `party`, `night_ventilation` |
| Valve control select | `Relais output 1`, `Relais output 2`, `Analog output 1`, `analog output 2` | `relais_output_1`, `relais_output_2`, `analog_output_1`, `analog_output_2` |
| Contact conditions select | `Only filtercondition`, `Only faultcondition`, `Filter and fault condition` | `only_filtercondition`, `only_faultcondition`, `filter_and_fault_condition` |

Other API option labels follow Home Assistant's `slugify` conversion: lowercase,
spaces and punctuation replaced by underscores, and accented characters converted
to their ASCII equivalents. For example, `Supply fan off` becomes `supply_fan_off`
and `Min. ventilation 50 m³/h` becomes `min_ventilation_50_m3_h`.

Select states already expressed as lowercase keys, such as `very_low` and
`on_if_bypass_conditions_met`, keep those keys. The numeric values sent to Brink
remain the same, including negative humidity sensitivity values. CN1 remains
controlled by the external input and cannot be selected through an action.

Update `select.select_option` calls to pass the new option key and
`fan.set_preset_mode` calls to pass the new preset key. For example, use `manual`
instead of `Manual`. Update state triggers and template comparisons in the same
way. Check the entity's current options in Developer Tools after reloading the
integration.
