/**
 * Created by ari on 6/17/14.
 */

function loadList(){
    var partnerId = $('#partner').val();
   var url = makeURL('media','list');
    var tags = tagsChanged();
    if(tags.length>0) {
        url += '&filter:tagsLike=' + tags.join(',');
    }
     $('#listContent').html('');
    $.get(url, function(data){
        console.log(data);
        for(var i=0; i<data.totalCount; i++){
            var media = data.objects[i];
           var div = $('<div class="media-th" style="background-image:url(\''+media.thumbnailUrl+'\')"></div>');
            var a = $('<a href="'+media.dataUrl+'"></a>');
            var img = $('<img src="/static/play_button.png" />');
            a.append(img);
            div.append(a);
            $('#listContent').append(div);
        }
    });
}

window.onload = function(){
    var ut = $.get(makeURL('uploadToken','add'),function(data){
        $('#uploadTokenId').val(data['id']);
        loadList();
    });
};