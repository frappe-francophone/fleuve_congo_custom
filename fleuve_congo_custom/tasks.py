import frappe
import json
import requests
from datetime import datetime
import pytz
from frappe.utils import now
import string
import random

def cron():
    url_base = "http://10.184.104.230:8080/iclock/api/transactions/"
    token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzMyNjE5ODU5LCJpYXQiOjE3MzI1MzM0NTksImp0aSI6IjMwNzk3NmY0MTQwMzRjYTk4Nzg1MjE4Y2Y2NWFhNWQ0IiwidXNlcl9pZCI6MX0.msx3MwlnejASvx-t8hEzH6le3jOMNcbMUQn2ZSFwIeg"
    page = 1
    limit = 1000
    all_data = []  # This will store the combined data
  
    # Get today's date
    date_time_string = frappe.utils.now()
  
    # Use correct date format
    #datejour_end = '2024-11-30'

    datejour_start = frappe.utils.add_days(date_time_string, -35)
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

        datejour_start = frappe.utils.add_days(date_time_string, -35)
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

                        every_minute(list.Matricule)

                        message = f"Employee Code: {emp_code}, Name: {first_name} , Devices {terminal_sn}, Punch Time: {punch_time}"
                        print(message)  
                
                
        except requests.exceptions.Timeout:
            frappe.throw("La requête a expiré (timeout). Vérifiez la disponibilité du serveur.")
        except requests.exceptions.ConnectionError as e:
            frappe.throw(f"Erreur de connexion : {str(e)}")
        except Exception as e:
            frappe.throw(f"Une erreur inattendue s'est produite : {str(e)}")

def every_minute(name):
    current_time = now()
    frappe.logger().info(f"[every_minute] Tâche exécutée à {current_time}")
    
    # Générer une chaîne aléatoire de 20 caractères
    letters = string.ascii_letters
    random_text = "".join(random.choice(letters) for i in range(20))
    
    # Concaténation simple
    note_title = f"{name} {random_text}"
    
    # Création du document Note
    new_note = frappe.get_doc({
        "doctype": "Note",
        "title": note_title
    })
    new_note.insert()
    frappe.db.commit()
    
    print(f"[every_minute] Tâche exécutée à {current_time}")