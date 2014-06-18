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
    if(tags.length>0) {
        url += '&filter:tagsLike=' + tags.join(',');
    }
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
        }
    });
}

function uploadFile(event){
    var file = $('#fileData').val();
    var token = $('#uploadTokenId').val();
    if(token==""){
        return;
    }
    var url = makeURL('uploadToken','upload');
    var obj = {'fileData': file, 'uploadTokenId': token};
    $.post(url,obj, function(data){
        console.log('upload to token');
        var uploadResults = data;
        if(uploadResults['fileName']!=undefined){
            $.post(makeURL('media','add'), {'entry:mediaType':2},function(data){
                console.log('create media');
                var addMediaResults = data;
                var linkBody = {'entryId':addMediaResults.id,
                    'resource:token': token,
                    'resource:objectType':'KalturaUploadedFileTokenResource'};
                $.post(makeURL('media','addContent'),linkBody).done(function(){
                    console.log('upload complete');
                });
            });
        }
    });
}


window.onload = function(){
    addTag('#tag-warning');
    $('#first_tag').val();

    var ut = $.get(makeURL('uploadToken','add'),function(data){
        $('#uploadTokenId').val(data['id']);
        $('#do_upload').click(uploadFile);
    });
};