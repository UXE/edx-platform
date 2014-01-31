import json
import sys
from mock import Mock, patch
from django.test.utils import override_settings
from xmodule.modulestore.tests.factories import CourseFactory, ItemFactory
from xmodule.modulestore.tests.django_utils import ModuleStoreTestCase
from courseware.tests.tests import TEST_DATA_MONGO_MODULESTORE
from xmodule.modulestore import Location
from xmodule.course_module import CourseDescriptor
from xmodule.modulestore.django import modulestore


@override_settings(MODULESTORE=TEST_DATA_MONGO_MODULESTORE)
class TestUnitVisibility(ModuleStoreTestCase):
    """
    This test exercises the 'unit visibility' feature code. The feature is primarily visible when
    a course overview/outline view is opened in the Studio tool. The main functional elements are these:

        * Where units are shown on the page, one new visual element has been added
            - An icon to the far right in the unit's presentation block
                This icon indicates the public/private state of the unit.

                The user may click on the icon to request a toggle of the public/private state. Before
                the change is made a confirmation dialog is presented to the user. Either the user
                confirms the action or cancels the dialog, aborting the requested operation.

        * Where subsections are shown on the page, two new visual elements have been added
            - An icon to the far right in the unit's presentation block
                This icon indicates the public/private state of the units assigned to the subsection.
                Here there are three possible states for the icon to display: all units public, all units
                private, or a mix of the two.

                The user may click on the icon to request a change of state for all the assigned units. All
                public changes to all private (and vice versa). When there is a mix of public/private, the
                only available change is to make all units public.

                Before the change is made a confirmation dialog is presented to the user. Either the user
                confirms the action or cancels the dialog, aborting the requested operation.

            - A colored bar to the far left of the subsection's name
                This bar indicates the public/published state of the subsection. There are four possible
                states:
                    All public units and publication date > NOW
                    All public units and publication date < NOW
                    Some non-public units and publication date > NOW
                    Some non-public units and publication date < NOW

        * Where units are shown on the page, one new visual element has been added
            - An icon to the far right in the unit's presentation block
                This icon indicates the public/private state of the units assigned to the section.
                Here there are three possible states for the icon to display: all units public, all units
                private, or a mix of the two.

                The user may click on the icon to request a toggle of the public/private state. Before
                the change is made a confirmation dialog is presented to the user. Either the user
                confirms the action or cancels the dialog, aborting the requested operation.

    The test situation for this test (established at setup time) is a simple course with only two sections, Dog and Cat.
    Each section has two subsections and each of those, in turn, have two units. This is the schematic representation
    of the course:

        Course
            Section: Dog
                Subsection: Best Friend
                    Unit_1a
                    Unit_1b
                Subsection: Loyal Companion
                    Unit_2a
                    Unit_2b

            Section: Cat
                Subsection: Aloof
                    Unit_3a
                    Unit_3b
                Subsection: Opportunistic Companion
                    Unit_4a
                    Unit_4b
    """
    def setUp(self):
        # ______________________________________ Course
        self.course = CourseFactory.create()
        sys.stdout.write(str("\ncourse: " + str(self.course.location) + "\n"))

        # ______________________________________ Sections
        self.section_dog = ItemFactory.create(
            parent_location=self.course.location,
            category="chapter",
            display_name="Dog",
        )
        sys.stdout.write(str("\n    section_dog: " + str(self.section_dog.location) + "\n"))

        self.section_cat = ItemFactory.create(
            parent_location=self.course.location,
            category="chapter",
            display_name="Cat",
        )
        sys.stdout.write(str("\n    section_cat: " + str(self.section_cat.location) + "\n"))

        # ______________________________________ Subsections
        self.sub_section_best_friend = ItemFactory.create(
            parent_location=self.section_dog.location,
            category="sequential",
            display_name="Best Friend",
        )
        sys.stdout.write(str("\n        sub_section_best_friend: " + str(self.sub_section_best_friend.location) + "\n"))

        self.sub_section_loyal_companion = ItemFactory.create(
            parent_location=self.section_dog.location,
            category="sequential",
            display_name="Loyal Companion",
        )
        sys.stdout.write(str("\n        sub_section_loyal_companion: " + str(self.sub_section_loyal_companion.location) + "\n"))

        self.sub_section_aloof = ItemFactory.create(
            parent_location=self.section_cat.location,
            category="sequential",
            display_name="Aloof",
        )
        sys.stdout.write(str("\n        sub_section_aloof: " + str(self.sub_section_aloof.location) + "\n"))

        self.sub_section_opportunistic_companion = ItemFactory.create(
            parent_location=self.section_cat.location,
            category="sequential",
            display_name="Opportunistic Companion",
        )
        sys.stdout.write(str("\n        sub_section_opportunistic_companion: " + str(self.sub_section_opportunistic_companion.location) + "\n"))

        # ______________________________________ Units
        self.unit_1a = ItemFactory.create(
            parent_location=self.sub_section_best_friend.location,
            category="vertical",
            display_name="Unit 1a",

        )
        sys.stdout.write(str("\n                unit_1a: " + str(self.unit_1a.location) + "\n"))

        self.unit_1b = ItemFactory.create(
            parent_location=self.sub_section_best_friend.location,
            category="vertical",
            display_name="Unit 1b",

        )
        sys.stdout.write(str("\n                unit_1b: " + str(self.unit_1b.location) + "\n"))

        self.unit_2a = ItemFactory.create(
            parent_location=self.sub_section_loyal_companion.location,
            category="vertical",
            display_name="Unit 2a",

        )
        sys.stdout.write(str("\n                unit_2a: " + str(self.unit_2a.location) + "\n"))

        self.unit_2b = ItemFactory.create(
            parent_location=self.sub_section_loyal_companion.location,
            category="vertical",
            display_name="Unit 2b",

        )
        sys.stdout.write(str("\n                unit_2b: " + str(self.unit_2b.location) + "\n"))

        self.unit_3a = ItemFactory.create(
            parent_location=self.sub_section_aloof.location,
            category="vertical",
            display_name="Unit 3a",

        )
        sys.stdout.write(str("\n                unit_3a: " + str(self.unit_3a.location) + "\n"))

        self.unit_3b = ItemFactory.create(
            parent_location=self.sub_section_aloof.location,
            category="vertical",
            display_name="Unit 3b",

        )
        sys.stdout.write(str("\n                unit_3b: " + str(self.unit_3b.location) + "\n"))

        self.unit_4a = ItemFactory.create(
            parent_location=self.sub_section_opportunistic_companion.location,
            category="vertical",
            display_name="Unit 4a",

        )
        sys.stdout.write(str("\n                unit_4a: " + str(self.unit_4a.location) + "\n"))

        self.unit_4b = ItemFactory.create(
            parent_location=self.sub_section_opportunistic_companion.location,
            category="vertical",
            display_name="Unit 4b",

        )
        sys.stdout.write(str("\n                unit_4b: " + str(self.unit_4b.location) + "\n"))


    def test_get_unit_by_locator(self, draft=False):
        '''
        Attempt to reference a single unit
        '''
        #sys.stdout.write(str("\nunit_1a: " + str(self.unit_1a.location) + "\n"))

        store = modulestore('direct')
        unit = store.get_item(self.unit_1a.location)

        self.assertEquals(1, 0)


