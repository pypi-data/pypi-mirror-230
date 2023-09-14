from extras.plugins import PluginMenuButton, PluginMenuItem
from utilities.choices import ButtonColorChoices

menu_items = (
    PluginMenuItem(
        link="plugins:netbox_software_tracker:goldenimage_list",
        link_text="Golden Images",
    ),
    PluginMenuItem(
        link="plugins:netbox_software_tracker:softwareimage_list",
        link_text="Software Images",
        buttons=[
            PluginMenuButton(
                link="plugins:netbox_software_tracker:softwareimage_add",
                title="Add",
                icon_class="mdi mdi-plus-thick",
                color=ButtonColorChoices.GREEN
            )
        ]
    ),
)