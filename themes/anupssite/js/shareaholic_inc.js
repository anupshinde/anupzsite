$(window).load(function(){
	(function() {
		var sb = document.createElement("script"); sb.type = "text/javascript";sb.async = true;
		sb.src = ("https:" == document.location.protocol ? "https://dtym7iokkjlif.cloudfront.net" : "http://cdn.shareaholic.com") + "/media/js/jquery.shareaholic-publishers-sb.min.js";
		var s = document.getElementsByTagName("script")[0]; s.parentNode.insertBefore(sb, s);
		})();
	
	prettyPrint();
})

var SHRSB_Globals = {"perfoption":"1"};
function addToSHRSB_Settings(k, v) {
	if(typeof(SHRSB_Settings)=='undefined' ||  SHRSB_Settings==null) {
		SHRSB_Settings={}
	}
	SHRSB_Settings[k] = v;
}
