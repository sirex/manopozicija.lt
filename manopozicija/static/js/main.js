var manopozicija = window.manopozicija || {};

(function (manopozicija, $) {
    manopozicija.save_user_vote = function (elem, vote) {
        var $votes = $(elem).siblings('.js-post-votes'),
            $me = $(elem), $he = $(elem).siblings('.js-post-thumb'),
            votes = parseInt($votes.text());

        if ($me.hasClass('active')) {
            $me.removeClass('active');
            $me.data('vote', 0);
            votes = votes - vote;
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
    };
}(manopozicija, jQuery));  //eslint-disable-line no-undef
