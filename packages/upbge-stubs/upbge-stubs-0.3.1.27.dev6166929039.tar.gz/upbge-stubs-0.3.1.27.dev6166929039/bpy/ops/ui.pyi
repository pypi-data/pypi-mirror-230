"""


Ui Operators
************

:func:`assign_default_button`

:func:`button_execute`

:func:`button_string_clear`

:func:`copy_as_driver_button`

:func:`copy_data_path_button`

:func:`copy_python_command_button`

:func:`copy_to_selected_button`

:func:`drop_color`

:func:`drop_material`

:func:`drop_name`

:func:`editsource`

:func:`edittranslation_init`

:func:`eyedropper_color`

:func:`eyedropper_colorramp`

:func:`eyedropper_colorramp_point`

:func:`eyedropper_depth`

:func:`eyedropper_driver`

:func:`eyedropper_gpencil_color`

:func:`eyedropper_id`

:func:`jump_to_target_button`

:func:`list_start_filter`

:func:`override_idtemplate_clear`

:func:`override_idtemplate_make`

:func:`override_idtemplate_reset`

:func:`override_remove_button`

:func:`override_type_set_button`

:func:`reloadtranslation`

:func:`reset_default_button`

:func:`unset_property_button`

:func:`view_drop`

:func:`view_item_rename`

:func:`view_start_filter`

"""

import typing

import mathutils

def assign_default_button() -> None:

  """

  Set this property's current value as the new default

  """

  ...

def button_execute(skip_depressed: bool = False) -> None:

  """

  Presses active button

  """

  ...

def button_string_clear() -> None:

  """

  Unsets the text of the active button

  """

  ...

def copy_as_driver_button() -> None:

  """

  Create a new driver with this property as input, and copy it to the internal clipboard. Use Paste Driver to add it to the target property, or Paste Driver Variables to extend an existing driver

  """

  ...

def copy_data_path_button(full_path: bool = False) -> None:

  """

  Copy the RNA data path for this property to the clipboard

  """

  ...

def copy_python_command_button() -> None:

  """

  Copy the Python command matching this button

  """

  ...

def copy_to_selected_button(all: bool = True) -> None:

  """

  Copy the property's value from the active item to the same property of all selected items if the same property exists

  """

  ...

def drop_color(color: mathutils.Color = (0.0, 0.0, 0.0), gamma: bool = False) -> None:

  """

  Drop colors to buttons

  """

  ...

def drop_material(session_uuid: int = 0) -> None:

  """

  Drag material to Material slots in Properties

  """

  ...

def drop_name(string: str = '') -> None:

  """

  Drop name to button

  """

  ...

def editsource() -> None:

  """

  Edit UI source code of the active button

  """

  ...

def edittranslation_init() -> None:

  """

  Edit i18n in current language for the active button

  """

  ...

def eyedropper_color() -> None:

  """

  Sample a color from the Blender window to store in a property

  """

  ...

def eyedropper_colorramp() -> None:

  """

  Sample a color band

  """

  ...

def eyedropper_colorramp_point() -> None:

  """

  Point-sample a color band

  """

  ...

def eyedropper_depth() -> None:

  """

  Sample depth from the 3D view

  """

  ...

def eyedropper_driver(mapping_type: str = 'SINGLE_MANY') -> None:

  """

  Pick a property to use as a driver target

  """

  ...

def eyedropper_gpencil_color(mode: str = 'MATERIAL') -> None:

  """

  Sample a color from the Blender Window and create Grease Pencil material

  """

  ...

def eyedropper_id() -> None:

  """

  Sample a data-block from the 3D View to store in a property

  """

  ...

def jump_to_target_button() -> None:

  """

  Switch to the target object or bone

  """

  ...

def list_start_filter() -> None:

  """

  Start entering filter text for the list in focus

  """

  ...

def override_idtemplate_clear() -> None:

  """

  Delete the selected local override and relink its usages to the linked data-block if possible, else reset it and mark it as non editable

  """

  ...

def override_idtemplate_make() -> None:

  """

  Create a local override of the selected linked data-block, and its hierarchy of dependencies

  """

  ...

def override_idtemplate_reset() -> None:

  """

  Reset the selected local override to its linked reference values

  """

  ...

def override_remove_button(all: bool = True) -> None:

  """

  Remove an override operation

  """

  ...

def override_type_set_button(all: bool = True, type: str = 'REPLACE') -> None:

  """

  Create an override operation, or set the type of an existing one

  """

  ...

def reloadtranslation() -> None:

  """

  Force a full reload of UI translation

  """

  ...

def reset_default_button(all: bool = True) -> None:

  """

  Reset this property's value to its default value

  """

  ...

def unset_property_button() -> None:

  """

  Clear the property and use default or generated value in operators

  """

  ...

def view_drop() -> None:

  """

  Drag and drop onto a data-set or item within the data-set

  """

  ...

def view_item_rename() -> None:

  """

  Rename the active item in the data-set view

  """

  ...

def view_start_filter() -> None:

  """

  Start entering filter text for the data-set in focus

  """

  ...
