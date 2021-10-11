function clickFunction() {
    var likes_checkBox = document.getElementById("likes_checkbox");
    var likes_text = document.getElementById("likes_ul");
    var likes_input = document.getElementById("likes-input");
    var subscribers_checkBox = document.getElementById("subscribers_checkbox");
    var subscribers_text = document.getElementById("subscribers_ul");
    var subscribers_input = document.getElementById("subscribers-input");
    var date_checkBox = document.getElementById("date_checkBox");
    var date_input_checkBox = document.getElementById("date-input");
    var date_text = document.getElementById("date_ul");
    var date_input_1 = document.getElementById("date-input_1");
    var date_input_2 = document.getElementById("date-input_2");

    if (likes_checkBox.checked){
        likes_text.style.display = "block";
        likes_input.setAttribute('required', '');
    } else {
        likes_text.style.display = "none";
        likes_input.removeAttribute('required');
    }

    if (subscribers_checkBox.checked){
        subscribers_text.style.display = "block";
        subscribers_input.setAttribute('required', '');
    } else {
        subscribers_text.style.display = "none";
        subscribers_input.removeAttribute('required');
    }

    if (date_checkBox.checked){
        date_text.style.display = "block";
        date_input_1.setAttribute('required', '');
        date_input_2.setAttribute('required', '');
        date_input_checkBox.value = 'YES';
    } else {
        date_text.style.display = "none";
        date_input_1.removeAttribute('required');
        date_input_2.removeAttribute('required');
        date_input_checkBox.value = 'NO';
    }
}

function show_load() {
    document.querySelector('.main_main').classList.toggle('active');
    document.querySelector('.main_main').classList.toggle('disactive');
    document.querySelector('.main_load').classList.toggle('active');
    document.querySelector('.main_load').classList.toggle('disactive');
    document.querySelector('.header').classList.toggle('active');
    document.querySelector('.header').classList.toggle('disactive');
    document.querySelector('svg').classList.toggle('active');
    document.querySelector('svg').classList.toggle('disactive');
}

function check_invalid_str() {
    var likes = null;
    var subscribers = null;
    var date = null;
    var limit_input = document.getElementById("limit-input");
    var likes_input = document.getElementById("likes-input");
    var likes_checkBox = document.getElementById("likes_checkbox");
    var subscribers_input = document.getElementById("subscribers-input");
    var subscribers_checkBox = document.getElementById("subscribers_checkbox");
    var keyword_input = document.getElementById("key_word-input");
    var date_input_1 = document.getElementById("date-input_1");
    var date_input_2 = document.getElementById("date-input_2");
    var date_checkBox = document.getElementById("date_checkBox");

    if (likes_checkBox.checked) {
        if (likes_input.value != '') {
            likes = true;
        } else {
            likes = false;
        }
    }

    if (subscribers_checkBox.checked) {
        if (subscribers_input.value != '') {
            subscribers = true;
        } else {
            subscribers = false;
        }
    }

    if (date_checkBox.checked) {
        if (date_input_1.value != '' && date_input_2.value != '') {
            date = true;
        } else {
            date = false;
        }
    }

    if (limit_input.value != '' && (likes == null || likes) && (subscribers == null || subscribers) && keyword_input.value != '' && (date == null || date)) {
        show_load();
    }
}

function hide_show_password() {
    var password_checkBox = document.getElementById("password-checkbox");
    if (password_checkBox != null) {
        password_checkBox = password_checkBox.checked
        var password_input = document.getElementById("password-input");

        if (password_checkBox == true) {
            password_input.type = 'text';
        } if (password_checkBox == false) {
            password_input.type = 'password';
        }

    } else {
        var password_checkBox_1 = document.getElementById("password-checkbox-1").checked;
        var password_checkBox_2 = document.getElementById("password-checkbox-2").checked;
        var password_checkBox_3 = document.getElementById("password-checkbox-3").checked;
        var old_password_input = document.getElementById("old_password-input");
        var new_password_input = document.getElementById("new_password-input");
        var repeat_new_password_input = document.getElementById("repeat_new_password-input");

        if (password_checkBox_1 == true) {
            old_password_input.type = 'text';
        } if (password_checkBox_1 == false) {
            old_password_input.type = 'password';
        }

        if (password_checkBox_2 == true) {
            new_password_input.type = 'text';
        } if (password_checkBox_2 == false) {
            new_password_input.type = 'password';
        }

        if (password_checkBox_3 == true) {
            repeat_new_password_input.type = 'text';
        } if (password_checkBox_3 == false) {
            repeat_new_password_input.type = 'password';
        }
    }
}