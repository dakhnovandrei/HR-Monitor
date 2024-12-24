document.getElementById('register-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const role = document.getElementById('role').value;

    try {
        const response = await fetch('/api/v1/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ username, password, role }),
        });

        if (response.ok) {
            const data = await response.json();
            alert('Registration successful!');
            console.log(data);
            window.location.href = "index.html";
        } else {
            const error = await response.json();
            alert(`Error: ${error.detail}`);
        }
    } catch (error) {
        alert('An error occurred. Please try again.');
        console.error(error);
    }
});
