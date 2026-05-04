document.addEventListener("DOMContentLoaded", () => {
	const yearNode = document.querySelector("[data-year]");
	if (yearNode) {
		yearNode.textContent = String(new Date().getFullYear());
	}

	const leadForm = document.querySelector("#lead-form");
	if (leadForm) {
		const submitBtn = document.querySelector("#lead-submit");
		const successBox = document.querySelector("#lead-success");
		const errorBox = document.querySelector("#lead-error");

		leadForm.addEventListener("submit", async (event) => {
			event.preventDefault();
			if (submitBtn) submitBtn.disabled = true;
			if (successBox) successBox.style.display = "none";
			if (errorBox) errorBox.style.display = "none";

			try {
				const formData = new FormData(leadForm);
				const payload = Object.fromEntries(formData.entries());
				const csrfResp = await fetch("/api/method/securact_website.api.lead.get_csrf_token");
				const csrfData = await csrfResp.json();
				const csrfToken = csrfData?.message?.csrf_token || "";

				const resp = await fetch("/api/method/securact_website.api.lead.submit_lead", {
					method: "POST",
					headers: {
						"Content-Type": "application/json",
						"X-Frappe-CSRF-Token": csrfToken,
					},
					body: JSON.stringify(payload),
				});

				if (!resp.ok) {
					throw new Error("lead submission failed");
				}

				leadForm.reset();
				if (successBox) successBox.style.display = "block";
			} catch (err) {
				if (errorBox) errorBox.style.display = "block";
			} finally {
				if (submitBtn) submitBtn.disabled = false;
			}
		});
	}
});
