import frappe
from frappe import _
from frappe.sessions import get_csrf_token as _get_csrf_token

ALLOWED_KEYS = frozenset(
	(
		"full_name",
		"mobile",
		"company_name",
		"city",
		"service_interest",
		"requirement",
		"source",
	)
)


@frappe.whitelist(allow_guest=True, methods=["GET"])
def get_csrf_token():
	return {"csrf_token": _get_csrf_token()}


@frappe.whitelist(allow_guest=True, methods=["POST"])
def submit_lead():
	data = frappe.request.get_json(silent=True)
	if not isinstance(data, dict):
		data = {k: v for k, v in frappe.form_dict.items() if k not in ("cmd", "data")}

	if not isinstance(data, dict):
		frappe.throw(_("Invalid request"), frappe.ValidationError)

	payload = {k: data.get(k) for k in ALLOWED_KEYS if k in data}

	if not (payload.get("full_name") or "").strip():
		frappe.throw(_("Full name is required"), frappe.ValidationError)
	if not (payload.get("mobile") or "").strip():
		frappe.throw(_("Mobile is required"), frappe.ValidationError)
	if not (payload.get("requirement") or "").strip():
		frappe.throw(_("Requirement is required"), frappe.ValidationError)

	lead_name = _create_local_lead(payload)
	return {"ok": True, "lead_name": lead_name}


def _create_local_lead(payload: dict) -> str:
	service_interest = (payload.get("service_interest") or "").strip()
	requirement = (payload.get("requirement") or "").strip()
	source = (payload.get("source") or "").strip()
	company_name = (payload.get("company_name") or "").strip()
	city = (payload.get("city") or "").strip()
	req_title = requirement[:120] if requirement else "Website enquiry"

	doc = frappe.get_doc(
		{
			"doctype": "Lead",
			"lead_name": (payload.get("full_name") or "").strip(),
			"company_name": company_name or None,
			"mobile_no": (payload.get("mobile") or "").strip(),
			"city": city or None,
			"title": req_title,
		}
	)
	doc.insert(ignore_permissions=True)

	comment_lines = [
		f"Service Interest: {service_interest}" if service_interest else "",
		f"Source: {source}" if source else "",
		f"Requirement: {requirement}" if requirement else "",
	]
	comment_text = "\n".join([x for x in comment_lines if x]).strip()
	if comment_text:
		doc.add_comment("Comment", comment_text)

	frappe.db.commit()
	return doc.name
