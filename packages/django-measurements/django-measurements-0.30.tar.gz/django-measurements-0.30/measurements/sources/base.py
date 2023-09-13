# Source classes should not include reference to django
# This will facilitate use of functionalities within other packages/projects
# Django-related tasks (eg. uom conversion, fieldname mapping) should be moved
# into utilis or management commands

class BaseSource(object):
    def get_data(self):
        pass

