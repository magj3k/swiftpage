from util.elements import *
from addons.addons_server import *
from page import *

# modifies page through addons
page = AddonsModifier(page).generate()

page.check() # prints relevant design warnings and tips
page.write() # saves webpage to specified destination
