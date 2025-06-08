// Copyright (c) 2024, Kossivi Amouzou and contributors
// For license information, please see license.txt

frappe.ui.form.on('Provision', {
	// refresh: function(frm) {

	// }
	scondary_calendar: function(frm){
		if(frm.doc.scondary_calendar == 1){
			frm.set_value('start_date', frm.doc.second_start);
			frm.set_value('end_date', frm.doc.second_end);
		}
		else{
			frm.set_value('start_date', frm.doc.first_start);
			frm.set_value('end_date', frm.doc.first_end);
		}
	}
});
