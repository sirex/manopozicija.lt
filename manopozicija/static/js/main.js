var manopozicija = window.manopozicija || {};

(function (manopozicija, $) {
    
    // CSRF setup

    function getCookie(name) {
        var cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            var cookies = document.cookie.split(';');
            for (var i = 0; i < cookies.length; i++) {
                var cookie = jQuery.trim(cookies[i]);
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
        return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }

    var csrftoken = getCookie('csrftoken');

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrftoken);
            }
        }
    });

    // Voting

    function handle_vote_click(elem, vote) {
        var $votes = $(elem).siblings('.js-post-votes'),
            $me = $(elem), $he = $(elem).siblings('.js-post-thumb'),
            votes = parseInt($votes.text()),
            result = vote;

        if ($me.hasClass('active')) {
            $me.removeClass('active');
            $me.data('vote', 0);
            votes = votes - vote;
            result = 0;
        } else {
            $me.addClass('active');
            $me.data('vote', vote);
            if ($he.hasClass('active')) {
                votes = votes - parseInt($he.data('vote')) + vote;
                $he.removeClass('active');
                $he.data('vote', 0);
            } else {
                votes = votes + vote;
            }
        }

        $votes.text(votes);

        return result;
    }

    manopozicija.save_user_vote = function (elem, post_id, vote) {
        vote = handle_vote_click(elem, vote);
        $.post(manopozicija.urls['js:user-post-vote'](post_id), {'vote': vote});
    };

    manopozicija.save_curator_vote = function (elem, post_id, vote) {
        vote = handle_vote_click(elem, vote);
        $.post(manopozicija.urls['js:curator-post-vote'](post_id), {'vote': vote});
    };

}(manopozicija, jQuery));  //eslint-disable-line no-undef
