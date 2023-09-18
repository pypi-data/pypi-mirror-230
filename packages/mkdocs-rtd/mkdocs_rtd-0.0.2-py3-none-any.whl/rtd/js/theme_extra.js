/*
 * Assign 'docutils' class to tables so styling and
 * JavaScript behavior is applied.
 *
 * https://github.com/mkdocs/mkdocs/issues/2028
 */
(function($) {
    $('div.wy-social').css(
        'left',
        parseInt($("nav.wy-nav-side").outerWidth() + $("div.wy-nav-content").outerWidth()) + 'px'
    );
    $('div.wy-menu.wy-menu-vertical').css(
        'margin-top',
        $('div.wy-side-nav-search').outerHeight() + 16 + 'px'
    );

    $('div.rst-content table').addClass('docutils');
    $('div.wy-side-scroll li.toctree-l1').on('click', '>a:has(button)', function(e) {
        let $button = $(this).children('button');
        if ($button.length > 0) {
            $button.click();
        }
    });
    $('.rst-content a[href^="http"]').attr('target', '_blank');

    const $current = $('li.current,a.current');
    if ($current.length > 0) {
        $current[0].scrollIntoView();
    }
})(jQuery);
