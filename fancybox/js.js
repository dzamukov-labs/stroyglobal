		$(document).ready(function() {
			$("a[rel=example_group]").fancybox({
				'transitionIn'		: 'elastic',
				'transitionOut'		: 'elastic',
				'titlePosition' 	: 'over',
				'titleFormat'		: function(title, currentArray, currentIndex, currentOpts) {
					return '<span id="fancybox-title-over">Картинка № ' + (currentIndex + 1) + ' из ' + currentArray.length + ' &nbsp;&nbsp;—&nbsp; ' + (title.length ? ' &nbsp; ' + title : '') + '</span>';
				}
			});
		});