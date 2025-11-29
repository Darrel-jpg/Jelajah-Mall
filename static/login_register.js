const container = document.querySelector('.container')
const registerBtn = document.querySelector('.register-btn')
const loginBtn = document.querySelector('.login-btn')
const toggleIcon = document.querySelectorAll('.toggle-password')

registerBtn.addEventListener('click', () => {
    container.classList.add('active')
})

loginBtn.addEventListener('click', () => {
    container.classList.remove('active')
})

toggleIcon.forEach(icon => {
    icon.addEventListener('click', () => {
        const targetId = icon.getAttribute('data-target');
        const input = document.getElementById(targetId);
        
        if (input.type === 'password') {
            input.type = 'text';
            icon.classList.remove('fa-eye-slash');
            icon.classList.add('fa-eye');
        } else {
            input.type = 'password';
            icon.classList.remove('fa-eye');
            icon.classList.add('fa-eye-slash');
        }
    });
});

registerBtn.addEventListener('click', () => {
    container.classList.add('active');
    if (flashMessages) flashMessages.innerHTML = '';  // Hapus pesan flash register
});

loginBtn.addEventListener('click', () => {
    container.classList.remove('active');
    if (flashMessages) flashMessages.innerHTML = '';  // Hapus pesan flash login
});

forgotForm.addEventListener('submit', function(e) {
    const emailInput = forgotForm.querySelector("input[name='email']");
    const email = emailInput.value.trim();

    if (!email) {
        e.preventDefault();
        alert('Please enter your email');
    } else if (!validateEmail(email)) {
        e.preventDefault();
        alert('Please enter a valid email address');
    }
});

function validateEmail(email) {
    // Simple email regex
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email.toLowerCase());
}