# Copyright (c) 2024, Kossivi Amouzou and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import json
import requests
from datetime import datetime
import pytz


class Provision(Document):
	def second_calandar_query(self, employee_name):
		return frappe.db.sql(
			"""
			SELECT y.*,
			y.salaire01 / y.ratio_total * y.ratio01 AS `gratif01`,
			y.salaire02 / y.ratio_total * y.ratio02 AS `gratif02`,
			y.salaire03 / y.ratio_total * y.ratio03 AS `gratif03`,
			y.salaire04 / y.ratio_total * y.ratio04 AS `gratif04`,
			y.salaire05 / y.ratio_total * y.ratio05 AS `gratif05`,
			y.salaire06 / y.ratio_total * y.ratio06 AS `gratif06`,
			y.salaire07 / y.ratio_total * y.ratio07 AS `gratif07`,
			y.salaire08 / y.ratio_total * y.ratio08 AS `gratif08`,
			y.salaire09 / y.ratio_total * y.ratio09 AS `gratif09`,
			y.salaire10 / y.ratio_total * y.ratio10 AS `gratif10`,
			y.salaire11 / y.ratio_total * y.ratio11 AS `gratif11`,
			y.salaire12 / y.ratio_total * y.ratio12 AS `gratif12`,

			y.salaire01 / 26 * y.ratio01 AS `salmois01`,
			y.salaire02 / 26 * y.ratio02 AS `salmois02`,
			y.salaire03 / 26 * y.ratio03 AS `salmois03`,
			y.salaire04 / 26 * y.ratio04 AS `salmois04`,
			y.salaire05 / 26 * y.ratio05 AS `salmois05`,
			y.salaire06 / 26 * y.ratio06 AS `salmois06`,
			y.salaire07 / 26 * y.ratio07 AS `salmois07`,
			y.salaire08 / 26 * y.ratio08 AS `salmois08`,
			y.salaire09 / 26 * y.ratio09 AS `salmois09`,
			y.salaire10 / 26 * y.ratio10 AS `salmois10`,
			y.salaire11 / 26 * y.ratio11 AS `salmois11`,
			y.salaire12 / 26 * y.ratio12 AS `salmois12`
			FROM
				(SELECT w.*,  
				ratio01 + ratio02 + ratio03 + ratio04 + ratio05 + ratio06 + ratio07 + ratio08 + ratio09 + ratio10 + ratio11 + ratio12 AS ratio_total
				FROM(
					SELECT v.employee,
					SUM(CASE WHEN v.mois = 1 THEN new_rate ELSE 0 END) AS `ratio01`,
					SUM(CASE WHEN v.mois = 2 THEN new_rate ELSE 0 END) AS `ratio02`,
					SUM(CASE WHEN v.mois = 3 THEN new_rate ELSE 0 END) AS `ratio03`,
					SUM(CASE WHEN v.mois = 4 THEN new_rate ELSE 0 END) AS `ratio04`,
					SUM(CASE WHEN v.mois = 5 THEN new_rate ELSE 0 END) AS `ratio05`,
					SUM(CASE WHEN v.mois = 6 THEN new_rate ELSE 0 END) AS `ratio06`,
					SUM(CASE WHEN v.mois = 7 THEN new_rate ELSE 0 END) AS `ratio07`,
					SUM(CASE WHEN v.mois = 8 THEN new_rate ELSE 0 END) AS `ratio08`,
					SUM(CASE WHEN v.mois = 9 THEN new_rate ELSE 0 END) AS `ratio09`,
					SUM(CASE WHEN v.mois = 10 THEN new_rate ELSE 0 END) AS `ratio10`,
					SUM(CASE WHEN v.mois = 11 THEN new_rate ELSE 0 END) AS `ratio11`,
					SUM(CASE WHEN v.mois = 12 THEN new_rate ELSE 0 END) AS `ratio12`,
					
					SUM(CASE WHEN v.mois = 1 THEN salaire ELSE 0 END) AS `salaire01`,
					SUM(CASE WHEN v.mois = 2 THEN salaire ELSE 0 END) AS `salaire02`,
					SUM(CASE WHEN v.mois = 3 THEN salaire ELSE 0 END) AS `salaire03`,
					SUM(CASE WHEN v.mois = 4 THEN salaire ELSE 0 END) AS `salaire04`,
					SUM(CASE WHEN v.mois = 5 THEN salaire ELSE 0 END) AS `salaire05`,
					SUM(CASE WHEN v.mois = 6 THEN salaire ELSE 0 END) AS `salaire06`,
					SUM(CASE WHEN v.mois = 7 THEN salaire ELSE 0 END) AS `salaire07`,
					SUM(CASE WHEN v.mois = 8 THEN salaire ELSE 0 END) AS `salaire08`,
					SUM(CASE WHEN v.mois = 9 THEN salaire ELSE 0 END) AS `salaire09`,
					SUM(CASE WHEN v.mois = 10 THEN salaire ELSE 0 END) AS `salaire10`,
					SUM(CASE WHEN v.mois = 11 THEN salaire ELSE 0 END) AS `salaire11`,
					SUM(CASE WHEN v.mois = 12 THEN salaire ELSE 0 END) AS `salaire12`
					
					FROM
						(SELECT t.annee, t.mois, t.date_begin, t.date_end, t.date_join, t.date_debut, t.date_fin, t.date_quit, t.employee,
											(t.start_period_day / t.period_day * t.rate) + t.years_div_5 AS new_rate, 
											t.period_day, t.rate, t.salaire, t.start_period_day, t.years_difference, t.years_div_5, t.categorie
										FROM (
											SELECT 
												e.name as employee, 
												YEAR(p.end_date) AS annee, 
												MONTH(p.end_date) AS mois,
												CASE 
													WHEN p.end_date >= e.date_of_joining THEN  
														CASE 
															WHEN e.relieving_date IS NULL THEN 1.5
															WHEN e.relieving_date > p.start_date THEN 1.5 
															ELSE 0 
														END
													ELSE 0 
												END AS rate,
												DATEDIFF(p.end_date, p.start_date) AS period_day,
												CASE 
													WHEN STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(e.date_of_joining), '-', DAY(e.date_of_joining)), '%%Y-%%m-%%d') BETWEEN p.start_date AND p.end_date THEN
														CASE 
															WHEN YEAR(p.end_date) = YEAR(e.date_of_joining) THEN
																DATEDIFF(p.end_date, STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(e.date_of_joining), '-', DAY(e.date_of_joining)), '%%Y-%%m-%%d')) + 1 
															ELSE
																DATEDIFF(p.end_date, p.start_date)
														END
													ELSE 
														DATEDIFF(p.end_date, p.start_date)
												END AS start_period_day,
												e.relieving_date AS date_quit,
												p.end_date AS date_end, 
												p.start_date AS date_begin, 
												e.date_of_joining AS date_join,
												TIMESTAMPDIFF(YEAR, e.date_of_joining, p.end_date) AS years_difference,
												CASE 
													WHEN STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', CASE WHEN MONTH(e.date_of_joining) = 12 THEN 1 ELSE MONTH(e.date_of_joining) + 1 END, '-', DAY(e.date_of_joining)), '%%Y-%%m-%%d') BETWEEN p.start_date AND p.end_date
														AND (e.relieving_date > p.start_date OR e.relieving_date IS NULL) THEN
														TIMESTAMPDIFF(YEAR, e.date_of_joining, p.end_date) DIV 5 
													ELSE 0
												END AS years_div_5,
												se.categorie, se.date_debut, se.salaire, IFNULL(se.date_fin, DATE_FORMAT(NOW(),'%%Y-12-31'))  AS date_fin
											FROM 
												tabEmployee e 
												CROSS JOIN `tabPayroll Period` p INNER JOIN `tabSalaire employee` se ON e.name = se.parent 
											WHERE 
												YEAR(p.end_date) = %(fiscal_year)s AND e.employment_type = %(type)s AND e.employee LIKE %(employee_name)s
										) AS t  
										WHERE t.date_begin BETWEEN t.date_debut AND t.date_fin 
						) v
						GROUP BY v.employee) AS w) AS y 
			""", {"fiscal_year":int(self.fiscal_year), "type": self.employment_type, "employee_name": employee_name}, as_dict=1
		)

	def first_calandar_query(self, employee_name):
		return frappe.db.sql(
			"""
			SELECT y.*,
			y.salaire01 / y.ratio_total * y.ratio01 AS `gratif01`,
			y.salaire02 / y.ratio_total * y.ratio02 AS `gratif02`,
			y.salaire03 / y.ratio_total * y.ratio03 AS `gratif03`,
			y.salaire04 / y.ratio_total * y.ratio04 AS `gratif04`,
			y.salaire05 / y.ratio_total * y.ratio05 AS `gratif05`,
			y.salaire06 / y.ratio_total * y.ratio06 AS `gratif06`,
			y.salaire07 / y.ratio_total * y.ratio07 AS `gratif07`,
			y.salaire08 / y.ratio_total * y.ratio08 AS `gratif08`,
			y.salaire09 / y.ratio_total * y.ratio09 AS `gratif09`,
			y.salaire10 / y.ratio_total * y.ratio10 AS `gratif10`,
			y.salaire11 / y.ratio_total * y.ratio11 AS `gratif11`,
			y.salaire12 / y.ratio_total * y.ratio12 AS `gratif12`,

			y.salaire01 / 26 * y.ratio01 AS `salmois01`,
			y.salaire02 / 26 * y.ratio02 AS `salmois02`,
			y.salaire03 / 26 * y.ratio03 AS `salmois03`,
			y.salaire04 / 26 * y.ratio04 AS `salmois04`,
			y.salaire05 / 26 * y.ratio05 AS `salmois05`,
			y.salaire06 / 26 * y.ratio06 AS `salmois06`,
			y.salaire07 / 26 * y.ratio07 AS `salmois07`,
			y.salaire08 / 26 * y.ratio08 AS `salmois08`,
			y.salaire09 / 26 * y.ratio09 AS `salmois09`,
			y.salaire10 / 26 * y.ratio10 AS `salmois10`,
			y.salaire11 / 26 * y.ratio11 AS `salmois11`,
			y.salaire12 / 26 * y.ratio12 AS `salmois12`,

			y.salaire01 / 26 * y.period_day01 AS `bonus01`,
			y.salaire02 / 26 * y.period_day02 AS `bonus02`,
			y.salaire03 / 26 * y.period_day03 AS `bonus03`,
			y.salaire04 / 26 * y.period_day04 AS `bonus04`,
			y.salaire05 / 26 * y.period_day05 AS `bonus05`,
			y.salaire06 / 26 * y.period_day06 AS `bonus06`,
			y.salaire07 / 26 * y.period_day07 AS `bonus07`,
			y.salaire08 / 26 * y.period_day08 AS `bonus08`,
			y.salaire09 / 26 * y.period_day09 AS `bonus09`,
			y.salaire10 / 26 * y.period_day10 AS `bonus10`,
			y.salaire11 / 26 * y.period_day11 AS `bonus11`,
			y.salaire12 / 26 * y.period_day12 AS `bonus12`,

			y.air_ticket AS `air_ticket01`,
			y.air_ticket AS `air_ticket02`,
			y.air_ticket AS `air_ticket03`,
			y.air_ticket AS `air_ticket04`,
			y.air_ticket AS `air_ticket05`,
			y.air_ticket AS `air_ticket06`,
			y.air_ticket AS `air_ticket07`,
			y.air_ticket AS `air_ticket08`,
			y.air_ticket AS `air_ticket09`,
			y.air_ticket AS `air_ticket10`,
			y.air_ticket AS `air_ticket11`,
			y.air_ticket AS `air_ticket12`
			FROM
				(SELECT w.*,  
				ratio01 + ratio02 + ratio03 + ratio04 + ratio05 + ratio06 + ratio07 + ratio08 + ratio09 + ratio10 + ratio11 + ratio12 AS ratio_total
				FROM(
					SELECT v.employee, v.air_ticket,
					SUM(CASE WHEN v.mois = 1 THEN new_rate ELSE 0 END) AS `ratio01`,
					SUM(CASE WHEN v.mois = 2 THEN new_rate ELSE 0 END) AS `ratio02`,
					SUM(CASE WHEN v.mois = 3 THEN new_rate ELSE 0 END) AS `ratio03`,
					SUM(CASE WHEN v.mois = 4 THEN new_rate ELSE 0 END) AS `ratio04`,
					SUM(CASE WHEN v.mois = 5 THEN new_rate ELSE 0 END) AS `ratio05`,
					SUM(CASE WHEN v.mois = 6 THEN new_rate ELSE 0 END) AS `ratio06`,
					SUM(CASE WHEN v.mois = 7 THEN new_rate ELSE 0 END) AS `ratio07`,
					SUM(CASE WHEN v.mois = 8 THEN new_rate ELSE 0 END) AS `ratio08`,
					SUM(CASE WHEN v.mois = 9 THEN new_rate ELSE 0 END) AS `ratio09`,
					SUM(CASE WHEN v.mois = 10 THEN new_rate ELSE 0 END) AS `ratio10`,
					SUM(CASE WHEN v.mois = 11 THEN new_rate ELSE 0 END) AS `ratio11`,
					SUM(CASE WHEN v.mois = 12 THEN new_rate ELSE 0 END) AS `ratio12`,
					
					SUM(CASE WHEN v.mois = 1 THEN salaire ELSE 0 END) AS `salaire01`,
					SUM(CASE WHEN v.mois = 2 THEN salaire ELSE 0 END) AS `salaire02`,
					SUM(CASE WHEN v.mois = 3 THEN salaire ELSE 0 END) AS `salaire03`,
					SUM(CASE WHEN v.mois = 4 THEN salaire ELSE 0 END) AS `salaire04`,
					SUM(CASE WHEN v.mois = 5 THEN salaire ELSE 0 END) AS `salaire05`,
					SUM(CASE WHEN v.mois = 6 THEN salaire ELSE 0 END) AS `salaire06`,
					SUM(CASE WHEN v.mois = 7 THEN salaire ELSE 0 END) AS `salaire07`,
					SUM(CASE WHEN v.mois = 8 THEN salaire ELSE 0 END) AS `salaire08`,
					SUM(CASE WHEN v.mois = 9 THEN salaire ELSE 0 END) AS `salaire09`,
					SUM(CASE WHEN v.mois = 10 THEN salaire ELSE 0 END) AS `salaire10`,
					SUM(CASE WHEN v.mois = 11 THEN salaire ELSE 0 END) AS `salaire11`,
					SUM(CASE WHEN v.mois = 12 THEN salaire ELSE 0 END) AS `salaire12`,

					MAX(CASE WHEN v.mois = 1 THEN v.period_day ELSE 0 END) AS `period_day01`,
					MAX(CASE WHEN v.mois = 2 THEN v.period_day ELSE 0 END) AS `period_day02`,
					MAX(CASE WHEN v.mois = 3 THEN v.period_day ELSE 0 END) AS `period_day03`,
					MAX(CASE WHEN v.mois = 4 THEN v.period_day ELSE 0 END) AS `period_day04`,
					MAX(CASE WHEN v.mois = 5 THEN v.period_day ELSE 0 END) AS `period_day05`,
					MAX(CASE WHEN v.mois = 6 THEN v.period_day ELSE 0 END) AS `period_day06`,
					MAX(CASE WHEN v.mois = 7 THEN v.period_day ELSE 0 END) AS `period_day07`,
					MAX(CASE WHEN v.mois = 8 THEN v.period_day ELSE 0 END) AS `period_day08`,
					MAX(CASE WHEN v.mois = 9 THEN v.period_day ELSE 0 END) AS `period_day09`,
					MAX(CASE WHEN v.mois = 10 THEN v.period_day ELSE 0 END) AS `period_day10`,
					MAX(CASE WHEN v.mois = 11 THEN v.period_day ELSE 0 END) AS `period_day11`,
					MAX(CASE WHEN v.mois = 12 THEN v.period_day ELSE 0 END) AS `period_day12`,

					MAX(CASE WHEN v.mois = 1 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode01`,
					MAX(CASE WHEN v.mois = 2 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode02`,
					MAX(CASE WHEN v.mois = 3 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode03`,
					MAX(CASE WHEN v.mois = 4 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode04`,
					MAX(CASE WHEN v.mois = 5 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode05`,
					MAX(CASE WHEN v.mois = 6 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode06`,
					MAX(CASE WHEN v.mois = 7 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode07`,
					MAX(CASE WHEN v.mois = 8 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode08`,
					MAX(CASE WHEN v.mois = 9 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode09`,
					MAX(CASE WHEN v.mois = 10 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode10`,
					MAX(CASE WHEN v.mois = 11 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode11`,
					MAX(CASE WHEN v.mois = 12 THEN v.ratio_periode ELSE 0 END) AS `ratio_periode12`
					FROM
						(SELECT t.annee, t.mois, t.date_begin, t.date_end, t.date_join, t.date_debut, t.date_fin, t.date_quit, t.employee, t.air_ticket,
											(t.start_period_day / t.period_day * t.rate) + t.years_div_5 AS new_rate, t.start_period_day / t.period_day AS ratio_periode,
											t.period_day, t.rate, t.salaire, t.start_period_day, t.years_difference, t.years_div_5, t.categorie
										FROM (
											SELECT 
											e.name as employee, 
											e.air_ticket / 12 AS air_ticket,
											YEAR(p.end_date) AS annee, 
											MONTH(p.end_date) AS mois,
											CASE 
												WHEN p.end_date >= e.date_of_joining THEN  
													CASE 
														WHEN e.relieving_date IS NULL THEN 2.5
														WHEN e.relieving_date > STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(p.end_date), '-', 1), '%%Y-%%m-%%d') THEN 2.5 
														ELSE 0 
													END
												ELSE 0 
											END AS rate,
											DATEDIFF(LAST_DAY(p.end_date), STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(p.end_date), '-', 1), '%%Y-%%m-%%d')) + 1 AS period_day,
											CASE 
												WHEN STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(e.date_of_joining), '-', DAY(e.date_of_joining)), '%%Y-%%m-%%d') BETWEEN STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(p.end_date), '-', 1), '%%Y-%%m-%%d') AND LAST_DAY(p.end_date) THEN
													CASE 
														WHEN YEAR(p.end_date) = YEAR(e.date_of_joining) THEN
															DATEDIFF(LAST_DAY(p.end_date), STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(e.date_of_joining), '-', DAY(e.date_of_joining)), '%%Y-%%m-%%d')) 
														ELSE
															DATEDIFF(LAST_DAY(p.end_date), STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(p.end_date), '-', 1), '%%Y-%%m-%%d'))
													END
												ELSE 
													DATEDIFF(LAST_DAY(p.end_date), STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(p.end_date), '-', 1), '%%Y-%%m-%%d'))
											END + 1 AS start_period_day,
											e.relieving_date AS date_quit,
											LAST_DAY(p.end_date) AS date_end, 
											STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(p.end_date), '-', 1), '%%Y-%%m-%%d') AS date_begin, 
											e.date_of_joining AS date_join,
											TIMESTAMPDIFF(YEAR, e.date_of_joining, p.end_date) AS years_difference,
											CASE 
													WHEN STR_TO_DATE(CONCAT(YEAR(p.end_date), '-', MONTH(e.date_of_joining), '-', DAY(e.date_of_joining)), '%%Y-%%m-%%d') BETWEEN p.start_date AND p.end_date
														AND (e.relieving_date > p.start_date OR e.relieving_date IS NULL) THEN
														(TIMESTAMPDIFF(MONTH, e.date_of_joining, STR_TO_DATE(CONCAT(YEAR(p.end_date), '-12-31'), '%%Y-%%m-%%d')) / 12) DIV 5
													ELSE 0
												END AS years_div_5,
											se.categorie, se.date_debut, se.salaire, IFNULL(se.date_fin, DATE_FORMAT(NOW(),'%%Y-12-31'))  AS date_fin
											FROM 
											tabEmployee e 
											    CROSS JOIN `tabPayroll Period` p 
											    INNER JOIN `tabSalaire employee` se ON e.name = se.parent 
											WHERE 
												YEAR(p.end_date) = %(fiscal_year)s AND e.employment_type = %(type)s AND e.employee LIKE %(employee_name)s
										) AS t  
										WHERE t.date_begin BETWEEN t.date_debut AND t.date_fin 
						) v
						GROUP BY v.employee, v.air_ticket) AS w) AS y
			""", {"fiscal_year":int(self.fiscal_year), "type": self.employment_type, "employee_name": employee_name}, as_dict=1
		)

	def get_provision_ratio(self, employee, table, year):
		return frappe.db.sql(
			"""
			SELECT r.*
			FROM tabProvision p INNER JOIN {tbl} r ON p.name = r.parent
			WHERE r.employee = %(employee)s AND YEAR(p.end_date) = %(fiscal_year)s
			""".format( tbl=table ), 
			{"fiscal_year":int(year), "employee": employee}, as_dict=1
		)


	def get_provision_details(self, emp_name = None):
		employee_name = emp_name if emp_name else "%"
		return self.second_calandar_query(employee_name) if self.scondary_calendar == 1 else self.first_calandar_query(employee_name)

	@frappe.whitelist()
	def add_details(self):
		self.ratio.clear()
		self.conge.clear()
		self.gratification.clear()

		liste = self.get_provision_details()

		for i in liste:
			exist = self.get_provision_ratio(i.employee, '`tabProvision Ratio`', int(self.fiscal_year))
			if not exist:
				ly_total_ratio = 0
				ly_total_conge = 0
				ly_total_gratif = 0
				ly_total_ticket = 0
				ly_total_bonus = 0

				details = self.get_provision_ratio(i.employee, '`tabProvision Ratio`', int(self.fiscal_year) - 1)
				if details:
					if details[0]:
						ly_total_ratio = details[0].total if details[0].total else 0

				details = self.get_provision_ratio(i.employee, '`tabProvision Conge`', int(self.fiscal_year) - 1)
				if details:
					if details[0]:
						ly_total_conge = details[0].total if details[0].total else 0

				details = self.get_provision_ratio(i.employee, '`tabProvision Gratification`', int(self.fiscal_year) - 1)
				if details:
					if details[0]:
						ly_total_gratif = details[0].total if details[0].total else 0

				details = self.get_provision_ratio(i.employee, '`tabProvision Ticket`', int(self.fiscal_year) - 1)
				if details:
					if details[0]:
						ly_total_ticket = details[0].total if details[0].total else 0

				details = self.get_provision_ratio(i.employee, '`tabProvision Bonus`', int(self.fiscal_year) - 1)
				if details:
					if details[0]:
						ly_total_bonus = details[0].total if details[0].total else 0

				self.append(
						"ratio",
						{
							"employee": i.employee,
							"report": ly_total_ratio,
							"janvier": i.ratio01,
							"fevrier": i.ratio02,
							"mars": i.ratio03,
							"avril": i.ratio04,
							"mai": i.ratio05,
							"juin": i.ratio06,
							"juillet": i.ratio07,
							"aout": i.ratio08,
							"septembre": i.ratio09,
							"octobre": i.ratio10,
							"novembre": i.ratio11,
							"decembre": i.ratio12,
							"total": i.ratio_total + ly_total_ratio,
						}
					)

				self.append(
						"conge",
						{
							"employee": i.employee,
							"report": ly_total_conge,
							"janvier": i.salmois01,
							"fevrier": i.salmois02,
							"mars": i.salmois03,
							"avril": i.salmois04,
							"mai": i.salmois05,
							"juin": i.salmois06,
							"juillet": i.salmois07,
							"aout": i.salmois08,
							"septembre": i.salmois09,
							"octobre": i.salmois10,
							"novembre": i.salmois11,
							"decembre": i.salmois12,
							"total": ly_total_conge + i.salmois01 + i.salmois02 + i.salmois03 + i.salmois04 + i.salmois05 + i.salmois06 + i.salmois07 + i.salmois08 + i.salmois09 + i.salmois10 + i.salmois11 + i.salmois12
						}
					)

				self.append(
						"gratification",
						{
							"employee": i.employee,
							"report": ly_total_gratif,
							"janvier": i.gratif01,
							"fevrier": i.gratif02,
							"mars": i.gratif03,
							"avril": i.gratif04,
							"mai": i.gratif05,
							"juin": i.gratif06,
							"juillet": i.gratif07,
							"aout": i.gratif08,
							"septembre": i.gratif09,
							"octobre": i.gratif10,
							"novembre": i.gratif11,
							"decembre": i.gratif12,
							"total": ly_total_gratif + i.gratif01 + i.gratif02 + i.gratif03 + i.gratif04 + i.gratif05 + i.gratif06 + i.gratif07 + i.gratif08 + i.gratif09 + i.gratif10 + i.gratif11 + i.gratif12 
						}
					)

				if i.bonus01:
					self.append(
						"ticket",
						{
							"employee": i.employee,
							"report": ly_total_ticket,
							"janvier": i.air_ticket01,
							"fevrier": i.air_ticket02,
							"mars": i.air_ticket03,
							"avril": i.air_ticket04,
							"mai": i.air_ticket05,
							"juin": i.air_ticket06,
							"juillet": i.air_ticket07,
							"aout": i.air_ticket08,
							"septembre": i.air_ticket09,
							"octobre": i.air_ticket10,
							"novembre": i.air_ticket11,
							"decembre": i.air_ticket12,
							"total": ly_total_ticket + i.air_ticket01 + i.air_ticket02 + i.air_ticket03 + i.air_ticket04 + i.air_ticket05 + i.air_ticket06 + i.air_ticket07 + i.air_ticket08 + i.air_ticket09 + i.air_ticket10 + i.air_ticket11 + i.air_ticket12 
						}
					)

					self.append(
						"bonus",
						{
							"employee": i.employee,
							"report": ly_total_bonus,
							"janvier": i.bonus01,
							"fevrier": i.bonus02,
							"mars": i.bonus03,
							"avril": i.bonus04,
							"mai": i.bonus05,
							"juin": i.bonus06,
							"juillet": i.bonus07,
							"aout": i.bonus08,
							"septembre": i.bonus09,
							"octobre": i.bonus10,
							"novembre": i.bonus11,
							"decembre": i.bonus12,
							"total": ly_total_bonus + i.bonus01 + i.bonus02 + i.bonus03 + i.bonus04 + i.bonus05 + i.bonus06 + i.bonus07 + i.bonus08 + i.bonus09 + i.bonus10 + i.bonus11 + i.bonus12 
						}
					)

	def before_save(self):
		self.add_details()

	def on_submit(self):
		for i in self.ratio:
			doc = frappe.new_doc("Leave Allocation")
			doc.leave_type = self.leave_type
			doc.employee = i.employee
			doc.new_leaves_allocated = i.total
			doc.from_date = self.start_date
			doc.to_date = self.end_date
			doc.submit()

@frappe.whitelist()
def update_provision_details(fiscal_year, emp_name):
	liste = frappe.db.get_list("Provision", {"fiscal_year": int(fiscal_year)}, ["*"])
	for i in liste:
		ratio_list =frappe.db.sql(
				"""
				SELECT * 
				FROM `tabProvision Ratio`
				WHERE employee = %s AND parent = %s
				""", (emp_name, i.name), as_dict=1
			)
		if len(ratio_list) > 0 :
			doc = frappe.get_doc("Provision", i.name)
			details = doc.get_provision_details(emp_name)
			if details[0]:
				d  = details[0]
				#ratio_doc = frappe.get_doc("Provision Ratio", {"employee": emp_name, "parent": doc.name})
				frappe.db.set_value('Provision Ratio', ratio_list[0].name, 	{
					"janvier": d.ratio01,
					"fevrier": d.ratio02,
					"mars": d.ratio03,
					"avril": d.ratio04,
					"mai": d.ratio05,
					"juin": d.ratio06,
					"juillet": d.ratio07,
					"aout": d.ratio08,
					"septembre": d.ratio09,
					"octobre": d.ratio10,
					"novembre": d.ratio11,
					"decembre": d.ratio12,
					"total": ratio_list[0].report + d.ratio01 + d.ratio02 + d.ratio03 + d.ratio04 + d.ratio05 + d.ratio06 + 
					d.ratio07 + d.ratio08 + d.ratio09 + d.ratio10 + d.ratio11 + d.ratio12 - ratio_list[0].pris,
				})

				conge_list =frappe.db.sql(
					"""
					SELECT * 
					FROM `tabProvision Conge`
					WHERE employee = %s AND parent = %s
					""", (emp_name, i.name), as_dict=1
				)
				#conge_doc = frappe.get_doc("Provision Conge", {"employee": emp_name, "parent": doc.name})
				frappe.db.set_value('Provision Conge', conge_list[0].name, 	{
					"janvier": d.salmois01,
					"fevrier": d.salmois02,
					"mars": d.salmois03,
					"avril": d.salmois04,
					"mai": d.salmois05,
					"juin": d.salmois06,
					"juillet": d.salmois07,
					"aout": d.salmois08,
					"septembre": d.salmois09,
					"octobre": d.salmois10,
					"novembre": d.salmois11,
					"decembre": d.salmois12,
					"total": conge_list[0].report + d.salmois01 + d.salmois02 + d.salmois03 + d.salmois04 + d.salmois05 + d.salmois06 + 
					d.salmois07 + d.salmois08 + d.salmois09 + d.salmois10 + d.salmois11 + d.salmois12 - conge_list[0].pris,
				})

				gratif_list =frappe.db.sql(
					"""
					SELECT * 
					FROM `tabProvision Gratification`
					WHERE employee = %s AND parent = %s
					""", (emp_name, i.name), as_dict=1
				)
				#gratif_doc = frappe.get_doc("Provision Gratification", {"employee": emp_name, "parent": doc.name})
				frappe.db.set_value('Provision Gratification', gratif_list[0].name, 	{
					"janvier": d.gratif01,
					"fevrier": d.gratif02,
					"mars": d.gratif03,
					"avril": d.gratif04,
					"mai": d.gratif05,
					"juin": d.gratif06,
					"juillet": d.gratif07,
					"aout": d.gratif08,
					"septembre": d.gratif09,
					"octobre": d.gratif10,
					"novembre": d.gratif11,
					"decembre": d.gratif12,
					"total": gratif_list[0].report + d.gratif01 + d.gratif02 + d.gratif03 + d.gratif04 + d.gratif05 + d.gratif06 + 
					d.gratif07 + d.gratif08 + d.gratif09 + d.gratif10 + d.gratif11 + d.gratif12 - gratif_list[0].pris,
				})

				if d.bonus01:
					#frappe.db.set_value('Provision Ticket', gratif_list[0].name, 	{
					#		"employee": d.employee,
					#		"report": gratif_list[0].report,
					#		"janvier": d.air_ticket01,
					#		"fevrier": d.air_ticket02,
					#		"mars": d.air_ticket03,
					#		"avril": d.air_ticket04,
					#		"mai": d.air_ticket05,
					#		"juin": d.air_ticket06,
					#		"juillet": d.air_ticket07,
					#		"aout": d.air_ticket08,
					#		"septembre": d.air_ticket09,
					#		"octobre": d.air_ticket10,
					#		"novembre": d.air_ticket11,
					#		"decembre": d.air_ticket12,
					#		"total": gratif_list[0].report + d.air_ticket01 + d.air_ticket02 + d.air_ticket03 + d.air_ticket04 + d.air_ticket05 + 
					#		d.air_ticket06 + d.air_ticket07 + d.air_ticket08 + d.air_ticket09 + d.air_ticket10 + d.air_ticket11 + d.air_ticket12 
					#	}
					#)

					gratif_list =frappe.db.sql(
						"""
						SELECT * 
						FROM `tabProvision Ticket`
						WHERE employee = %s AND parent = %s
						""", (emp_name, i.name), as_dict=1
					)

					frappe.db.set_value('Provision Ticket', gratif_list[0].name, 	{
							"employee": d.employee,
							"report": gratif_list[0].report,
							"janvier": d.bonus01,
							"fevrier": d.bonus02,
							"mars": d.bonus03,
							"avril": d.bonus04,
							"mai": d.bonus05,
							"juin": d.bonus06,
							"juillet": d.bonus07,
							"aout": d.bonus08,
							"septembre": d.bonus09,
							"octobre": d.bonus10,
							"novembre": d.bonus11,
							"decembre": d.bonus12,
							"total": gratif_list[0].report + d.bonus01 + d.bonus02 + d.bonus03 + d.bonus04 + d.bonus05 + d.bonus06 + 
							d.bonus07 + d.bonus08 + d.bonus09 + d.bonus10 + d.bonus11 + d.bonus12 
						}
					)

				frappe.db.commit()

				return emp_name
	
@frappe.whitelist()		
def update_attendance_all():

	url_base = "http://10.184.104.230:8080/iclock/api/transactions/"
	token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyNjE5ODU5LCJpYXQiOjE3MzI1MzM0NTksImp0aSI6IjMwNzk3NmY0MTQwMzRjYTk4Nzg1MjE4Y2Y2NWFhNWQ0IiwidXNlcl9pZCI6MX0.msx3MwlnejASvx-t8hEzH6le3jOMNcbMUQn2ZSFwIeg"
	page = 1
	limit = 1000
	all_data = []  # This will store the combined data
  
    # Get today's date
	date_time_string = frappe.utils.now()
  
    # Use correct date format
    #datejour_end = '2024-11-30'

	datejour_start = frappe.utils.add_days(date_time_string, -25)
	date_end = frappe.utils.add_days(date_time_string, 2)
  
	datejour_end = frappe.utils.formatdate(date_end, 'yyyy-mm-dd')
	datejour_start = frappe.utils.formatdate(datejour_start, 'yyyy-mm-dd')

	username = "admin"
	password = "admin@123"
    
	headers = {
        "Authorization": f"JWT {token}",
        "Content-Type": "application/json"
    }
    #AND EC.employee = '04039'
    # SQL query to get active employee
	sql_query = """
        SELECT EC.date_of_joining, EC.employee AS Matricule, EC.status 
        FROM `tabEmployee` EC
        WHERE EC.status = 'Active'
    """
	employee_checkin = frappe.db.sql(sql_query,as_dict=True)

	for list in employee_checkin:
            # Get today's date
		date_time_string = frappe.utils.now()

		datejour_start = frappe.utils.add_days(date_time_string, -25)
		date_end = frappe.utils.add_days(date_time_string, 2)
    
		datejour_end = frappe.utils.formatdate(date_end, 'yyyy-mm-dd')
		datejour_start = frappe.utils.formatdate(datejour_start, 'yyyy-mm-dd')
        
		print(f"Page récupérée START ---{datejour_start}----------------END DATE------{datejour_end}--------------------------------------: {list.Matricule}")
		page = 1
		all_data = []
		records = []
		data = ''
		try:
            # Loop to paginate the API request
			while True:
                #print(f"VISON FIRST +++++++++++++++++++++===================+++++++++++--: {list.Matricule}")
				params = {
                    "start_time" : f'{datejour_start} 00:00:00',
                    "end_time" : f'{datejour_end} 00:00:00',  # Ensuring we cover the full day
                    "limit": limit,
                    "emp_code" : list.Matricule,
                    "page": page
                }
				url = (
                    f"{url_base}?emp_code={list['Matricule']}"
                    f"&start_time={datejour_start} 00:00:00"
                    f"&end_time={datejour_end} 00:00:00"
                    f"&limit={limit}"
                    f"&page={page}"
                )
            
                #print(f"Fetching data from URL: {url}")
				response = requests.get(url, auth=(username, password), headers=headers)
                
                #response = requests.get(url, params=params, auth=(username, password), headers=headers)

				if response.status_code == 200:
					data = response.json()
                    
					if not isinstance(data, dict) or "data" not in data:
						print("Le format de réponse est incorrect. Clé 'data' manquante.")
                    
					records = data["data"]
                    #print(f"Page +++++++++++++++++++++===================+++++++++++--: {list.Matricule}")
					if not records :
						print(f"NOT RECORD ######################----------------------#######################: {list.Matricule}")
					if page == 20:
						break
					
					all_data.extend(records)
					page += 1

            # Process all collected data
			for ligne in all_data:

				type_jour = ''
				emp_code = ligne.get('emp_code', 'N/A')
				punch_time = ligne.get('punch_time', 'N/A')
				first_name = ligne.get('first_name', 'N/A')
				terminal_sn = ligne.get('terminal_sn', 'N/A')

                #print(f"Terminal #################------------------------------- : {terminal_sn}")
                
				datejour_end_comp = frappe.utils.formatdate(list.date_of_joining, 'yyyy-mm-dd')
				datejour_start = frappe.utils.formatdate(punch_time, 'yyyy-mm-dd')
                                
				if datejour_end_comp > datejour_start :
					print(f"JOINNNING DATE ################# : {datejour_end_comp}")
				else :
					print(f"PUNCH TIME +++++++++###############-: {punch_time}")
                    
                    # Set type of punch (IN or OUT) based on terminal_sn
					if terminal_sn in ['CGT9221060018', 'BAY5240500035', 'BAY5240500077', 'BAY5240500078', 
                                    'BAY5240500099', 'CGT9221060020', 'CGT9221060023']:
						type_jour = "IN"
					else:
						type_jour = "OUT"

                    # SQL query to find existing attendance
					sql_query_find = """
                        SELECT *
                        FROM `tabEmployee Checkin` EC
                        WHERE EC.log_type = %s
                        AND EC.employee = %s
                        AND DATE(EC.time) = %s
                    """

					existing_attendance = frappe.db.sql(
                        sql_query_find, (type_jour, list.Matricule, frappe.utils.getdate(punch_time)),
                        as_dict=True
                    )

					if existing_attendance:
						print(f"EXISTANT Date punch_time ===> {punch_time} ||| emp_code == {emp_code} log_type == {type_jour}")
					else:
                        # Create a new attendance document
						attendance_list = frappe.new_doc('Employee Checkin')
						attendance_list.employee = list.Matricule
						attendance_list.employee_name = first_name
						attendance_list.time = punch_time
						attendance_list.log_type = type_jour
						attendance_list.device_id = terminal_sn

                        # Save the document
						attendance_list.insert(ignore_permissions=True)
						frappe.db.commit()

						message = f"Employee Code: {emp_code}, Name: {first_name} , Devices {terminal_sn}, Punch Time: {punch_time}"
						print(message)  
                
                
		except requests.exceptions.Timeout:
			frappe.throw("La requête a expiré (timeout). Vérifiez la disponibilité du serveur.")
		except requests.exceptions.ConnectionError as e:
			frappe.throw(f"Erreur de connexion : {str(e)}")
		except Exception as e:
			frappe.throw(f"Une erreur inattendue s'est produite : {str(e)}")

	
@frappe.whitelist()		
def update_attendance_individuel(employee):

	url_base = "http://10.184.104.230:8080/iclock/api/transactions/"
	token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyNjE5ODU5LCJpYXQiOjE3MzI1MzM0NTksImp0aSI6IjMwNzk3NmY0MTQwMzRjYTk4Nzg1MjE4Y2Y2NWFhNWQ0IiwidXNlcl9pZCI6MX0.msx3MwlnejASvx-t8hEzH6le3jOMNcbMUQn2ZSFwIeg"
	page = 1
	limit = 1000
	all_data = []  # This will store the combined data
	find_employee = employee
    # Get today's date
	date_time_string = frappe.utils.now()
  
    # Use correct date format
    #datejour_end = '2024-11-30'

	datejour_start = frappe.utils.add_days(date_time_string, -25)
	date_end = frappe.utils.add_days(date_time_string, 2)
  
	datejour_end = frappe.utils.formatdate(date_end, 'yyyy-mm-dd')
	datejour_start = frappe.utils.formatdate(datejour_start, 'yyyy-mm-dd')

	username = "admin"
	password = "admin@123"
    
	headers = {
        "Authorization": f"JWT {token}",
        "Content-Type": "application/json"
    }
    #AND EC.employee = '04039'
    # SQL query to get active employee
	sql_query = """
        SELECT EC.date_of_joining, EC.employee AS Matricule, EC.status 
        FROM `tabEmployee` EC
        WHERE EC.status = 'Active' AND EC.employee = %s
    """
	employee_checkin = frappe.db.sql(sql_query,(find_employee),as_dict=True)

	for list in employee_checkin:
            # Get today's date
		date_time_string = frappe.utils.now()

		datejour_start = frappe.utils.add_days(date_time_string, -25)
		date_end = frappe.utils.add_days(date_time_string, 2)
    
		datejour_end = frappe.utils.formatdate(date_end, 'yyyy-mm-dd')
		datejour_start = frappe.utils.formatdate(datejour_start, 'yyyy-mm-dd')
        
		print(f"Page récupérée START ---{datejour_start}----------------END DATE------{datejour_end}--------------------------------------: {list.Matricule}")
		page = 1
		all_data = []
		records = []
		data = ''
		try:
            # Loop to paginate the API request
			while True:
                #print(f"VISON FIRST +++++++++++++++++++++===================+++++++++++--: {list.Matricule}")
				params = {
                    "start_time" : f'{datejour_start} 00:00:00',
                    "end_time" : f'{datejour_end} 00:00:00',  # Ensuring we cover the full day
                    "limit": limit,
                    "emp_code" : list.Matricule,
                    "page": page
                }
				url = (
                    f"{url_base}?emp_code={list['Matricule']}"
                    f"&start_time={datejour_start} 00:00:00"
                    f"&end_time={datejour_end} 00:00:00"
                    f"&limit={limit}"
                    f"&page={page}"
                )
            
                #print(f"Fetching data from URL: {url}")
				response = requests.get(url, auth=(username, password), headers=headers)
                
                #response = requests.get(url, params=params, auth=(username, password), headers=headers)

				if response.status_code == 200:
					data = response.json()
                    
					if not isinstance(data, dict) or "data" not in data:
						print("Le format de réponse est incorrect. Clé 'data' manquante.")
                    
					records = data["data"]
                    #print(f"Page +++++++++++++++++++++===================+++++++++++--: {list.Matricule}")
					if not records :
						print(f"NOT RECORD ######################----------------------#######################: {list.Matricule}")
					if page == 20:
						break
					
					all_data.extend(records)
					page += 1

            # Process all collected data
			for ligne in all_data:

				type_jour = ''
				emp_code = ligne.get('emp_code', 'N/A')
				punch_time = ligne.get('punch_time', 'N/A')
				first_name = ligne.get('first_name', 'N/A')
				terminal_sn = ligne.get('terminal_sn', 'N/A')

                #print(f"Terminal #################------------------------------- : {terminal_sn}")
                
				datejour_end_comp = frappe.utils.formatdate(list.date_of_joining, 'yyyy-mm-dd')
				datejour_start = frappe.utils.formatdate(punch_time, 'yyyy-mm-dd')
                                
				if datejour_end_comp > datejour_start :
					print(f"JOINNNING DATE ################# : {datejour_end_comp}")
				else :
					print(f"PUNCH TIME +++++++++###############-: {punch_time}")
                    
                    # Set type of punch (IN or OUT) based on terminal_sn
					if terminal_sn in ['CGT9221060018', 'BAY5240500035', 'BAY5240500077', 'BAY5240500078', 
                                    'BAY5240500099', 'CGT9221060020', 'CGT9221060023']:
						type_jour = "IN"
					else:
						type_jour = "OUT"

                    # SQL query to find existing attendance
					sql_query_find = """
                        SELECT *
                        FROM `tabEmployee Checkin` EC
                        WHERE EC.log_type = %s
                        AND EC.employee = %s
                        AND DATE(EC.time) = %s
                    """

					existing_attendance = frappe.db.sql(
                        sql_query_find, (type_jour, list.Matricule, frappe.utils.getdate(punch_time)),
                        as_dict=True
                    )

					if existing_attendance:
						print(f"EXISTANT Date punch_time ===> {punch_time} ||| emp_code == {emp_code} log_type == {type_jour}")
					else:
                        # Create a new attendance document
						attendance_list = frappe.new_doc('Employee Checkin')
						attendance_list.employee = list.Matricule
						attendance_list.employee_name = first_name
						attendance_list.time = punch_time
						attendance_list.log_type = type_jour
						attendance_list.device_id = terminal_sn

                        # Save the document
						attendance_list.insert(ignore_permissions=True)
						frappe.db.commit()

						message = f"Employee Code: {emp_code}, Name: {first_name} , Devices {terminal_sn}, Punch Time: {punch_time}"
						print(message)  
                
                
		except requests.exceptions.Timeout:
			frappe.throw("La requête a expiré (timeout). Vérifiez la disponibilité du serveur.")
		except requests.exceptions.ConnectionError as e:
			frappe.throw(f"Erreur de connexion : {str(e)}")
		except Exception as e:
			frappe.throw(f"Une erreur inattendue s'est produite : {str(e)}")

