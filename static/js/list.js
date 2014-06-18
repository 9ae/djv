/**
 * Created by ari on 6/17/14.
 */

function makeURL(service,action){
    var base_url = 'http://www.kaltura.com/api_v3/?';
    var ks = $('#ks').val();
    return base_url+'format=1&ks='+ks+'&service='+service+'&action='+action;
}

function loadList(){
    var partnerId = $('#partner').val();
    var url = makeURL('media','list');
    var tags = tagsChanged();
    url+='&filter:tagsLike='+tags.join(',');
     $('#listContent').html('');
    $.get(url, function(data){
        console.log(data);
        for(var i=0; i<data.totalCount; i++){
            var media = data.objects[i];
           var div = $('<div class="media-th"></div>');
            var a = $('<a href="'+media.dataUrl+'"></a>');
            var img = $('<img src="'+media.thumbnailUrl+'" />');
            a.append(img);
            div.append(a);
            $('#listContent').append(div);
          /*  var iframe = '<iframe src="http://www.kaltura.com/p/'+partnerId+'/sp/'+partnerId+'00/embedIframeJs' +
            '/uiconf_id/24675211/partner_id/'+partnerId+'?iframeembed=true&playerId=24675211&entry_id='+media.id+'"' +
            ' width="400" height="330" allowfullscreen webkitallowfullscreen mozAllowFullScreen frameborder="0"></iframe>';
            $('#listContent').append(iframe); */
        }

    });
}

function uploadFile(event){

}

window.onload = function(){
    addTag('#tag-warning');
    $('#upload').attr('action',makeURL('media','upload'));
    $('#first_tag').val();
};