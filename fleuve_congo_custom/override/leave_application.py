from hrms.hr.doctype.leave_application.leave_application import LeaveApplication
import frappe
from frappe import _
from frappe.utils import getdate, flt
#from fleuve_congo_custom.fleuve_congo_custom.doctype.provision.provision import get_provision_ratio

class CustomLeaveApplication(LeaveApplication):
	def before_save(self):
		if self.cash_collected :
			total_jours = 0
			montant = 0.0

			prov = frappe.db.sql(
				"""
				SELECT r.total
				FROM tabProvision p INNER JOIN `tabProvision Ratio` r ON p.name = r.parent
				WHERE r.employee = %(employee)s AND YEAR(p.end_date) = %(fiscal_year)s
				""", 
				{"fiscal_year":int(getdate(self.to_date).year), "employee": self.employee}, as_dict=1
			)
			if prov:
				total_jours = prov[0].total

				prov = frappe.db.sql(
					"""
					SELECT r.total
					FROM tabProvision p INNER JOIN `tabProvision Conge` r ON p.name = r.parent
					WHERE r.employee = %(employee)s AND YEAR(p.end_date) = %(fiscal_year)s
					""", 
					{"fiscal_year":int(getdate(self.to_date).year), "employee": self.employee}, as_dict=1
				)
				montant = prov[0].total

				if total_jours > 0 :
					if self.total_leave_days <= total_jours:
						self.amount = self.total_leave_days / total_jours * montant
					else:
						self.amount = montant

	def on_submit(self):
		frappe.db.sql(
			"""
			UPDATE `tabProvision Ratio` r INNER JOIN  tabProvision p ON p.name = r.parent
			SET r.pris =r.pris + %(pris)s, r.total = r.total - %(pris)s
			WHERE r.employee = %(employee)s AND %(to_date)s BETWEEN p.start_date AND end_date
			""", {"pris": int(self.total_leave_days), "employee": self.employee, "to_date": self.to_date } 
		)
		#calculer le valeur des congés à prendre à afficher sur leaves application
		frappe.db.sql(
			"""
			UPDATE `tabProvision Conge` r INNER JOIN  tabProvision p ON p.name = r.parent
			SET r.pris = r.pris + %(pris)s, r.total = r.total - %(pris)s
			WHERE r.employee = %(employee)s AND %(to_date)s BETWEEN p.start_date AND end_date
			""", {"pris": flt(self.amount), "employee": self.employee, "to_date": self.to_date } 
		)

	def on_cancel(self):
		frappe.db.sql(
			"""
			UPDATE `tabProvision Ratio` r INNER JOIN  tabProvision p ON p.name = r.parent
			SET r.pris = r.pris - %(pris)s, r.total = r.total + %(pris)s
			WHERE r.employee = %(employee)s AND %(to_date)s BETWEEN p.start_date AND end_date
			""", {"pris": int(self.total_leave_days), "employee": self.employee, "to_date": self.to_date } 
		)
		#calculer le valeur des congés à prendre à afficher sur leaves application
		frappe.db.sql(
			"""
			UPDATE `tabProvision Conge` r INNER JOIN  tabProvision p ON p.name = r.parent
			SET r.pris =r.pris - %(pris)s, r.total = r.total + %(pris)s
			WHERE r.employee = %(employee)s AND %(to_date)s BETWEEN p.start_date AND end_date
			""", {"pris": flt(self.amount), "employee": self.employee, "to_date": self.to_date } 
		)
