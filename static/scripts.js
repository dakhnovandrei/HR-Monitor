document.getElementById("login-form").addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(this);
    const data = Object.fromEntries(formData);

    try {
        const response = await fetch("/api/v1/login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(data)
        });

        if (response.ok) {
            const result = await response.json();

            if (result.role === "hr") {
                window.location.href = "/static/templates/vacancies.html";
            } else if (result.role === "team_lead_hr") {
                window.location.href = "/static/templates/dashboard.html";
            }
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (err) {
        console.error("Login failed:", err);
        alert("Login failed: Unable to connect to the server.");
    }
});
