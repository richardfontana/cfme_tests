Development Tips and Tricks
===========================

Introduction
------------

This document is intended to explain some of the extra bits of the framework that are there to
make your life easier. Not everything is included here and we encourage people to add new tricks
as they are developed and rediscovered.

.. _blockers:


Version Picking
---------------

Dealing with multiple releases, it's obvious that some things change from version to version. A lot
of the time, these changes are simple, such as a string change. So that we can continue using the same
codebase for any version, we define the idea of version picking. Version picking essentially returns
an object depending on the version of an appliance. It's particularly useful for things like locator
changes because most of the element handling routines are version picking away. This means if they
receive a dict as an argument, they will automatically try to resolve it using the version picking tool.
To use version picking is easy::

    from utils import version

    version.pick({'5.4': "Houses",
                  '5.3': "House",
                  version.LOWEST: "Boat"})

In this example, if the version is below 5.3, the ``Boat`` will be returned. Anything between 5.3 and 5.4
will return ``House`` and anything over 5.4 will return ``Houses``. There is also a ``version.LATEST``
which points to upstream appliances.

Defining blockers
-----------------

Sometimes we know a test fails due to a bug in the codebase. In order to make sure the test isn't run
and attributing an extra fail that doesn't need to be investigated, we mark it with a meta marker.
The meta marker is incredibly useful and integrates with our Bugzilla implementation to ensure that
if a bug is still on DEV, or hasn't even been assigned yet, that the test won't run. The syntax is
really easy::

    @pytest.mark.meta(blockers=[12345, 12346])
    def test_my_feature():
        # Test the new feature
        pass

Note the two bug numbers 12345 and 12346. More information can be found in the :py:mod:`fixtures.blockers`
fixture.

Using blockers in tests
-----------------------

On the odd occasion, you don't want to disable an entire test, but just a part of it, until a bug
is fixed. To do this, we can specify a bug object and ask the framework to skip if a certain bug
exists and is not closed. The syntax is pretty simple::

    def my_test(provider, bug):
        ui_bug = bug(12234)
        if not ui_bug:
            # Do something unless the bug is still present in which case, it will be skipped

Uncollecting tests
------------------

There are times when conditions dictate that we don't need to run a test if a certain condition
is true. Imagine you don't want to run a test if the appliance version is below a certain value.
In these instances, you can use ``uncollectif`` which is a pytest marker::

    @pytest.mark.uncollectif(lambda: version.current_version() < '5.3')
    def test_my_feature():
        # Test the new feature
        pass

Now if the version of the appliance is less than 5.3. Then the test will not be skipped, it will
never even try to be run. This is ONLY to be used when a certain test is not valid for a certain
reason. it is NOT to be used if there is a bug in the code. See the :ref:`blockers` section above for
skipping because of a bug.

.. _appliance_stack:

Running commands on another appliance
-------------------------------------

We implement a small appliance stack in the framework. When a test first starts it loads up the
base_url appliance as the first appliance in the stack. From then on, all the browsing operations,
database operations and ssh commands are run on the top appliance in the stack. From time to time
it becomes necessary to run commands on another appliance. Let's say you were trying to get two
appliances to talk to each other, in this case, you would use the context manager for appliances.

By default, even if you add a new appliance onto the stack, the browser operations will keep
happening on the last appliance that was used, however, there is a simple way to steal the browsers
focus, and this is detailed in the example below::

    appl1.ipapp.browser_steal = True
    with appl1.ipapp:
        provider_crud.create()

In the example we have already created a new :py:class:`utils.appliance.Appliance` object and
called it ``appl1``. Then we have set it to steal the browser focus. After this, we enter the
context manager ``appl1.ipapp`` and are able to run operations like provider creates.

This is also why you should use ``ssh_client`` and ``db`` access from the ``store.current_appliance``
and not from the modules directly. If someone else uses your code and is inside an appliance
context manager, the commands could be run against the wrong appliance.

Invalidating cached data
------------------------

In order to speed things up, we cache certain items of data, such as the appliances version and
configuration details. When these get changed, the cache becomes invalid and we must invalidate
the cache somehow. It's not as tricky as it sounds. We have created a signals module to help with
this. You can find the list of used signals in the :py:mod:`utils.signals` file. An example of this would
be the server name. If the server name is changed. We need to invalidate the cache. To do this, we
do the following::

    def update(self):
        """ Navigate to a correct page, change details and save.

        """
        sel.force_navigate("cfg_settings_currentserver_server")
        fill(self.basic_information, self.details)
        # Workaround for issue with form_button staying dimmed.
        if self.details["appliance_zone"] is not None and current_version() < "5.3":
            sel.browser().execute_script(
                "$j.ajax({type: 'POST', url: '/ops/settings_form_field_changed/server',"
                " data: {'server_zone':'%s'}})" % (self.details["appliance_zone"]))
        sel.click(form_buttons.save)
        # TODO: Maybe make a cascaded delete on lazycache?
        fire('server_details_changed')

Notice the last line in this snippet which fires off the ``server_details_changed`` signal. You as the
user don't need to care how to invalidate the cache, you just need to let the system know you've done
it. Any time any one updates the server details using the
:py:class:`cfme.configure.configuration.BasicInformation` class from the configuration
module, this signal will automatically be fired, so unless you are doing something out of the ordinary,
you shouldn't have to worry about it. However the signals are there if you need to. Note that the cache
invalidation happens on the ``current_appliance`` in the stack. See the :ref:`appliance_stack` section
for more details.

pytest store
------------

The pytest store provides access to common pytest data structures and instances that may not be readily available elsewhere. It can be found in :py:mod:`fixtures.pytest_store`, and during a test run is exposed on the pytest module in the store namespace as ``pytest.store``.

Test generation (testgen)
-------------------------

We try to consolidate common test generation functions in the :py:mod:`utils.testgen` module. When parametrizing tests with the ``pytest_generate_tests`` hook, check the testgen module to see if there are functions available that already parametrize on the axis you want (usually by provider, but there are some other helpers in there).

Working with file paths
-----------------------
For any path in the project root, there are several helper functions that can be used.  Look at the :py:mod:`utils.path` module for the complete list of pre-configured directories and available functions.
