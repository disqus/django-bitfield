django-bitfield
---------------

Provides a BitField like class (using a BigIntegerField) for your Django models.

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

Now you can use the field using very familiar Django operations::

	# Create the model 
	o = MyModel.objects.create(flags=0)

	# Add awesome_flag (does not work in SQLite)
	MyModel.objects.filter(pk=o.pk).update(flags=MyModel.flags.awesome_flag)

	# Set flags manually to [awesome_flag, flaggy_foo]
	MyModel.objects.filter(pk=o.pk).update(flags=3)
	
	# Remove awesome_flag (does not work in SQLite)
	MyModel.objects.filter(pk=o.pk).update(flags=~MyModel.flags.awesome_flag)
	
	# Test awesome_flag
	if o.flags.awesome_flag:
	    print "Happy times!"
	
	# List all flags on the field
	for f in o.flags:
	    print f

Enjoy!