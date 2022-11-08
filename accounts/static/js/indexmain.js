// Menu-toggle button

      $(document).ready(function() {
            
        $(".menu-icon").on("click", function() {
            console.log("hello")
              $("nav ul").toggleClass("showing");
        });
  });

  // Scrolling Effect

  $(window).on("scroll", function() {
        if($(window).scrollTop()) {
              $('nav').addClass('black');
        }

        else {
              $('nav').removeClass('black');
        }
  })
