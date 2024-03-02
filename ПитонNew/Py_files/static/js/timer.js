function urldecode() {
    return decodeURIComponent((window.location.href+'').replace(/\+/g, '%20'));
}
// Set the date we're counting down to
if (urldecode().includes("item")){
    var countDownDate = new Date("Jun 26, 2024 18:36:00").getTime();

    // Update the count down every 1 second
    var x = setInterval(function() {

      // Get today's date and time
      var now = new Date().getTime();

      // Find the distance between now and the count down date
      var distance = countDownDate - now;

      // Time calculations for days, hours, minutes and seconds
      var days = Math.floor(distance / (1000 * 60 * 60 * 24));
      var hours = Math.floor((distance % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
      var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
      var seconds = Math.floor((distance % (1000 * 60)) / 1000);


      document.getElementById("days_num").innerHTML = days;
      document.getElementById("hours_num").innerHTML = hours;
      document.getElementById("minutes_num").innerHTML = minutes;
      document.getElementById("seconds_num").innerHTML = seconds;

      // If the count down is over, write some text
      if (distance < 0)
      {
        clearInterval(x);
        document.getElementById("days_num").innerHTML = "00";
        document.getElementById("hours_num").innerHTML = "00";
        document.getElementById("minutes_num").innerHTML = "00";
        document.getElementById("seconds_num").innerHTML = "00";
      }
    }, 1000);
}