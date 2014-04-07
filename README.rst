django-bitfield
---------------

.. image:: https://api.travis-ci.org/disqus/django-bitfield.png?branch=master

Provides a BitField like class (using a BigIntegerField) for your Django models.

(If you're upgrading from a version before 1.2 the API has changed greatly and is backwards incompatible!)

Requirements
============

* Django >= 1.2

Note: SQLite does not support save operations using a ``Bit`` (per the example under Usage)

Installation
============

Install it with pip (or easy_install)::

	pip install django-bitfield

Usage
=====

First you'll need to attach a BitField to your class. This acts as a BigIntegerField (BIGINT) in your database::

	from bitfield import BitField

	class MyModel(models.Model):
	    flags = BitField(flags=(
	        'awesome_flag',
	        'flaggy_foo',
	        'baz_bar',
	    ))

Flags can also be defined with labels::

	class MyModel(models.Model):
	    flags = BitField(flags=(
	        ('awesome_flag', 'Awesome Flag!'),
	        ('flaggy_foo', 'Flaggy Foo'),
	        ('baz_bar', 'Baz (bar)'),
	    ))

Now you can use the field using very familiar Django operations::

	# Create the model
	o = MyModel.objects.create(flags=0)

	# Add awesome_flag (does not work in SQLite)
	MyModel.objects.filter(pk=o.pk).update(flags=F('flags').bitor(MyModel.flags.awesome_flag))

	# Set flags manually to [awesome_flag, flaggy_foo]
	MyModel.objects.filter(pk=o.pk).update(flags=MyModel.flags.awesome_flag | MyModel.flags.flaggy_foo)

	# Remove awesome_flag (does not work in SQLite)
	MyModel.objects.filter(pk=o.pk).update(flags=F('flags').bitand(~MyModel.flags.awesome_flag))

	# Find by awesome_flag
	MyModel.objects.filter(flags=MyModel.flags.awesome_flag)

	# Exclude by awesome_flag
	MyModel.objects.filter(flags=~MyModel.flags.awesome_flag)

	# Test awesome_flag
	if o.flags.awesome_flag:
	    print "Happy times!"

	# List all flags on the field
	for f in o.flags:
	    print f

	# Get a flag label
	print o.flags.get_label('awesome_flag')

Enjoy!

Admin
=====

To use the widget in the admin, you'll need to update your ModelAdmin. Add the
following lines to your ModelAdmin::

	formfield_overrides = {
		BitField: {'widget': BitFieldCheckboxSelectMultiple},
	}

Make sure you've imported the classes by adding these lines to the top of the file::

	from bitfield import BitField
	from bitfield.forms import BitFieldCheckboxSelectMultiple

There is also a ``BitFieldListFilter`` list filter (Django 1.4 or newer).
To use it set ``list_filter`` ModelAdmin option::

    list_filter = (
            ('flags', BitFieldListFilter,)
            )

BitFieldListFilter is in ``bitfield.admin`` module::

    from bitfield.admin import BitFieldListFilter
