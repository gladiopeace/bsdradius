"""
html form class.
"""

# HeadURL		$HeadURL: file:///Z:/backup/svn/webstuff/tags/release20061229_v_1_0_0/webstuff/webform.py $
# Author:		$Author: atis $
# File version:	$Revision: 63 $
# Last changes:	$Date: 2006-08-02 14:02:00 +0300 (Tr, 02 Aug 2006) $


from logger import *
import Typecast
web = None



class InputField:
	"""Input field base class."""

	name = ""
	value_type = ""
	submitted_value = None
	default = None
	value = None
	required = True
	error = False



	def __init__(self, value_type, default=None, req=False):
		self.value_type = value_type
		self.required = req
		self.default = default
		self.value = default



	def setName(self, name):
		self.name = name

	
	
	def setValue(self, value):
		pass



	def submitted(self):
		if web.getvar(self.name) == None:
			return False
		return True



	def setSubmittedValue(self):
		self.submitted_value = web.getvar(self.name)



	def validate(self):
		try:
			method = Typecast.typecastMethods[self.value_type]
			self.value = method(self.submitted_value)
		except:
			self.error = True
			return False

		self.error = False
		return True



	def fillTemplate(self, template):
		try:
			method = Typecast.typecastMethods[self.value_type]
			if self.submitted_value != None:
				value = method(self.submitted_value)
			else:
				value = method(self.value)
		except:
			value = self.submitted_value

		setattr(template, self.name, value)
		label_style = "ok_label"
		if self.error == True:
			label_style = "error_label"
		setattr(template, self.name + "_style", label_style)
		
	

class TextField(InputField):
	"""Textual input."""

	def __init__(self, value_type="str", default="", req=False):
		InputField.__init__(self, value_type, default, req)


	
	def validate(self):
		# check for an empty value
		if self.required == True and self.submitted_value == "":
			self.error = True
			return False

		return InputField.validate(self)



class SelectField(InputField):
	"""Selection."""

	options = []



	def __init__(self, value_type="int", default=None, req=True):
		InputField.__init__(self, value_type, default, req)



	def setOptions(self, opt_list):
		self.options = opt_list



	def fillTemplate(self, template):
		try:
			method = Typecast.typecastMethods[self.value_type]
			if self.submitted_value != None:
				value = method(self.submitted_value)
			else:
				value = method(self.value)
		except:
			value = self.submitted_value

		if len(self.options) == 0:
			self.options = [("", "---")]

		optstring = ""
		for k, v in self.options:
			if k == value:
				selstr = ' selected="selected"'
			else:
				selstr = ''
			optstring += "<option value=\"%s\"%s>%s</option>\n" % (str(k), selstr, str(v))

		setattr(template, self.name, optstring)
		label_style = "ok_label"
		if self.error == True:
			label_style = "error_label"
		setattr(template, self.name + "_style", label_style)



class DateField(InputField):
	"""Date field."""

	year_select = None
	month_select = None
	day_select = None
	


	def __init__(self, value_type="date", default="2006-01-01", req=True):
		InputField.__init__(self, value_type, default, req)

		split = default.split('-')

		self.year_select = SelectField(default=split[0])
		self.month_select = SelectField(default=split[1])
		self.day_select = SelectField(default=split[2])

		# set default options
		self.year_select.setOptions([(2004, "2004")])
		self.month_select.setOptions([(1, "January")])
		day_opt = []
		for d in xrange(1, 32):
			day_opt.append((d, str(d)))
		self.day_select.setOptions(day_opt)



	def setName(self, name):
		self.name = name
		self.year_select.setName(name + "_year")
		self.month_select.setName(name + "_month")
		self.day_select.setName(name + "_day")


	
	def submitted(self):
		if self.year_select.submitted() and \
		    self.month_select.submitted() and \
		    self.day_select.submitted():
			return True
		return False



	def setSubmittedValue(self):
		self.year_select.setSubmittedValue()
		self.month_select.setSubmittedValue()
		self.day_select.setSubmittedValue()

		year = str(self.year_select.submitted_value)
		month = str(self.month_select.submitted_value).rjust(2, '0')
		day = str(self.day_select.submitted_value).rjust(2, '0')

		self.submitted_value = "%s-%s-%s" % (year, month, day)



	def validate(self):
		self.year_select.validate()
		self.month_select.validate()
		self.day_select.validate()

		if self.year_select.error or \
		    self.month_select.error or \
		    self.day_select.error:
			self.error = True
			return False

		year = str(self.year_select.value)
		month = str(self.month_select.value).rjust(2, '0')
		day = str(self.day_select.value).rjust(2, '0')
		self.value = "%s-%s-%s" % (year, month, day)
		self.error = False
		return True



	def fillTemplate(self, template):
		self.year_select.fillTemplate(template)
		self.month_select.fillTemplate(template)
		self.day_select.fillTemplate(template)
		
		label_style = "ok_label"
		if self.error == True:
			label_style = "error_label"
		setattr(template, self.name + "_style", label_style)



	def setYearOptions(self, year_opt):
		my_year_opt = []
		for year in year_opt:
			my_year_opt.append((year, str(year)))
		self.year_select.setOptions(my_year_opt)
		


	def setMonthOptions(self, month_opt):
		self.month_select.setOptions(month_opt)
	


class CheckboxField(InputField):
	"""Checkbox."""
	
	def __init__(self, value_type = "int", default = 1, req = True):
		InputField.__init__(self, value_type, default, req)



class WebForm:
	"""A web form is a collection of input fields."""

	fields = {}



	# input field classes
	TextField = TextField
	SelectField = SelectField
	CheckboxField = CheckboxField
	DateField = DateField



	# form state constants
	STAT_NONE = -1
	STAT_FAIL = 0
	STAT_OK = 1
	


	def __init__(self):
		self.__dict__["fields"] = {}



	def validate(self):
		is_valid = True
		for name, field in self.fields.iteritems():
			if field.validate() == False:
				is_valid = False
		return is_valid



	def submitted(self):
		for name, field in self.fields.iteritems():
			if not field.submitted():
				debug ("not submitted: " + field.name)
				return False
		return True



	# add/change field
	def __setattr__(self, name, value):
		# check if it's a normal attribute
		if self.__dict__.has_key(name):
			self.__dict__[name] = value
			return

		# assume it's a field
		value.setName(name)
		self.fields[name] = value



	# get field reference
	def __getattr__(self, name):
		return self.fields[name]



	def setSubmittedValues(self):
		for name, field in self.fields.iteritems():
			field.setSubmittedValue()
			


	def fillTemplate(self, template):
		for name, field in self.fields.iteritems():
			field.fillTemplate(template)



	def clear(self):
		"""Clear submitted field values"""
		
		for name, field in self.fields.iteritems():
			field.submitted_value = None
			field.value = field.default
			field.error = False
			
