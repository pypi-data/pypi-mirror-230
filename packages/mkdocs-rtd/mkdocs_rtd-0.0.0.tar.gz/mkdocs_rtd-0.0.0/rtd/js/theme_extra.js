/*
 * Assign 'docutils' class to tables so styling and
 * JavaScript behavior is applied.
 *
 * https://github.com/mkdocs/mkdocs/issues/2028
 */
(function($) {
    $('div.rst-content table').addClass('docutils');
    $('div.wy-side-scroll li.toctree-l1').on('click', '>a:has(button)', function(e) {
        let $button = $(this).children('button');
        if ($button.length > 0) {
            $button.click();
        }
    });

    const $current = $('li.current,a.current');
    if ($current.length > 0) {
        $current[0].scrollIntoView();
    }
})(jQuery);
