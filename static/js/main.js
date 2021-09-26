function clickFunction() {
    var likes_checkBox = document.getElementById("likes_checkbox");
    var likes_text = document.getElementById("likes_ul");
    var likes_input = document.getElementById("likes-input");
    var subscribers_checkBox = document.getElementById("subscribers_checkbox");
    var subscribers_text = document.getElementById("subscribers_ul");
    var subscribers_input = document.getElementById("subscribers-input");
    var date_checkBox = document.getElementById("date_checkBox");
    var date_text = document.getElementById("date_ul");
    var date_input = document.getElementById("date-input");

    if (likes_checkBox.checked == true){
        likes_text.style.display = "block";
        likes_input.setAttribute('required', '');
    } else {
        likes_text.style.display = "none";
        likes_input.removeAttribute('required');
    }

    if (subscribers_checkBox.checked == true){
        subscribers_text.style.display = "block";
        subscribers_input.setAttribute('required', '');
    } else {
        subscribers_text.style.display = "none";
        subscribers_input.removeAttribute('required');
    }

    if (date_checkBox.checked == true){
        date_text.style.display = "block";
        date_input.setAttribute('required', '');
    } else {
        date_text.style.display = "none";
        date_input.removeAttribute('required');
    }
}

function show_load() {
    document.querySelector('.main').classList.toggle('active');
    document.querySelector('.main').classList.toggle('disactive');
    document.querySelector('.header').classList.toggle('active');
    document.querySelector('.header').classList.toggle('disactive');
    document.querySelector('svg').classList.toggle('active');
    document.querySelector('svg').classList.toggle('disactive');
}

function hide_show_password() {
    var password_checkBox = document.getElementById("password-checkbox");
    var password_input = document.getElementById("password-input");

    if (password_checkBox.checked) {
        password_input.type = 'text';
    } else {
        password_input.type = 'password';
    }
}