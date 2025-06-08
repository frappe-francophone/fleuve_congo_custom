from hrms.payroll.doctype.salary_slip.salary_slip import SalarySlip
import frappe
from frappe.utils import getdate, flt

class CustomSalarySlip(SalarySlip):
	def on_submit(self):
		if getdate(self.end_date).month == 12 :
			bonus_in_separate_slip = frappe.db.get_single_value('Custom Paie Settings', 'bonus_in_separate_slip')
            if bonus_in_separate_slip == 1:
				gratif = frappe.db.get_list(doctype="Salary Structure Assignment", fields=["salary_type", "salary_structure"], 
                        filters={"eventual": 1, "employee": self.employee, "docstatus": 1, 'event_name': 'Prime annuelle'})
				if gratif[0].salary_structure == self.salary_structure :
					frappe.db.sql(
						"""
						UPDATE `tabProvision Gratification` r INNER JOIN  tabProvision p ON p.name = r.parent
						SET r.pris =r.total, r.total = 0
						WHERE r.employee = %(employee)s AND %(to_date)s BETWEEN p.start_date AND end_date
						""", {"employee": self.employee, "to_date": self.end_date } 
					)
			else:
				frappe.db.sql(
					"""
					UPDATE `tabProvision Gratification` r INNER JOIN  tabProvision p ON p.name = r.parent
					SET r.pris =r.total, r.total = 0
					WHERE r.employee = %(employee)s AND %(to_date)s BETWEEN p.start_date AND end_date
					""", {"employee": self.employee, "to_date": self.end_date } 
				)

	def on_cancel(self):
		if getdate(self.end_date).month == 12 :
			frappe.db.sql(
				"""
				UPDATE `tabProvision Gratification` r INNER JOIN  tabProvision p ON p.name = r.parent
				SET r.pris =0, r.total = r.report + r.janvier + r.fevrier + r.mars + r.avril + r.mai + r.juin + r.juillet + r.aout + r.septembre + r.octobre + r.novembre + r.decembre
				WHERE r.employee = %(employee)s AND %(to_date)s BETWEEN p.start_date AND end_date
				""", {"employee": self.employee, "to_date": self.end_date } 
			)