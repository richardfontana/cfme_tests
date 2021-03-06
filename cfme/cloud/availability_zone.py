""" A page functions for Availability Zone


:var list_page: A :py:class:`cfme.web_ui.Region` object describing elements on the list page.
:var details_page: A :py:class:`cfme.web_ui.Region` object describing elements on the detail page.
"""

from cfme.web_ui import Region, SplitTable


# Page specific locators
list_page = Region(
    locators={
        'zone_table': SplitTable(header_data=('//div[@class="xhdr"]/table/tbody', 1),
            body_data=('//div[@class="objbox"]/table/tbody', 1))
    },
    title='Availability Zones')


details_page = Region(infoblock_type='detail')
