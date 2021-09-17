function clickFunction() {
    var likes_checkBox = document.getElementById("likes_checkbox");
    var likes_text = document.getElementById("likes_ul");
    var subscribers_checkBox = document.getElementById("subscribers_checkbox");
    var subscribers_text = document.getElementById("subscribers_ul");
    var date_checkBox = document.getElementById("date_checkBox");
    var date_text = document.getElementById("date_ul");

    if (likes_checkBox.checked == true){
        likes_text.style.display = "block";
    } else {
        likes_text.style.display = "none";
    }

    if (subscribers_checkBox.checked == true){
        subscribers_text.style.display = "block";
    } else {
        subscribers_text.style.display = "none";
    }

    if (date_checkBox.checked == true){
        date_text.style.display = "block";
    } else {
        date_text.style.display = "none";
    }
}

function toggleFunction() {
    console.log('Click on button!')
    document.querySelector('.main').classList.toggle('active');
    document.querySelector('.main').classList.toggle('disactive');
    document.querySelector('.header').classList.toggle('active');
    document.querySelector('.header').classList.toggle('disactive');
    document.querySelector('svg').classList.toggle('active');
    document.querySelector('svg').classList.toggle('disactive');
}