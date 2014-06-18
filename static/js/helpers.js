/**
 * Created by ari on 6/18/14.
 */
function makeURL(service,action){
    var base_url = 'http://www.kaltura.com/api_v3/?';
    var ks = $('#ks').val();
    return base_url+'format=1&ks='+ks+'&service='+service+'&action='+action;
}