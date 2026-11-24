app_name = "dsa_loan"
app_title = "DSA Loan Portal"
app_publisher = "Naveed Ahmed"
app_description = "Direct Selling Agent Loan Management System"
app_email = "123naveedahmed@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "dsa_loan",
# 		"logo": "/assets/dsa_loan/logo.png",
# 		"title": "DSA Loan Portal",
# 		"route": "/dsa_loan",
# 		"has_permission": "dsa_loan.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/dsa_loan/css/dsa_loan.css"
# app_include_js = "/assets/dsa_loan/js/dsa_loan.js"

# include js, css files in header of web template
# web_include_css = "/assets/dsa_loan/css/dsa_loan.css"
# web_include_js = "/assets/dsa_loan/js/dsa_loan.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "dsa_loan/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "dsa_loan/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "dsa_loan.utils.jinja_methods",
# 	"filters": "dsa_loan.utils.jinja_filters"
# }

# Installation
# ------------

# Roles must exist before the DocType permissions that use them are synced.
before_install = "dsa_loan.dsa_loan_portal.access.create_roles"
before_migrate = "dsa_loan.dsa_loan_portal.access.create_roles"
# Lender invoicing: service item, default email template, DSA Accounts access to Sales Invoice
after_install = "dsa_loan.dsa_loan_portal.invoicing.after_migrate"
after_migrate = "dsa_loan.dsa_loan_portal.invoicing.after_migrate"

scheduler_events = {
	"monthly": ["dsa_loan.dsa_loan_portal.automation.create_monthly_payout_statements"],
}

doc_events = {
	"Commission Calculation": {
		"on_update": "dsa_loan.dsa_loan_portal.invoicing.on_commission_update",
	},
}

# Uninstallation
# ------------

# before_uninstall = "dsa_loan.uninstall.before_uninstall"
# after_uninstall = "dsa_loan.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "dsa_loan.utils.before_app_install"
# after_app_install = "dsa_loan.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "dsa_loan.utils.before_app_uninstall"
# after_app_uninstall = "dsa_loan.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "dsa_loan.build.after_build"

# To hook into the build process of other apps
# The list of apps being built is passed as an argument

# after_app_build = "dsa_loan.build.after_app_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "dsa_loan.notifications.get_notification_config"

# Awesome Bar
# -----------
# Extra search results: list of dicts with label, description, route, index.
# route: ["List", "ToDo"], "/desk/docs/some/page", or "https://example.com"
# awesomebar_search = ["dsa_loan.search.awesomebar_results"]

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"dsa_loan.tasks.all"
# 	],
# 	"daily": [
# 		"dsa_loan.tasks.daily"
# 	],
# 	"hourly": [
# 		"dsa_loan.tasks.hourly"
# 	],
# 	"weekly": [
# 		"dsa_loan.tasks.weekly"
# 	],
# 	"monthly": [
# 		"dsa_loan.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "dsa_loan.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "dsa_loan.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "dsa_loan.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["dsa_loan.utils.before_request"]
# after_request = ["dsa_loan.utils.after_request"]

# Job Events
# ----------
# before_job = ["dsa_loan.utils.before_job"]
# after_job = ["dsa_loan.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"dsa_loan.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

