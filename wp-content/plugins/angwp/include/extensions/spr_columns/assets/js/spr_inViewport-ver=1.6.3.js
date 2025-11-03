// Return the visible amount of px
// of any element currently in viewport.
// https://stackoverflow.com/a/27462500/3481803
// http://jsfiddle.net/RokoCB/tw6g2oeu/7/
/**
 * $(".example").inViewport(function(px){ if(px) $(this).addClass("class"); }, {padding:0});
 *
*/
;(function($, win) {
  $.fn.inViewport = function(cb, options) {
	  
	  // Defaults
	  var settings = $.extend({
		 padding: 0 // Add delay
	  }, options );
	  
     return this.each(function(i,el){
		//var func = function(px){if(px) $(this).addClass(settings.class+' '+$(this).data('animation'));};
       function visPx(){
         var H = $(this).height(),
             r = el.getBoundingClientRect(), t=r.top+settings.padding, b=r.bottom+settings.padding;
         return cb.call(el, Math.max(0, t>0? H-t : (b<H?b:H)));  
       } visPx();
       $(win).on("resize scroll", visPx);
     });
  };
}(jQuery, window));